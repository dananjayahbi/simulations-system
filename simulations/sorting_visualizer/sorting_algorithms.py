# sorting_algorithms.py - Sorting algorithm implementations as generators


def bubble_sort(array):
    """
    Bubble Sort implementation as a generator.
    Yields after each comparison for visualization.
    """
    n = len(array)
    for i in range(n):
        for j in range(0, n - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
            yield array, j, j + 1  # Yield current state and compared indices


def quick_sort(array, low=0, high=None):
    """
    Quick Sort implementation as a generator.
    Yields after each swap for visualization.
    """
    if high is None:
        high = len(array) - 1
    
    if low < high:
        # Partition
        pivot = array[high]
        i = low - 1
        
        for j in range(low, high):
            yield array, j, high  # Yield comparison
            if array[j] <= pivot:
                i += 1
                array[i], array[j] = array[j], array[i]
                yield array, i, j  # Yield swap
        
        array[i + 1], array[high] = array[high], array[i + 1]
        yield array, i + 1, high  # Yield pivot placement
        
        pi = i + 1
        
        # Recursively sort left and right partitions
        yield from quick_sort(array, low, pi - 1)
        yield from quick_sort(array, pi + 1, high)


def merge_sort(array, left=0, right=None):
    """
    Merge Sort implementation as a generator.
    Yields after each merge operation for visualization.
    """
    if right is None:
        right = len(array) - 1
    
    if left < right:
        mid = (left + right) // 2
        
        # Sort left half
        yield from merge_sort(array, left, mid)
        # Sort right half
        yield from merge_sort(array, mid + 1, right)
        # Merge
        yield from merge(array, left, mid, right)


def merge(array, left, mid, right):
    """Helper function for merge sort - merges two halves."""
    left_copy = array[left:mid + 1]
    right_copy = array[mid + 1:right + 1]
    
    i = j = 0
    k = left
    
    while i < len(left_copy) and j < len(right_copy):
        if left_copy[i] <= right_copy[j]:
            array[k] = left_copy[i]
            i += 1
        else:
            array[k] = right_copy[j]
            j += 1
        yield array, k, mid  # Yield after each placement
        k += 1
    
    while i < len(left_copy):
        array[k] = left_copy[i]
        yield array, k, mid
        i += 1
        k += 1
    
    while j < len(right_copy):
        array[k] = right_copy[j]
        yield array, k, mid
        j += 1
        k += 1


# Algorithm mapping dictionary
ALGORITHM_MAP = {
    "Bubble Sort": bubble_sort,
    "Quick Sort": quick_sort,
    "Merge Sort": merge_sort
}
