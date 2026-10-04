def merge_intervals_brute_force(intervals):
    if not intervals:
        return []

    res = [list(x) for x in intervals]
    changed = True

    while changed:
        changed = False
        i = 0
        while i < len(res):
            j = i + 1
            while j < len(res):
                s1, e1 = res[i]
                s2, e2 = res[j]

                if not (e1 < s2 or e2 < s1):
                    res[i] = [min(s1, s2), max(e1, e2)]
                    res.pop(j)
                    changed = True
                else:
                    j += 1
            i += 1

    return sorted(res)


def merge_intervals(intervals):
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    res = [intervals[0]]

    for curr in intervals[1:]:
        last = res[-1]

        if curr[0] <= last[1]:
            last[1] = max(last[1], curr[1])
        else:
            res.append(curr)

    return res


# Time Complexity: O(n log n)
# Space Complexity: O(n)
