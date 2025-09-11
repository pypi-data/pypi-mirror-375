class Node(object):
    def __init__(self, data) -> None:
        self.data = data
        self.next = None


class Stack(object):
    def __init__(self) -> None:
        self.top = None

    def __str__(self) -> str:
        curr = self.top
        s = f'{curr.data} '
        while curr.next:
            s += f'{curr.next.data}'
        return s

    def push(self, data):
        new_node = Node(data)

        if not self.top:
            self.top = new_node
            return
        
        new_node.next = self.top
        self.top = new_node

    def pop(self):
        if not self.top:
            return -1
        
        top = self.top

        if self.top.next:
            self.top = self.top.next
        else:
            self.top = None

        return top.data
    
    def empty(self):
        if not self.top:
            return True
        
        return False
    
    def size(self):
        count = 1
        curr = self.top
        while curr.next:
            count += 1

        return count
