from typing import List, Tuple, Any, Optional
import numpy as np
class BSTNode:
    def __init__(self, key: int, value: object):
        self.key = key
        self.value = value
        self.left: Optional[BSTNode] = None
        self.right: Optional[BSTNode] = None

class BST:
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def _insert(self, node: Optional[BSTNode], key: int, value: Any) -> BSTNode:
        if node is None:
            return BSTNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value  # Update existing key
        return node

    def insert(self, key: int, value: Any) -> None:
        self.root = self._insert(self.root, key, value)

    def _query(self, node: Optional[BSTNode], key: int) -> Optional[Any]:
        if node is None:
            return None
        if key < node.key:
            return self._query(node.left, key)
        elif key > node.key:
            return self._query(node.right, key)
        else:
            return node.value

    def query(self, key: int) -> Optional[Any]:
        return self._query(self.root, key)

    def _delete(self, node: Optional[BSTNode], key: int) -> Optional[BSTNode]:
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            min_larger_node = self.find_min(node.right)
            node.key, node.value = min_larger_node.key, min_larger_node.value
            node.right = self._delete(node.right, min_larger_node.key)
        return node

    def delete(self, key: int) -> bool:
        if self.query(key) is None:
            return False
        self.root = self._delete(self.root, key)
        return True

    def find_min(self, node: BSTNode) -> BSTNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def find_max(self, node: Optional[BSTNode]) -> BSTNode:
        current = node
        while current.right is not None:
            current = current.right
        return current

    def items(self) -> List[Tuple[int, Any]]:
        return self._inorder_traversal(self.root)

    def _inorder_traversal(self, node: Optional[BSTNode]) -> List[Tuple[int, Any]]:
        if node is None:
            return []
        return self._inorder_traversal(node.left) + [(node.key, node.value)] + self._inorder_traversal(node.right)

    def find_successor(self, key: int) -> Optional[BSTNode]:
        current = self.root
        successor = None

        while current:
            if key < current.key:
                successor = current
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                # Node with the matching key found
                if current.right:
                    # The successor is the minimum key node in the right subtree
                    successor = self.find_min(current.right)
                    break
                else:
                    # There is no right child, the successor is one of the ancestors
                    # The loop has already set the correct successor in this case
                    break

        return successor

    def find_predecessor(self, key: int) -> Optional[BSTNode]:
        current = self.root
        predecessor = None

        while current:
            if key > current.key:
                predecessor = current
                current = current.right
            elif key < current.key:
                current = current.left
            else:
                # Node with the matching key found
                if current.left:
                    # The predecessor is the maximum key node in the left subtree
                    predecessor = self.find_max(current.left)
                    break
                else:
                    # There is no left child, the predecessor is one of the ancestors
                    # The loop has already set the correct predecessor in this case
                    break

        return predecessor

