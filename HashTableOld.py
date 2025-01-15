from typing import List, Tuple, Any, Optional
from sympy import nextprime
import random


class HashNode:
    def __init__(self, key: int, value: object):
        self.key = key
        self.value = value
        self.next: Optional[HashNode] = None


class HashTable:
    def __init__(self, values: List[Tuple[int, object]], capacity: int = 1024, w: int = 32) -> None:
        # TODO: initialize the hash table.
        # You can define or choose object type based on your needs.
        # Do not need to return anything.
        self.capacity = capacity  # This is 'm' in the hash function
        self.w = w
        self.p = nextprime(2 ** self.w)  # Use sympy to find a prime 'p'
        self.alpha = random.randint(1, self.p - 1)
        self.beta = random.randint(0, self.p - 1)
        while self.alpha == self.beta:  # Ensure alpha is not equal to beta
            self.beta = random.randint(0, self.p - 1)
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity
        for key, value in values:
            self.insert(key, value)

    def _hash(self, key: int) -> int:
        return (self.alpha * key + self.beta) % self.p % self.capacity

    def delete(self, key: int) -> bool:
        # TODO: delete an existing value.
        # Return True if successfully deleted, False if the key does not exist in the database.
        index = self._hash(key)
        node = self.buckets[index]
        prev = None

        while node is not None and node.key != key:
            prev = node
            node = node.next

        if node is None:
            return False

        if prev is None:
            self.buckets[index] = node.next
        else:
            prev.next = node.next

        return True

    def insert(self, key: int, value: object) -> None:
        # TODO: insert a new value into the database.
        # Do not need to return anything.
        # Hash the key and get the index for the buckets array
        index = self._hash(key)
        # Create a new hash node
        new_node = HashNode(key, value)
        # Insert the new node into the linked list at the bucket
        if self.buckets[index] is None:
            self.buckets[index] = new_node
        else:
            # Collision resolution by chaining
            current = self.buckets[index]
            while current.next:
                if current.key == key:
                    # Update the value if the key is already present
                    current.value = value
                    return
                current = current.next
            if current.key == key:
                # Update the value if the key is already present
                current.value = value
            else:
                # Add the new node at the end of the linked list
                current.next = new_node

    def query(self, key: int) -> Optional[object]:
        # TODO: query by key. Return None if the key does not exist.
        # Return the query result. Return None if the key does not exist in the database.
        index = self._hash(key)
        node = self.buckets[index]

        while node:
            if node.key == key:
                return node.value
            node = node.next

        return None

    def get_all_keys(self) -> List[int]:
        keys = []
        for bucket in self.buckets:
            node = bucket
            while node is not None:
                keys.append(node.key)
                node = node.next
        return keys

    def items(self) -> List[Tuple[int, object]]:
        items_list = []
        for bucket in self.buckets:
            node = bucket
            while node is not None:
                items_list.append((node.key, node.value))
                node = node.next
        return items_list

    def get_bucket(self, key: int) -> Optional[List[HashNode]]:
        # Calculate the index for the key
        index = self._hash(key)
        # Retrieve the bucket at the index
        bucket = self.buckets[index]
        # If the bucket is not empty, collect all nodes in that bucket
        if bucket:
            nodes = []
            current = bucket
            while current:
                nodes.append(current)
                current = current.next
            return nodes
        else:
            # If the bucket is empty, return None or an empty list
            return None
