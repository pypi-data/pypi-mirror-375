class Node(object):
    def __init__(self, data=None) -> None:
        self.data = data
        self.next = None
        self.prev = None


class De_queue(object):
    def __init__(self) -> None:
        self.size = 0
        self.head = Node()
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head

    def push_front(self, data):
        new_node = Node(data)
        new_node.next = self.head.next
        new_node.prev = self.head
        self.head.next.prev = new_node
        self.head.next = new_node
        self.size += 1

    def push_back(self, data):
        new_node = Node(data)
        new_node.prev = self.tail.prev
        self.tail.prev.next = new_node
        self.tail.prev = new_node
        new_node.next = self.tail
        self.size += 1

    def pop_front(self):
        if self.head.next == self.tail:
            return
        
        elem = self.head.next
        
        elem.next.prev = self.head
        self.head = elem.next
        elem.next = None
        elem.prev = None
        self.size -= 1

        return elem.data
    
    def pop_back(self):
        if self.head.next == self.tail:
            return
        
        elem = self.tail.prev
        
        elem.prev.next = self.tail
        self.tail.prev = elem.prev
        elem.next = None
        elem.prev = None
        self.size -= 1

        return elem.data
    
    def print_De_queue(self):
        curr = self.head.next
        while curr.next:
            print(curr.data, end = ' ')
            curr = curr.next
        print()


