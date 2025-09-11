import logging
import time
from typing import Iterator
import copy

import numpy as np
from torch.utils.data import Sampler, Subset
import torch.distributed as dist

from ..dataset import MetadataConcatDataset, PerturbationDataset
from ..utils.data_utils import H5MetadataCache

logger = logging.getLogger(__name__)


class PerturbationBatchSampler(Sampler):
    """
    Samples batches ensuring that cells in each batch share the same
    (cell_type, perturbation) combination, using only H5 codes.

    Instead of grouping by cell type and perturbation names, this sampler
    groups based on integer codes stored in the H5 file (e.g. `cell_type_codes`
    and `pert_codes` in the H5MetadataCache). This avoids repeated string operations.

    Supports distributed training.
    """

    def __init__(
        self,
        dataset: "MetadataConcatDataset",
        batch_size: int,
        drop_last: bool = False,
        cell_sentence_len: int = 512,
        test: bool = False,
        use_batch: bool = False,
        seed: int = 0,
        epoch: int = 0,
    ):
        logger.info(
            "Creating perturbation batch sampler with metadata caching (using codes)..."
        )
        start_time = time.time()

        # If the provided dataset has a `.data_source` attribute, use that.
        self.dataset = (
            dataset.data_source if hasattr(dataset, "data_source") else dataset
        )
        self.batch_size = batch_size
        self.test = test
        self.use_batch = use_batch
        self.seed = seed
        self.epoch = epoch

        if self.test and self.batch_size != 1:
            logger.warning(
                "Batch size should be 1 for test mode. Setting batch size to 1."
            )
            self.batch_size = 1

        self.cell_sentence_len = cell_sentence_len
        self.drop_last = drop_last

        # Setup distributed settings if distributed mode is enabled.
        self.distributed = False
        self.num_replicas = 1
        self.rank = 0

        if dist.is_available() and dist.is_initialized():
            self.distributed = True
            self.num_replicas = dist.get_world_size()
            self.rank = dist.get_rank()
            logger.info(
                f"Distributed mode enabled. World size: {self.num_replicas}, rank: {self.rank}."
            )

        # Create caches for all unique H5 files.
        self.metadata_caches = {}
        for subset in self.dataset.datasets:
            base_dataset: PerturbationDataset = subset.dataset
            self.metadata_caches[base_dataset.h5_path] = base_dataset.metadata_cache

        # Create batches using the code-based grouping.
        self.sentences = self._create_sentences()
        sentence_lens = [len(sentence) for sentence in self.sentences]
        avg_num = np.mean(sentence_lens)
        std_num = np.std(sentence_lens)
        tot_num = np.sum(sentence_lens)
        logger.info(
            f"Total # cells {tot_num}. Cell set size mean / std before resampling: {avg_num:.2f} / {std_num:.2f}."
        )

        # combine sentences into batches that are flattened
        logger.info(
            f"Creating meta-batches with cell_sentence_len={cell_sentence_len}..."
        )
        self.batches = self._create_batches()
        self.tot_num = tot_num

        end_time = time.time()
        logger.info(
            f"Sampler created with {len(self.batches)} batches in {end_time - start_time:.2f} seconds."
        )

    def _create_batches(self) -> list[list[int]]:
        """
        Combines existing batches into meta-batches of size batch_size * cell_sentence_len,
        sampling with replacement if needed to reach cell_sentence_len.

        IF distributed, each rank will process a subset of the sentences.
        """

        if self.distributed:
            rank_sentences = self._get_rank_sentences()

        else:
            rank_sentences = self.sentences

        all_batches = []
        current_batch = []

        num_full = 0
        num_partial = 0
        for sentence in rank_sentences:
            # If batch is smaller than cell_sentence_len, sample with replacement
            if len(sentence) < self.cell_sentence_len and not self.test:
                # during inference, don't sample by replacement
                new_sentence = np.random.choice(
                    sentence, size=self.cell_sentence_len, replace=True
                ).tolist()
                num_partial += 1
            else:
                new_sentence = copy.deepcopy(sentence)
                assert len(new_sentence) == self.cell_sentence_len or self.test
                num_full += 1

            sentence_len = len(new_sentence) if self.test else self.cell_sentence_len

            if len(current_batch) + len(new_sentence) <= self.batch_size * sentence_len:
                current_batch.extend(new_sentence)
            else:
                if current_batch:  # Add the completed meta-batch
                    all_batches.append(current_batch)
                current_batch = new_sentence

        if self.distributed:
            logger.info(
                f"Rank {self.rank}: Of {len(rank_sentences)} sentences, {num_full} were full and {num_partial} were partial."
            )
        else:
            logger.info(
                f"Of all batches, {num_full} were full and {num_partial} were partial."
            )

        # Add the last meta-batch if it exists
        if current_batch and not self.drop_last:
            all_batches.append(current_batch)

        return all_batches

    def _get_rank_sentences(self) -> list[list[int]]:
        """
        Get the subset of sentences that this rank should process.
        Sentences are shuffled using epoch-based seed, then distributed across ranks.
        """
        # Shuffle sentences using epoch-based seed for consistent ordering across ranks
        shuffled_sentences = self.sentences.copy()
        np.random.RandomState(self.seed + self.epoch).shuffle(shuffled_sentences)

        # Calculate sentence distribution across processes
        total_sentences = len(shuffled_sentences)
        base_sentences = total_sentences // self.num_replicas
        remainder = total_sentences % self.num_replicas

        # Calculate number of sentences for this specific rank
        if self.rank < remainder:
            num_sentences_for_rank = base_sentences + 1
        else:
            num_sentences_for_rank = base_sentences

        # Calculate starting sentence index for this rank
        start_sentence_idx = self.rank * base_sentences + min(self.rank, remainder)
        end_sentence_idx = start_sentence_idx + num_sentences_for_rank

        rank_sentences = shuffled_sentences[start_sentence_idx:end_sentence_idx]

        logger.info(
            f"Rank {self.rank}: Processing {len(rank_sentences)} sentences "
            f"(indices {start_sentence_idx} to {end_sentence_idx - 1} of {total_sentences})"
        )

        return rank_sentences

    def _process_subset(self, global_offset: int, subset: Subset) -> list[list[int]]:
        """
        Process a single subset to create batches based on H5 codes.

        For each subset, the method:
          - Retrieves the subset indices.
          - Extracts the corresponding cell type and perturbation codes from the cache.
          - Constructs a structured array with two fields (cell, pert) so that unique
            (cell_type, perturbation) pairs can be identified using np.unique.
          - For each unique pair, shuffles the indices and splits them into batches.
        """
        base_dataset = subset.dataset
        indices = np.array(subset.indices)
        cache: H5MetadataCache = self.metadata_caches[base_dataset.h5_path]

        # Use codes directly rather than names.
        cell_codes = cache.cell_type_codes[indices]
        pert_codes = cache.pert_codes[indices]

        if "use_batch" in self.__dict__ and self.use_batch:
            # If using batch, we need to use the batch codes instead of cell type codes.
            batch_codes = cache.batch_codes[indices]
            # Also get batch codes if grouping by batch is desired.
            batch_codes = cache.batch_codes[indices]
            dt = np.dtype(
                [
                    ("batch", batch_codes.dtype),
                    ("cell", cell_codes.dtype),
                    ("pert", pert_codes.dtype),
                ]
            )
            groups = np.empty(len(indices), dtype=dt)
            groups["batch"] = batch_codes
            groups["cell"] = cell_codes
            groups["pert"] = pert_codes
        else:
            dt = np.dtype([("cell", cell_codes.dtype), ("pert", pert_codes.dtype)])
            groups = np.empty(len(indices), dtype=dt)
            groups["cell"] = cell_codes
            groups["pert"] = pert_codes

        # Create global indices (assuming that indices in each subset refer to a global concatenation).
        global_indices = np.arange(global_offset, global_offset + len(indices))

        subset_batches = []
        # Group by unique (cell, pert) pairs.
        for group_key in np.unique(groups):
            mask = groups == group_key
            group_indices = global_indices[mask]
            np.random.shuffle(group_indices)

            # Split the group indices into batches.
            for i in range(0, len(group_indices), self.cell_sentence_len):
                sentence = group_indices[i : i + self.cell_sentence_len].tolist()
                if len(sentence) < self.cell_sentence_len and self.drop_last:
                    continue
                subset_batches.append(sentence)

        return subset_batches

    def _create_sentences(self) -> list[list[int]]:
        """
        Process each subset sequentially (across all datasets) and combine the batches.
        """
        global_offset = 0
        all_batches = []
        for subset in self.dataset.datasets:
            subset_batches = self._process_subset(global_offset, subset)
            all_batches.extend(subset_batches)
            global_offset += len(subset)

        np.random.shuffle(all_batches)
        return all_batches

    def __iter__(self) -> Iterator[list[int]]:
        # Shuffle the order of batches each time we iterate in non-distributed mode.
        if not self.distributed:
            self.batches = self._create_batches()
        yield from self.batches

    def __len__(self) -> int:
        return len(self.batches)

    def set_epoch(self, epoch: int) -> None:
        """
        Set the epoch for this sampler.

        This ensures all replicas use a different random ordering for each epoch.

        Args:
            epoch: Epoch number
        """
        self.epoch = epoch
        # Recreate batches for new epoch (sentences remain the same)
        self.batches = self._create_batches()