class TwoLevelHashTable:
    def __init__(self, bits: int):
        self.bits = bits
        self.capacity = 2 ** (bits // 3)
        self.buckets: List[Optional[BST]] = [None] * self.capacity
        self.bitmap = [0] * self.capacity

    def set_bitmap(self, index: int, value: int) -> None:
        self.bitmap[index] = value  # Set the bitmap value at the given index

    def first_level_hash(self, key: int) -> int:
        bucket_index = key * self.capacity // (2 ** self.bits)
        return bucket_index

    def insert(self, key: int, value: Any) -> None:
        first_level_index = self.first_level_hash(key)

        if self.buckets[first_level_index] is None:
            self.buckets[first_level_index] = BST()
            self.set_bitmap(first_level_index, 1)  # Mark this bucket as non-empty

        self.buckets[first_level_index].insert(key, value)

    def query(self, key: int) -> Optional[Any]:
        first_level_index = self.first_level_hash(key)
        if self.buckets[first_level_index] is None:
            return None

        return self.buckets[first_level_index].query(key)

    def delete(self, key: int) -> bool:
        first_level_index = self.first_level_hash(key)
        if self.buckets[first_level_index] is None:
            return False

        deleted = self.buckets[first_level_index].delete(key)

        if deleted and not self.buckets[first_level_index].root:
            self.buckets[first_level_index] = None
            self.set_bitmap(first_level_index, 0)  # Mark this bucket as empty

        return deleted

    def next_larger_key(self, key: int) -> Optional[Tuple[int, Any]]:
        first_level_index = self.first_level_hash(key)

        # Find the successor within the same bucket
        if self.buckets[first_level_index] is not None:
            successor_node = self.buckets[first_level_index].find_successor(key)
            if successor_node:
                return successor_node.key, successor_node.value

        # If not found, move to the next non-empty bucket
        for next_bucket_index in range(first_level_index + 1, self.capacity):
            if self.buckets[next_bucket_index] is not None:
                # Get the minimum key in this bucket
                min_node = self.buckets[next_bucket_index].find_min(self.buckets[next_bucket_index].root)
                if min_node:
                    return min_node.key, min_node.value

        # If we reach here, there is no larger key in the hash table
        return -1, -1

    def next_smaller_key(self, key: int) -> Optional[Tuple[int, Any]]:
        first_level_index = self.first_level_hash(key)

        # Find the predecessor within the same bucket
        if self.buckets[first_level_index] is not None:
            predecessor_node = self.buckets[first_level_index].find_predecessor(key)
            if predecessor_node:
                return predecessor_node.key, predecessor_node.value

        # If not found, move to the previous non-empty bucket
        for next_bucket_index in range(first_level_index -1, -1, -1):
            if self.buckets[next_bucket_index] is not None:
                # Get the maximum key in this bucket
                max_node = self.buckets[next_bucket_index].find_max(self.buckets[next_bucket_index].root)
                if max_node:
                    return max_node.key, max_node.value

        # If we reach here, there is no smaller key in the hash table
        return -1, -1

    def max_key(self) -> Optional[Tuple[int, Any]]:
        for bucket_index in range(self.capacity - 1, -1, -1):
            if self.buckets[bucket_index] is not None:
                # Find the maximum key within this non-empty bucket
                max_node = self.buckets[bucket_index].find_max(self.buckets[bucket_index].root)
                if max_node:
                    return max_node.key, max_node.value

        # If we reach here, there is no key in the hash table
        return -1, -1
    def items(self) -> List[Tuple[int, Any]]:
        # Method to extract all items from the entire hash table
        all_items_list = []
        for index, second_level_hash_table in enumerate(self.buckets):
            if second_level_hash_table is not None:
                second_level_items = second_level_hash_table.items()
                all_items_list.extend(second_level_items)
        return all_items_list

class BSTNodeList:
    def __init__(self, key: int, value: object):
        self.key = key
        self.value = [value] if not isinstance(value, list) else value
        self.left: Optional[BSTNodeList] = None
        self.right: Optional[BSTNodeList] = None

class BSTList:
    def __init__(self):
        self.root: Optional[BSTNodeList] = None

    def _insert(self, node: Optional[BSTNodeList], key: int, value: Any) -> BSTNodeList:
        if node is None:
            return BSTNodeList(key, [value])  # Wrap the value in a list when creating a new node
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Append the value to the existing list for this key
            if value not in node.value:  # Optional: prevent duplicate values in the list
                node.value.append(value)
        return node

    def insert(self, key: int, value: Any) -> None:
        self.root = self._insert(self.root, key, value)

    def _query(self, node: Optional[BSTNodeList], key: int) -> Optional[Any]:
        if node is None:
            return None
        if key < node.key:
            return self._query(node.left, key)
        elif key > node.key:
            return self._query(node.right, key)
        else:
            return node.value

    def query(self, key: int) -> Optional[Any]:
        return self._query(self.root, key)

    def _delete(self, node: Optional[BSTNodeList], key: int, value: Any = None) -> Optional[BSTNodeList]:
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key, value)
        elif key > node.key:
            node.right = self._delete(node.right, key, value)
        else:
            # If a value is specified, remove it from the list of values for this key
            if value is not None:
                if value in node.value:
                    node.value.remove(value)
                # If the list of values is now empty, remove the node
                if not node.value:
                    # Node has no values left and should be removed
                    if node.left is None:
                        return node.right
                    if node.right is None:
                        return node.left
                    # Node has two children, find the inorder successor
                    min_larger_node = self.find_min(node.right)
                    node.key, node.value = min_larger_node.key, min_larger_node.value
                    node.right = self._delete(node.right, min_larger_node.key)
            else:
                # No value specified, this means remove the node with this key
                if node.left is None:
                    return node.right
                if node.right is None:
                    return node.left
                min_larger_node = self.find_min(node.right)
                node.key, node.value = min_larger_node.key, min_larger_node.value
                node.right = self._delete(node.right, min_larger_node.key)
        return node

    def delete(self, key: int, value: Any = None) -> bool:
        if self.query(key) is None:
            return False
        self.root = self._delete(self.root, key, value)
        return True

    def find_min(self, node: BSTNodeList) -> BSTNodeList:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def find_max(self, node: Optional[BSTNodeList]) -> BSTNodeList:
        current = node
        while current.right is not None:
            current = current.right
        return current

    def items(self) -> List[Tuple[int, Any]]:
        return self._inorder_traversal(self.root)

    def _inorder_traversal(self, node: Optional[BSTNodeList]) -> List[Tuple[int, Any]]:
        if node is None:
            return []
        # The inorder traversal will include the key and the entire list of values
        return self._inorder_traversal(node.left) + [(node.key, node.value)] + self._inorder_traversal(node.right)

    def find_successor(self, key: int) -> Optional[BSTNodeList]:
        current = self.root
        successor = None

        while current:
            if key < current.key:
                successor = current
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                # Node with the matching key found
                if current.right:
                    # The successor is the minimum key node in the right subtree
                    successor = self.find_min(current.right)
                    break
                else:
                    # There is no right child, the successor is one of the ancestors
                    # The loop has already set the correct successor in this case
                    break

        return successor

    def find_predecessor(self, key: int) -> Optional[BSTNodeList]:
        current = self.root
        predecessor = None

        while current:
            if key > current.key:
                predecessor = current
                current = current.right
            elif key < current.key:
                current = current.left
            else:
                # Node with the matching key found
                if current.left:
                    # The predecessor is the maximum key node in the left subtree
                    predecessor = self.find_max(current.left)
                    break
                else:
                    # There is no left child, the predecessor is one of the ancestors
                    # The loop has already set the correct predecessor in this case
                    break

        return predecessor

