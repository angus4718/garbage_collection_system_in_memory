from MemoryManager import MemoryManager, MemoryStrategy
from MemoryOperation import MemoryOperation, MemoryOperationType
import matplotlib.pyplot as plt
import numpy as np
import time

def read_operations_from_file(file_path):
    input_file = open(file_path, mode='r')
    memory_operations = []
    for line in input_file.readlines():
        line = line.strip()
        if line == "":
            continue
        str_op = line.replace("\n", "").replace("\r", "").replace(" ", "").split(",")
        op_type_int = int(str_op[0])
        size = None if str_op[1] == "" else int(str_op[1])
        addr = None if str_op[2] == "" else int(str_op[2])
        memory_operations.append({
            "op": MemoryOperation(
                op_type=MemoryOperationType.REQUEST if op_type_int == 1 else MemoryOperationType.RELEASE,
                addr=addr, size=size),
            })
    input_file.close()
    return memory_operations


class TestContext:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def basic_test_on(self, test_file_path):
        start_time = time.time()
        test_cases = read_operations_from_file(test_file_path)
        print(f"Start test on {test_file_path}.")
        all_bucket_sizes = [[], [], []]
        for test_case in test_cases:
            if test_case["op"].op_type == MemoryOperationType.REQUEST:
                self.memory_manager.request(test_case["op"])
                #all_bucket_sizes[0].append(self.memory_manager.get_bucket_sizes_free_addresses())
                #all_bucket_sizes[1].append(self.memory_manager.get_bucket_sizes_free_sizes())
                #all_bucket_sizes[2].append(self.memory_manager.get_bucket_sizes_allocated_addresses())
            elif test_case["op"].op_type == MemoryOperationType.RELEASE:
                self.memory_manager.release(test_case["op"])
                #all_bucket_sizes[0].append(self.memory_manager.get_bucket_sizes_free_addresses())
                #all_bucket_sizes[1].append(self.memory_manager.get_bucket_sizes_free_sizes())
                #all_bucket_sizes[2].append(self.memory_manager.get_bucket_sizes_allocated_addresses())
        end_time = time.time()
        print(end_time - start_time)
        #print(np.sum(all_bucket_sizes[0][-1]))
        #print(np.sum(all_bucket_sizes[1][-1]))
        #print(np.sum(all_bucket_sizes[2][-1]))
        print('a')
        # Prepare the data for the surface plot
        for i in range(3):
            X = np.arange(len(all_bucket_sizes[i][0]))  # Bucket indices
            Y = np.arange(len(all_bucket_sizes[i]))  # Operation numbers
            X, Y = np.meshgrid(X, Y)  # Create the 2D grid for X and Y
            Z = np.array(all_bucket_sizes[i])  # Convert the bucket sizes into a NumPy array for Z values

            # Plotting the 3D surface
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            # Create the surface plot
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')

            # Add a color bar to show the bucket size scale
            fig.colorbar(surf, shrink=0.5, aspect=5)

            # Labels
            ax.set_xlabel('Bucket Index')
            ax.set_ylabel('Operation Number')
            ax.set_zlabel('Bucket Size')

            # Show plot
            plt.show()
        print(f"All test passed for {test_file_path}.")


if __name__ == "__main__":
    # This test code is only for you to debug the basic implementation of MemoryManager.
    # Please note that these are not final test cases for assessment.
    memory_manager_to_test = MemoryManager(strategy=MemoryStrategy.WORST_FIT)
    # Pass your `MemoryManager` implementation instance to the `TestContext` class.
    test_context = TestContext(memory_manager=memory_manager_to_test)
    test_context.basic_test_on("../Data/MY_TEST.csv")