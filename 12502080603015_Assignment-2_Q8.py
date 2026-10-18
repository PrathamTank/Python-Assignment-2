MOD = 1000000007

print("=== Matrix Path Optimizer ===")

n, m = map(int, input("Enter rows and columns: ").split())

previous_score = [None] * m
previous_count = [0] * m

for i in range(n):
    row = input(f"Enter row {i + 1}: ").split()

    current_score = [None] * m
    current_count = [0] * m

    for j in range(m):
        if row[j] == "X":
            continue

        value = int(row[j])

        if i == 0 and j == 0:
            current_score[j] = value
            current_count[j] = 1
            continue

        candidates = []

        if j > 0 and current_score[j - 1] is not None:
            candidates.append((current_score[j - 1], current_count[j - 1]))

        if previous_score[j] is not None:
            candidates.append((previous_score[j], previous_count[j]))

        if j > 0 and previous_score[j - 1] is not None:
            candidates.append((previous_score[j - 1], previous_count[j - 1]))

        if candidates:
            best_score = max(score for score, count in candidates)
            ways = sum(
                count for score, count in candidates
                if score == best_score
            ) % MOD

            current_score[j] = best_score + value
            current_count[j] = ways

    previous_score = current_score
    previous_count = current_count

if previous_score[m - 1] is None:
    print("IMPOSSIBLE")
else:
    print(previous_score[m - 1], previous_count[m - 1])