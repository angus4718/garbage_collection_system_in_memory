import enum
from typing import Dict, List, Tuple
from MemoryOperation import MemoryOperation
from MemoryOperation import MemoryOperationType
from HashTableOld import HashTable
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
        # TODO:
        #  Initialize the hash tables for memory storage.
        #  Do not need to return anything.
        self.total_memory = 1024
        self.free_sizes_hash_table = HashTable(values=[])
        self.free_addresses_hash_table = HashTable(values=[])
        self.allocated_addresses_hash_table = HashTable(values=[])
        self.free_sizes_hash_table.insert(self.total_memory, [0]) # A list with one element: the start address of the free block.
        self.free_addresses_hash_table.insert(0, self.total_memory) # The whole memory block starts at address 0 and is free.

    def _find_block(self, size: int) -> Tuple[int, int]:
        if self.strategy == MemoryStrategy.FIRST_FIT:
            all_keys = self.free_addresses_hash_table.get_all_keys()
            # Initialize with no block found
            smallest_key = None
            smallest_key_block_size = None
            for start_address in all_keys:
                block_size = self.free_addresses_hash_table.query(start_address)
                if block_size and block_size >= size:
                    # Update if this is the smallest key found so far
                    if smallest_key is None or start_address < smallest_key:
                        smallest_key = start_address
                        smallest_key_block_size = block_size
            if smallest_key is not None:
                return smallest_key, smallest_key_block_size

        elif self.strategy == MemoryStrategy.BEST_FIT:
            best_start_address = -1
            best_fit_size = float('inf')

            all_keys = self.free_addresses_hash_table.get_all_keys()
            for start_address in all_keys:
                block_size = self.free_addresses_hash_table.query(start_address)
                if block_size and block_size >= size and block_size < best_fit_size:
                    best_start_address = start_address
                    best_fit_size = block_size

            if best_start_address != -1:
                return best_start_address, best_fit_size

        elif self.strategy == MemoryStrategy.WORST_FIT:
            worst_start_address = -1
            worst_fit_size = -1

            all_keys = self.free_addresses_hash_table.get_all_keys()
            for start_address in all_keys:
                block_size = self.free_addresses_hash_table.query(start_address)
                if block_size and block_size >= size and (worst_fit_size == -1 or block_size > worst_fit_size):
                    worst_start_address = start_address
                    worst_fit_size = block_size

            if worst_start_address != -1:
                return worst_start_address, worst_fit_size

        return -1, -1

    def _allocate(self, start: int, size: int) -> None:
        # Allocate a block of memory and update the data structures
        allocated = False

        # Create a list to keep track of the changes to be made in the hash table
        updates = []
        deletions = []

        # Check all free blocks to find the right place for allocation
        for free_start, free_size in self.free_addresses_hash_table.items():
            free_end = free_start + free_size
            if start >= free_start and start + size <= free_end:
                # The allocation fits within this block
                allocated = True
                if free_start < start:
                    # There's space before the allocation, add to updates
                    updates.append((free_start, start - free_start))
                if start + size < free_end:
                    # There's space after the allocation, add to updates
                    updates.append((start + size, free_end - (start + size)))
                # Since we're allocating part of this block, the original needs to be deleted
                deletions.append(free_start)
                # No need to check other blocks
                break

        if not allocated:
            raise Exception(f"Cannot allocate block at {start} with size {size}.")

        # Apply the updates and deletions to the free addresses hash table
        for free_start in deletions:
            self.free_addresses_hash_table.delete(free_start)
        for free_start, free_size in updates:
            self.free_addresses_hash_table.insert(free_start, free_size)

        # Allocate the block by adding it to the allocated addresses hash table
        self.allocated_addresses_hash_table.insert(start, size)
        self._merge_allocated_blocks()

    def _deallocate(self, start: int, size: int) -> None:
        # Find the allocated block that contains the start address
        for allocated_start in self.allocated_addresses_hash_table.get_all_keys():
            allocated_size = self.allocated_addresses_hash_table.query(allocated_start)
            allocated_end = allocated_start + allocated_size

            if allocated_start <= start < allocated_end:
                dealloc_end = start + size

                # Check if the deallocation is within bounds
                if dealloc_end > allocated_end:
                    # Handle the error - requested deallocation exceeds the allocated block
                    return

                # Remove the original block from allocated addresses
                self.allocated_addresses_hash_table.delete(allocated_start)

                # If there is a leading part of the block that remains allocated
                if start > allocated_start:
                    leading_size = start - allocated_start
                    self.allocated_addresses_hash_table.insert(allocated_start, leading_size)

                # If there is a trailing part of the block that remains allocated
                if allocated_end > dealloc_end:
                    trailing_size = allocated_end - dealloc_end
                    self.allocated_addresses_hash_table.insert(dealloc_end, trailing_size)

                # Insert the deallocated block into the free addresses
                self.free_addresses_hash_table.insert(start, size)

                # Merge any adjacent free blocks
                self._merge_free_blocks()
                break
        else:
            # Handle the error - start address not found in allocated blocks
            pass

    def _merge_free_blocks(self) -> None:
        merged = True
        while merged:
            merged = False
            keys_to_delete = []
            for start, size in list(self.free_addresses_hash_table.items()):
                # Calculate the end of the current block
                end = start + size

                # If the end of this block is the start of another block, merge them
                if end in self.free_addresses_hash_table.get_all_keys():
                    # Merge the blocks by adding the size of the next block to the current one
                    start_block_size = self.free_addresses_hash_table.query(start)
                    end_block_size = self.free_addresses_hash_table.query(end)

                    if start_block_size is not None and end_block_size is not None:
                        # Calculate the new size for the start block after merging
                        new_start_block_size = start_block_size + end_block_size

                        # Insert the new size for the start block into the hash table
                        self.free_addresses_hash_table.insert(start, new_start_block_size)

                        # Now delete the end block from the hash table, as it's been merged with the start block
                        self.free_addresses_hash_table.delete(end)

                        # Mark the next block for deletion
                        keys_to_delete.append(end)
                    else:
                        # Handle the case where one of the blocks does not exist or does not have a valid size
                        # This could involve logging an error, raising an exception, or other error handling
                        pass


                    # We made a merge, so we should check again after this iteration
                    merged = True

            # Delete all keys that have been merged
            for key in keys_to_delete:
                self.free_addresses_hash_table.delete(key)

    def _merge_allocated_blocks(self) -> None:
        merged = True
        while merged:
            merged = False
            keys_to_delete = []
            for start, size in list(self.allocated_addresses_hash_table.items()):
                # Calculate the end of the current block
                end = start + size

                # If the end of this block is the start of another block, merge them
                if end in self.allocated_addresses_hash_table.get_all_keys():
                    # Merge the blocks by adding the size of the next block to the current one
                    start_block_size = self.allocated_addresses_hash_table.query(start)
                    end_block_size = self.allocated_addresses_hash_table.query(end)

                    if start_block_size is not None and end_block_size is not None:
                        # Calculate the new size for the start block after merging
                        new_start_block_size = start_block_size + end_block_size

                        # Insert the new size for the start block into the hash table
                        self.allocated_addresses_hash_table.insert(start, new_start_block_size)

                        # Now delete the end block from the hash table, as it's been merged with the start block
                        self.allocated_addresses_hash_table.delete(end)

                        # Mark the next block for deletion
                        keys_to_delete.append(end)
                    else:
                        # Handle the case where one of the blocks does not exist or does not have a valid size
                        # This could involve logging an error, raising an exception, or other error handling
                        pass


                    # We made a merge, so we should check again after this iteration
                    merged = True

            # Delete all keys that have been merged
            for key in keys_to_delete:
                self.allocated_addresses_hash_table.delete(key)

    def request(self, op: MemoryOperation) -> int:
        # TODO:
        #  Accepts a space request (of a specified number of bytes that may include an optional starting byte address),
        #   and allocate memory.
        #  If the memory is not available (is occupied already), the request should not be accepted.
        #  Remember to allocate the memory according to current strategy (self.strategy) unless the address is given.
        #  Return the allocated address if the memory is allocated successfully.
        #  Otherwise, return -1.
        size = op.size
        if op.addr is not None:
            # If address is provided, check if it's available
            if not self.is_valid_op(op):
                return -1
            self._allocate(op.addr, size)
            print(self.free_addresses_hash_table.items())
            print(self.allocated_addresses_hash_table.items())
            return op.addr
        else:
            # Find a block based on the strategy
            start, _ = self._find_block(size)
            if start != -1:
                self._allocate(start, size)
                print(self.free_addresses_hash_table.items())
                print(self.allocated_addresses_hash_table.items())
                return start
            return -1

    def release(self, op: MemoryOperation) -> bool:
        # TODO:
        #  Accepts a space release (with a defined starting byte address and its corresponding number of bytes),
        #   and release memory.
        #  Return True if the memory is released successfully.
        #  Otherwise, return False.
        if not self.is_valid_op(op):
            return False
            # Release the block and merge adjacent free blocks if necessary
        self._deallocate(op.addr, op.size)
        print(self.free_addresses_hash_table.items())
        print(self.allocated_addresses_hash_table.items())
        return True

    def is_valid_op(self, op: MemoryOperation) -> bool:
        if op.op_type == MemoryOperationType.REQUEST:
            # If a specific address is requested, check if it falls within any of the free blocks
            if op.addr is not None:
                for free_start, free_size in self.free_addresses_hash_table.items():
                    free_end = free_start + free_size
                    if free_start <= op.addr < free_end:
                        # Check if the free block has enough space from op.addr to fit op.size
                        remaining_size = free_end - op.addr
                        if remaining_size >= op.size:
                            return True
                # If no free block satisfies the request, return False
                return False
            # If no specific address is requested, check if there is any free block that is large enough
            else:
                for start, size in self.free_addresses_hash_table.items():
                    if size >= op.size:
                        return True
                return False
        elif op.op_type == MemoryOperationType.RELEASE:
            # Whether the release is valid will be decided later in _deallocate
            return True

        # If the operation type is neither REQUEST nor RELEASE, return False
        return False


