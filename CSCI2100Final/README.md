# README: Memory Management System

## Overview

This repository implements a **Memory Management System** designed to simulate memory allocation and deallocation using different strategies. It supports **First Fit**, **Best Fit**, and **Worst Fit** allocation strategies for managing memory blocks. The system employs **Two-Level Hash Tables** and **Binary Search Trees (BST)** to efficiently store and manage memory blocks.

The project is broken into the following components:

1. **HashTable.py**: Implements the `TwoLevelHashTable` and `TwoLevelHashTableList` classes for efficient memory management.
2. **MemoryManager.py**: Contains the `MemoryManager` class, which provides memory operations such as allocation, deallocation, and merging of memory blocks.
3. **MemoryOperation.py**: Defines the `MemoryOperation` and `MemoryOperationType` classes for specifying memory operations.
4. **Test.py**: Provides a framework for testing the memory manager with sample input files.

---

## Features

### Memory Allocation Strategies
The system supports the following memory allocation strategies:
- **First Fit**: Allocates the first memory block that satisfies the requested size.
- **Best Fit**: Allocates the smallest block that satisfies the requested size.
- **Worst Fit**: Allocates the largest block available.

### Data Structures
The system uses:
- **Two-Level Hash Tables**: For efficient storage of free and allocated memory blocks.
- **Binary Search Trees (BST)**: To manage and query memory blocks within hash table buckets.

---

## File Descriptions

### 1. **HashTable.py**
Defines the following classes:
- **`BST` and `BSTNode`**: Implements a binary search tree for managing memory blocks at the second level of the hash table.
- **`TwoLevelHashTable`**: A two-level hash table where each bucket contains a BST for fast memory block management.
- **`TwoLevelHashTableList`**: Similar to `TwoLevelHashTable`, but supports storing multiple values for the same key (used for free sizes).

### 2. **MemoryManager.py**
Defines the `MemoryManager` class, which provides core memory management functionality:
- Memory allocation (`request` method).
- Memory deallocation (`release` method).
- Block merging for efficient memory utilization.
- Strategies for selecting memory blocks (`FIRST_FIT`, `BEST_FIT`, `WORST_FIT`).

The memory manager uses:
- A hash table for free memory sizes.
- A hash table for free memory starting addresses.
- A hash table for allocated memory addresses.

### 3. **MemoryOperation.py**
Defines:
- **`MemoryOperationType`**: Enum for `REQUEST` and `RELEASE` operations.
- **`MemoryOperation`**: Represents a single memory operation, including its type, size, and address.

### 4. **Test.py**
- Reads test cases from a CSV file.
- Executes memory operations on the `MemoryManager`.
- Validates the results against expected outcomes.

---

## How to Use

### 1. **Setup**
Ensure you have Python 3.8+ installed. Clone the repository and navigate to the project directory.

### 2. **Run Tests**
Modify the `test_file_path` in `Test.py` to point to your test file (e.g., `../Data/WORST_FIT.csv`). Then, run:

```bash
python Test.py
```

### 3. **File Format for Test Cases**
The test cases are read from a CSV file formatted as follows:
- **Columns**: `OperationType, Size, Address, ExpectedAddress`
- **OperationType**:
  - `1` for `REQUEST`
  - `0` for `RELEASE`
- **Size**: Memory size for the operation.
- **Address**: Address for the operation (if applicable).
- **ExpectedAddress**: Expected result (used for validation).

Example:
```csv
1, 64, , 0
1, 128, , 64
0, 64, 0,
```

### 4. **Customize the Memory Manager**
You can change the allocation strategy by modifying this line in `Test.py`:

```python
memory_manager_to_test = MemoryManager(strategy=MemoryStrategy.WORST_FIT)
```

Available strategies:
- `MemoryStrategy.FIRST_FIT`
- `MemoryStrategy.BEST_FIT`
- `MemoryStrategy.WORST_FIT`

---

## Key Classes and Methods

### MemoryManager
| Method                      | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `request(op: MemoryOperation) -> int` | Allocates memory based on the given operation and strategy. Returns the start address of the allocated block. |
| `release(op: MemoryOperation) -> bool` | Deallocates memory based on the given operation. Returns `True` if successful. |
| `_find_block(size: int) -> Tuple[int, int]` | Finds a memory block based on the allocation strategy. |
| `_allocate(start: int, size: int) -> None` | Allocates a block of memory and updates hash tables. |
| `_deallocate(start: int, size: int) -> bool` | Deallocates a block of memory and updates hash tables. |
| `_merge_free_blocks(start: int, size: int) -> None` | Merges adjacent free memory blocks for efficient utilization. |

### TwoLevelHashTable
| Method                      | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `insert(key: int, value: Any)` | Inserts a key-value pair into the hash table.                             |
| `query(key: int) -> Optional[Any]` | Queries a value based on the key.                                       |
| `delete(key: int) -> bool`   | Deletes a key-value pair from the hash table.                              |
| `next_larger_key(key: int)`  | Finds the next larger key in the hash table.                               |
| `next_smaller_key(key: int)` | Finds the next smaller key in the hash table.                              |

---

## Example Usage

### Allocating Memory
```python
from MemoryManager import MemoryManager, MemoryStrategy
from MemoryOperation import MemoryOperation, MemoryOperationType

# Create a memory manager with Best Fit strategy
mem_manager = MemoryManager(strategy=MemoryStrategy.BEST_FIT)

# Request 128 bytes of memory
op_request = MemoryOperation(op_type=MemoryOperationType.REQUEST, size=128)
allocated_address = mem_manager.request(op_request)
print(f"Allocated Address: {allocated_address}")

# Release the allocated memory
op_release = MemoryOperation(op_type=MemoryOperationType.RELEASE, addr=allocated_address, size=128)
mem_manager.release(op_release)
```

---

## Testing

### Sample Test Case
Input file (`test.csv`):
```csv
1, 64, ,
1, 128, ,
0, 64, 0,
```

Run the test:
```bash
python Test.py
```

Expected Output:
```
Start test on test.csv.
All test passed for test.csv.
```

---

## Dependencies
- Python 3.8+
- `numpy` (for logarithmic operations)

Install dependencies using:
```bash
pip install numpy
```

---

## Future Enhancements
- Add support for dynamic memory resizing.
- Improve performance for large-scale memory operations.
- Implement additional allocation strategies (e.g., Next Fit).

---

## License
This project is open-source and free to use.
