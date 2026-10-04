class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def detect_and_remove_cycle_hash_set(head: ListNode):
    vis = set()
    curr = head
    prev = None

    while curr:
        if curr in vis:
            prev.next = None
            return head
        vis.add(curr)
        prev = curr
        curr = curr.next

    return head


def detect_and_remove_cycle(head: ListNode) -> ListNode:
    if not head or not head.next:
        return head

    slow = head
    fast = head
    has_cycle = False

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            has_cycle = True
            break

    if not has_cycle:
        return head

    slow = head

    if slow == fast:
        while fast.next != slow:
            fast = fast.next
        fast.next = None
        return head

    while slow.next != fast.next:
        slow = slow.next
        fast = fast.next

    fast.next = None
    return head


# Time Complexity: O(n)
# Space Complexity: O(1)
