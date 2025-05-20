import enum
from typing import Dict, List, Tuple
from MemoryOperation import MemoryOperation
from MemoryOperation import MemoryOperationType
from HashTable import TwoLevelHashTable, TwoLevelHashTableList
import numpy as np


class MemoryStrategy(enum.Enum):
    FIRST_FIT = 0
    BEST_FIT = 1
    WORST_FIT = 2


class Block:
    def __init__(self, start: int, size: int):
        self.start = start
        self.size = size


class MemoryManager:

    def __init__(self, strategy: MemoryStrategy) -> None:
        self.strategy = strategy
        self.total_memory = 1024 # Can be modified
        self.total_memory_bits = int(np.ceil(np.log2(self.total_memory)))
        self.free_sizes_hash_table = TwoLevelHashTableList(self.total_memory_bits)
        self.free_addresses_hash_table = TwoLevelHashTable(self.total_memory_bits)
        self.allocated_addresses_hash_table = TwoLevelHashTable(self.total_memory_bits)
        self.free_sizes_hash_table.insert(self.total_memory, 0) # A list with one element: the start address of the free block.
        self.free_addresses_hash_table.insert(0, self.total_memory) # The whole memory block starts at address 0 and is free.
        self.allocated_addresses_hash_table.insert(0, 0)  # A placeholder block

    def _find_block(self, size: int) -> Tuple[int, int]:
        if self.strategy == MemoryStrategy.FIRST_FIT:
            # Get the bitmap and the buckets from the hash table
            buckets = self.free_addresses_hash_table.buckets
            bitmap = self.free_addresses_hash_table.bitmap

            # Find non-empty bucket
            for index, bit in enumerate(bitmap):
                if bit == 1:
                    bucket = buckets[index]
                    # Get all items from the occupied bucket
                    second_level_items = bucket.items()
                    for start_address, block_size in second_level_items:
                        if block_size >= size:
                            # Return the first fit
                            return start_address, block_size

        elif self.strategy == MemoryStrategy.BEST_FIT:
            if self.free_sizes_hash_table.query(size) is not None:
                block_size = size
                start_address_list = self.free_sizes_hash_table.query(size)
            else: block_size, start_address_list = self.free_sizes_hash_table.next_larger_key(size)

            if isinstance(start_address_list, list):
                return start_address_list[0], block_size
            else:
                return start_address_list, block_size

        elif self.strategy == MemoryStrategy.WORST_FIT:
            block_size, start_address_list = self.free_sizes_hash_table.max_key()
            if isinstance(start_address_list, list):
                return start_address_list[0], block_size
            else:
                return start_address_list, block_size
        return -1, -1

    def _allocate(self, start: int, size: int) -> None:
        # Allocate a block of memory and update the data structures
        end = start + size
        previous_free_size = self.free_addresses_hash_table.query(start)
        if previous_free_size is None:
            previous_free_start, previous_free_size = self.free_addresses_hash_table.next_smaller_key(start)
        else: previous_free_start = start
        previous_free_end = previous_free_start + previous_free_size
        self.allocated_addresses_hash_table.insert(start, size)
        a = True
        if start > previous_free_start:
            leading_size = start - previous_free_start
            self.free_addresses_hash_table.insert(previous_free_start, leading_size)
            self.free_sizes_hash_table.insert(leading_size, previous_free_start)
            a = False
        if previous_free_end > end:
            trailing_size = previous_free_end - end
            self.free_addresses_hash_table.insert(end, trailing_size)
            self.free_sizes_hash_table.insert(trailing_size, end)
        if a:
            if previous_free_start == 0:
                self.free_addresses_hash_table.insert(0, 0)
            else: self.free_addresses_hash_table.delete(previous_free_start)
        self.free_sizes_hash_table.delete(previous_free_size, previous_free_start)
        self._merge_allocated_blocks(start, size)

    def _deallocate(self, start: int, size: int) -> bool:
        # Find the allocated block that contains the start address
        allocated_size = self.allocated_addresses_hash_table.query(start)
        if allocated_size is None:
            allocated_start, allocated_size = self.allocated_addresses_hash_table.next_smaller_key(start)
            if allocated_start is None:
                return False
        else: allocated_start = start
        allocated_end = allocated_start + allocated_size
        if allocated_start <= start < allocated_end:
            dealloc_end = start + size
            if dealloc_end > allocated_end:
                # Handle the error - requested deallocation exceeds the allocated block
                return False

            a = True
            if start > allocated_start:
                leading_size = start - allocated_start
                self.allocated_addresses_hash_table.insert(allocated_start, leading_size)
                a = False
            if allocated_end > dealloc_end:
                trailing_size = allocated_end - dealloc_end
                self.allocated_addresses_hash_table.insert(dealloc_end, trailing_size)
            if a:
                if allocated_start == 0:
                    self.allocated_addresses_hash_table.insert(0, 0)
                else: self.allocated_addresses_hash_table.delete(allocated_start)
            self.free_addresses_hash_table.insert(start, size)
            self.free_sizes_hash_table.insert(size, start)
            self._merge_free_blocks(start, size)
            return True
        return False

    def _merge_free_blocks(self, start: int, size: int) -> None:
        end = start + size
        previous_free_start, previous_free_size = self.free_addresses_hash_table.next_smaller_key(start)
        previous_free_end = previous_free_start + previous_free_size
        next_free_start, next_free_size = self.free_addresses_hash_table.next_larger_key(start)
        next_free_end = next_free_start + next_free_size
        if previous_free_end == start:
            if end == next_free_start:
                combined_size = next_free_end - previous_free_start
                if previous_free_start == 0:
                    self.free_addresses_hash_table.insert(0, 0)
                else:
                    self.free_addresses_hash_table.delete(previous_free_start)
                self.free_sizes_hash_table.delete(previous_free_size, previous_free_start)
                self.free_addresses_hash_table.delete(next_free_start)
                self.free_sizes_hash_table.delete(next_free_size, next_free_start)
                self.free_addresses_hash_table.delete(start)
                self.free_sizes_hash_table.delete(size, start)
                self.free_addresses_hash_table.insert(previous_free_start, combined_size)
                self.free_sizes_hash_table.insert(combined_size, previous_free_start)
            else:
                combined_size = end - previous_free_start
                if previous_free_start == 0:
                    self.free_addresses_hash_table.insert(0, 0)
                else:
                    self.free_addresses_hash_table.delete(previous_free_start)
                self.free_sizes_hash_table.delete(previous_free_size, previous_free_start)
                self.free_addresses_hash_table.delete(start)
                self.free_sizes_hash_table.delete(size, start)
                self.free_addresses_hash_table.insert(previous_free_start, combined_size)
                self.free_sizes_hash_table.insert(combined_size, previous_free_start)
        elif end == next_free_start:
            combined_size = next_free_end - start
            self.free_addresses_hash_table.delete(next_free_start)
            self.free_sizes_hash_table.delete(next_free_size, next_free_start)
            if start == 0:
                self.free_addresses_hash_table.insert(0, 0)
            else:
                self.free_addresses_hash_table.delete(start)
            self.free_sizes_hash_table.delete(size, start)
            self.free_addresses_hash_table.insert(start, combined_size)
            self.free_sizes_hash_table.insert(combined_size, start)


    def _merge_allocated_blocks(self, start: int, size: int) -> None:
        end = start + size
        previous_allocated_start, previous_allocated_size = self.allocated_addresses_hash_table.next_smaller_key(start)
        previous_allocated_end = previous_allocated_start + previous_allocated_size
        next_allocated_start, next_allocated_size = self.allocated_addresses_hash_table.next_larger_key(start)
        next_allocated_end = next_allocated_start + next_allocated_size
        if previous_allocated_end == start:
            if end == next_allocated_start:
                combined_size = next_allocated_end - previous_allocated_start
                if previous_allocated_start == 0:
                    self.allocated_addresses_hash_table.insert(0, 0)
                else: self.allocated_addresses_hash_table.delete(previous_allocated_start)
                self.allocated_addresses_hash_table.delete(next_allocated_start)
                self.allocated_addresses_hash_table.delete(start)
                self.allocated_addresses_hash_table.insert(previous_allocated_start, combined_size)
            else:
                combined_size = end - previous_allocated_start
                if previous_allocated_start == 0:
                    self.allocated_addresses_hash_table.insert(0, 0)
                else: self.allocated_addresses_hash_table.delete(previous_allocated_start)
                self.allocated_addresses_hash_table.delete(start)
                self.allocated_addresses_hash_table.insert(previous_allocated_start, combined_size)
        elif end == next_allocated_start:
            combined_size = next_allocated_end - start
            self.allocated_addresses_hash_table.delete(next_allocated_start)
            if start == 0:
                self.allocated_addresses_hash_table.insert(0, 0)
            else: self.allocated_addresses_hash_table.delete(start)
            self.allocated_addresses_hash_table.insert(start, combined_size)

    def request(self, op: MemoryOperation) -> int:
        size = op.size
        if op.addr is not None:
            # If address is provided, check if it's available
            if not self.is_valid_op(op):
                return -1
            self._allocate(op.addr, size)
            #print(self.free_addresses_hash_table.items())
            #print(self.free_sizes_hash_table.items())
            #print(self.allocated_addresses_hash_table.items())
            return op.addr
        else:
            # Find a block based on the strategy
            if not self.is_valid_op(op):
                return -1
            start, _ = self._find_block(size)
            if start != -1:
                self._allocate(start, size)
                #print(self.free_addresses_hash_table.items())
                #print(self.free_sizes_hash_table.items())
                #print(self.allocated_addresses_hash_table.items())
                return start
            return -1

    def release(self, op: MemoryOperation) -> bool:
        if not self.is_valid_op(op):
            return False

        boolean = self._deallocate(op.addr, op.size)
        #print(self.free_addresses_hash_table.items())
        #print(self.free_sizes_hash_table.items())
        #print(self.allocated_addresses_hash_table.items())
        return boolean

    def is_valid_op(self, op: MemoryOperation) -> bool:
        if op.op_type == MemoryOperationType.REQUEST:
            # If a specific address is requested, check if it falls within any of the free blocks
            if op.size > self.total_memory or op.size < 0:
                return False
            if op.addr is not None:
                if op.addr > self.total_memory or op.addr < 0:
                    return False
                previous_free_size = self.free_addresses_hash_table.query(op.addr)
                if previous_free_size is None:
                    previous_free_start, previous_free_size = self.free_addresses_hash_table.next_smaller_key(op.addr)
                else: previous_free_start = op.addr
                previous_free_end = previous_free_start + previous_free_size
                if previous_free_start <= op.addr < previous_free_end:
                    remaining_size = previous_free_end - op.addr
                    if remaining_size >= op.size:
                        return True
                # If no free block satisfies the request, return False
                return False
            # If no specific address is requested, check if there is any free block that is large enough
            else:
                max_free_size, _ = self.free_sizes_hash_table.max_key()
                if max_free_size >= op.size:
                    return True
        elif op.op_type == MemoryOperationType.RELEASE:
            if op.size > self.total_memory or op.size < 0 or op.addr > self.total_memory or op.addr < 0:
                return False
            # Whether the release is valid will be decided later in _deallocate
            return True

        # If the operation type is neither REQUEST nor RELEASE, return False
        return False

    def get_bucket_sizes_allocated_addresses(self) -> List[int]:
        bucket_sizes = []
        for bucket in self.allocated_addresses_hash_table.buckets:
            if bucket is not None:
                size = len(bucket.items())
            else:
                size = 0
            bucket_sizes.append(size)
        return bucket_sizes

    def get_bucket_sizes_free_addresses(self) -> List[int]:
        bucket_sizes = []
        for bucket in self.free_addresses_hash_table.buckets:
            if bucket is not None:
                size = len(bucket.items())
            else:
                size = 0
            bucket_sizes.append(size)

        return bucket_sizes

    def get_bucket_sizes_free_sizes(self) -> List[int]:
        bucket_sizes = []
        for bucket in self.free_sizes_hash_table.buckets:
            if bucket is not None:
                size = len(bucket.items())
            else:
                size = 0
            bucket_sizes.append(size)
        return bucket_sizes

