import re
from collections import defaultdict, deque
from datetime import datetime

print("=== Log Anomaly Detector ===")

X, T = map(int, input("Enter X and T: ").split())
n = int(input("Enter number of log entries: "))

pattern = re.compile(
    r"^(\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(FAIL|SUCCESS)$"
)

failures = defaultdict(deque)
suspicious = {}

for i in range(n):
    line = input().strip()
    match = pattern.match(line)

    if not match:
        continue

    timestamp, user, ip, status = match.groups()

    current_time = datetime.strptime(timestamp, "%H:%M")
    current_minutes = current_time.hour * 60 + current_time.minute

    queue = failures[user]

    while queue and current_minutes - queue[0][0] > T:
        queue.popleft()

    if status == "FAIL":
        queue.append((current_minutes, ip))

    elif status == "SUCCESS":
        if (
            len(queue) >= X
            and any(failure_ip != ip for _, failure_ip in queue)
            and user not in suspicious
        ):
            suspicious[user] = timestamp

for user in sorted(suspicious):
    print(user, suspicious[user])