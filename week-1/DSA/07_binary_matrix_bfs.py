from collections import deque

def shortest_path_binary_matrix_dfs(grid):
    n = len(grid)
    if grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
        return -1

    vis = set([(0, 0)])
    dirs = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    min_dist = [float("inf")]

    def dfs(r, c, d):
        if r == n - 1 and c == n - 1:
            min_dist[0] = min(min_dist[0], d)
            return

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0 and (nr, nc) not in vis:
                vis.add((nr, nc))
                dfs(nr, nc, d + 1)
                vis.remove((nr, nc))

    dfs(0, 0, 1)
    return min_dist[0] if min_dist[0] != float("inf") else -1


def shortest_path_binary_matrix(grid):
    n = len(grid)
    if grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
        return -1

    if n == 1:
        return 1

    dirs = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    q = deque([(0, 0, 1)])
    vis = set([(0, 0)])

    while q:
        r, c, d = q.popleft()

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc

            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                if nr == n - 1 and nc == n - 1:
                    return d + 1

                if (nr, nc) not in vis:
                    vis.add((nr, nc))
                    q.append((nr, nc, d + 1))

    return -1


# Time Complexity: O(n^2)
# Space Complexity: O(n^2)
