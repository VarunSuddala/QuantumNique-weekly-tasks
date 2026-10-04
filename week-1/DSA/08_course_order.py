import itertools
from collections import deque

def course_order_brute_force(num_courses, prerequisites):
    for perm in itertools.permutations(range(num_courses)):
        pos = {c: i for i, c in enumerate(perm)}
        valid = True
        for crs, pre in prerequisites:
            if pos[pre] >= pos[crs]:
                valid = False
                break
        if valid:
            return list(perm)
    return []


def find_course_order(num_courses, prerequisites):
    adj = {i: [] for i in range(num_courses)}
    deg = [0] * num_courses

    for crs, pre in prerequisites:
        adj[pre].append(crs)
        deg[crs] += 1

    q = deque([i for i in range(num_courses) if deg[i] == 0])
    ans = []

    while q:
        curr = q.popleft()
        ans.append(curr)

        for nxt in adj[curr]:
            deg[nxt] -= 1
            if deg[nxt] == 0:
                q.append(nxt)

    if len(ans) == num_courses:
        return ans
    return []


# Time Complexity: O(V + E)
# Space Complexity: O(V + E)