class TwoLevelHashTableList:
    def __init__(self, bits: int):
        self.bits = bits
        self.M = 2 ** bits
        self.capacity = 2 ** (bits // 3)
        self.buckets: List[Optional[BSTList]] = [None] * self.capacity
        self.bitmap = [0] * self.capacity

    def set_bitmap(self, index: int, value: int) -> None:
        self.bitmap[index] = value  # Set the bitmap value at the given index

    def first_level_hash(self, key: int) -> int:
        if key == self.M:
            key = key - 1
        bucket_index = int(self.capacity * np.log2(key) // self.bits)

        return bucket_index

    def insert(self, key: int, value: Any) -> None:
        first_level_index = self.first_level_hash(key)
        if self.buckets[first_level_index] is None:
            self.buckets[first_level_index] = BSTList()
            self.set_bitmap(first_level_index, 1)  # Mark this bucket as non-empty
        self.buckets[first_level_index].insert(key, value)

    def query(self, key: int) -> Optional[Any]:
        first_level_index = self.first_level_hash(key)
        if self.buckets[first_level_index] is None:
            return None

        return self.buckets[first_level_index].query(key)

    def delete(self, key: int, value: Any = None) -> bool:
        first_level_index = self.first_level_hash(key)
        if self.buckets[first_level_index] is None:
            return False

        deleted = self.buckets[first_level_index].delete(key, value)

        if deleted and not self.buckets[first_level_index].root:
            self.buckets[first_level_index] = None
            self.set_bitmap(first_level_index, 0)  # Mark this bucket as empty

        return deleted

    def next_larger_key(self, key: int) -> Optional[Tuple[int, Any]]:
        first_level_index = self.first_level_hash(key)

        # Find the successor within the same bucket
        if self.buckets[first_level_index] is not None:
            successor_node = self.buckets[first_level_index].find_successor(key)
            if successor_node:
                return successor_node.key, successor_node.value

        # If not found, move to the next non-empty bucket
        for next_bucket_index in range(first_level_index + 1, self.capacity):
            if self.buckets[next_bucket_index] is not None:
                # Get the minimum key in this bucket
                min_node = self.buckets[next_bucket_index].find_min(self.buckets[next_bucket_index].root)
                if min_node:
                    return min_node.key, min_node.value

        # If we reach here, there is no larger key in the hash table
        return -1, -1

    def next_smaller_key(self, key: int) -> Optional[Tuple[int, Any]]:
        first_level_index = self.first_level_hash(key)

        # Find the predecessor within the same bucket
        if self.buckets[first_level_index] is not None:
            predecessor_node = self.buckets[first_level_index].find_predecessor(key)
            if predecessor_node:
                return predecessor_node.key, predecessor_node.value

        # If not found, move to the previous non-empty bucket
        for next_bucket_index in range(first_level_index -1, -1, -1):
            if self.buckets[next_bucket_index] is not None:
                # Get the maximum key in this bucket
                max_node = self.buckets[next_bucket_index].find_max(self.buckets[next_bucket_index].root)
                if max_node:
                    return max_node.key, max_node.value

        # If we reach here, there is no smaller key in the hash table
        return -1, -1

    def max_key(self) -> Optional[Tuple[int, Any]]:
        for bucket_index in range(self.capacity - 1, -1, -1):
            if self.buckets[bucket_index] is not None:
                # Find the maximum key within this non-empty bucket
                max_node = self.buckets[bucket_index].find_max(self.buckets[bucket_index].root)
                if max_node:
                    return max_node.key, max_node.value

        # If we reach here, there is no key in the hash table
        return -1, -1
    def items(self) -> List[Tuple[int, Any]]:
        # Method to extract all items from the entire hash table
        all_items_list = []
        for index, second_level_hash_table in enumerate(self.buckets):
            if second_level_hash_table is not None:
                second_level_items = second_level_hash_table.items()
                all_items_list.extend(second_level_items)
        return all_items_list