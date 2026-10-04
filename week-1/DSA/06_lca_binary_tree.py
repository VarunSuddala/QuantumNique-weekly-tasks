class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def find_path(root, target, path):
    if not root:
        return False
    path.append(root)
    if root == target:
        return True
    if find_path(root.left, target, path) or find_path(root.right, target, path):
        return True
    path.pop()
    return False


def lowest_common_ancestor_brute_force(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    p1 = []
    p2 = []
    if not find_path(root, p, p1) or not find_path(root, q, p2):
        return None

    ans = None
    for a, b in zip(p1, p2):
        if a == b:
            ans = a
        else:
            break
    return ans


def lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    if not root or root == p or root == q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root

    return left if left else right


# Time Complexity: O(n)
# Space Complexity: O(h)
