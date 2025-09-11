from collections import deque
from binary_search_tree import BinaryTree


def bfs_on_deque(root: BinaryTree):
    q = deque()
    q += [root]
    while q:
        for _ in range(len(q)):
            node = q.popleft()
            if node:
                print(node.data, end=' ')
                q += [node.left]
                q += [node.right]


def bfs_on_queue(root: BinaryTree):
    root = [root]
    result = []

    while root:
        q = []
        for curr in root:
            result.append(curr.data)
            if curr.left:
                q += [curr.left]
            if curr.right:
                q += [curr.right]
        root = q

    print(*result)


def dfs(root: BinaryTree):
    if not root:
        return 
    dfs(root.left)
    print(root.data, end=' ')
    dfs(root.right)
