import heapq

class KthLargestStreamBruteForce:
    def __init__(self, k: int):
        self.k = k
        self.arr = []

    def add(self, val: int):
        self.arr.append(val)
        if len(self.arr) < self.k:
            return None
        self.arr.sort(reverse=True)
        return self.arr[self.k - 1]


class KthLargestStream:
    def __init__(self, k: int):
        self.k = k
        self.h = []

    def add(self, val: int):
        heapq.heappush(self.h, val)

        if len(self.h) > self.k:
            heapq.heappop(self.h)

        if len(self.h) == self.k:
            return self.h[0]
        return None


# Time Complexity: O(log k) per add
# Space Complexity: O(k)
