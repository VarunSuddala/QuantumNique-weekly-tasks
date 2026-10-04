"""
Minimum Window Containing All Required Skills (Minimum Window Substring)
Given two strings S and T, return the minimum window substring of S such that every
character in T (including duplicates) is included in the window. If there is no such
substring, return an empty string "".
"""

from collections import Counter

def min_window_brute_force(s: str, t: str) -> str:
    if not s or not t or len(s) < len(t):
        return ""

    t_count = Counter(t)
    min_window = ""
    min_len = float("inf")

    n = len(s)
    for i in range(n):
        for j in range(i + len(t), n + 1):
            sub = s[i:j]
            sub_count = Counter(sub)
            valid = True
            for ch, req in t_count.items():
                if sub_count[ch] < req:
                    valid = False
                    break
            if valid and len(sub) < min_len:
                min_len = len(sub)
                min_window = sub
                break  
    return min_window


#Optimized Idea:
def min_window(s: str, t: str) -> str:
    if not s or not t or len(s) < len(t):
        return ""

    target_count = Counter(t)
    window_count = {}

    have = 0
    need = len(target_count)

    best_len = float("inf")
    best_range = (0, 0)
    left = 0

    for right, ch in enumerate(s):
        window_count[ch] = window_count.get(ch, 0) + 1

        if ch in target_count and window_count[ch] == target_count[ch]:
            have += 1

        while have == need:
            current_len = right - left + 1
            if current_len < best_len:
                best_len = current_len
                best_range = (left, right + 1)

            left_char = s[left]
            window_count[left_char] -= 1
            if left_char in target_count and window_count[left_char] < target_count[left_char]:
                have -= 1
            left += 1

    return s[best_range[0]:best_range[1]] if best_len != float("inf") else ""


# Time Complexity : O(m + n): 
# Space Complexity: O(k)
