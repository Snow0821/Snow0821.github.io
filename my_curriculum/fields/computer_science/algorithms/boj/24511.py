from collections import deque

N = int(input())

types = list(map(int, input().split()))
numbers = list(map(int, input().split()))

q = deque()

for i in range(N):
    if not types[i]:
        q.appendleft(numbers[i])

M = int(input())

X = list(map(int, input().split()))

ans = []

for x in X:
    q.append(x)
    ans.append(q.popleft())

print(*ans)