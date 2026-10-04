class RangeMaxArrayBruteForce:
    def __init__(self, nums):
        self.arr = list(nums)

    def update(self, idx: int, val: int):
        self.arr[idx] = val

    def query(self, l: int, r: int) -> int:
        return max(self.arr[l:r + 1])


class SegmentTreeRangeMax:
    def __init__(self, nums):
        self.n = len(nums)
        self.tree = [float("-inf")] * (4 * self.n) if self.n > 0 else []
        if self.n > 0:
            self._build(nums, 0, 0, self.n - 1)

    def _build(self, nums, node, s, e):
        if s == e:
            self.tree[node] = nums[s]
            return
        mid = (s + e) // 2
        l_child = 2 * node + 1
        r_child = 2 * node + 2

        self._build(nums, l_child, s, mid)
        self._build(nums, r_child, mid + 1, e)
        self.tree[node] = max(self.tree[l_child], self.tree[r_child])

    def update(self, idx: int, val: int):
        if 0 <= idx < self.n:
            self._update(0, 0, self.n - 1, idx, val)

    def _update(self, node, s, e, idx, val):
        if s == e:
            self.tree[node] = val
            return
        mid = (s + e) // 2
        l_child = 2 * node + 1
        r_child = 2 * node + 2

        if idx <= mid:
            self._update(l_child, s, mid, idx, val)
        else:
            self._update(r_child, mid + 1, e, idx, val)

        self.tree[node] = max(self.tree[l_child], self.tree[r_child])

    def query(self, l: int, r: int) -> int:
        if self.n == 0 or l > r or l < 0 or r >= self.n:
            return float("-inf")
        return self._query(0, 0, self.n - 1, l, r)

    def _query(self, node, s, e, l, r):
        if e < l or s > r:
            return float("-inf")

        if l <= s and e <= r:
            return self.tree[node]

        mid = (s + e) // 2
        l_child = 2 * node + 1
        r_child = 2 * node + 2

        left_max = self._query(l_child, s, mid, l, r)
        right_max = self._query(r_child, mid + 1, e, l, r)

        return max(left_max, right_max)


# Time Complexity: O(log n) for update and query, O(n) build
# Space Complexity: O(n)
