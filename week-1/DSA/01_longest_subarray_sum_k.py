def longest_subarray_sum_k_brute_force(nums, k):
    ans = 0
    n = len(nums)
    for i in range(n):
        curr = 0
        for j in range(i, n):
            curr += nums[j]
            if curr == k:
                ans = max(ans, j - i + 1)
    return ans


def longest_subarray_sum_k(nums, k):
    mp = {}
    curr = 0
    ans = 0

    for i, x in enumerate(nums):
        curr += x

        if curr == k:
            ans = i + 1

        rem = curr - k
        if rem in mp:
            ans = max(ans, i - mp[rem])

        if curr not in mp:
            mp[curr] = i

    return ans


# Time Complexity: O(n)
# Space Complexity: O(n)
