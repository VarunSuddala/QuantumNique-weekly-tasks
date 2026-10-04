def min_coins_brute_force(coins, amount):
    if amount == 0:
        return 0
    if amount < 0:
        return -1

    ans = float("inf")
    for c in coins:
        sub = min_coins_brute_force(coins, amount - c)
        if sub >= 0 and sub < ans:
            ans = sub + 1

    return ans if ans != float("inf") else -1


def min_coins_for_amount(coins, amount):
    if amount == 0:
        return 0

    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for c in coins:
            if i - c >= 0 and dp[i - c] != float("inf"):
                dp[i] = min(dp[i], dp[i - c] + 1)

    return dp[amount] if dp[amount] != float("inf") else -1


# Time Complexity: O(amount * len(coins))
# Space Complexity: O(amount)
