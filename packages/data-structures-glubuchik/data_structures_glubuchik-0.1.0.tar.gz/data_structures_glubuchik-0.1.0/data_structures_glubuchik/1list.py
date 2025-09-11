class Node():
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList():

    def __init__(self):
        self.head = None

    def new_head(self, data):
        new_Node = Node(data)

        if not self.head:
            self.head = new_Node
            return

        new_Node.next = self.head
        self.head = new_Node
        return

    def append_list(self, data):
        new_Node = Node(data)

        if not self.head:
            self.head = new_Node
            return
        
        curr = self.head
        while curr.next:
            curr = curr.next

        curr.next = new_Node

    def insert_list(self, data, index):
        new_Node = Node(data)

        curr = self.head
        count = 0
        while count != index - 1:
            curr = curr.next
            count += 1
        
        curr_after = curr.next
        curr.next = new_Node
        new_Node.next = curr_after
 
    def print_list(self):
        curr = self.head
        res = ''

        while curr is not None:
            res += str(curr.data)

            if curr.next:
                res += ', '
            
            curr = curr.next
        
        print(res)
        return
    
    def length(self):
        curr = self.head
        count = 1
        while curr.next:
            count += 1
            curr = curr.next

        return count
    
    def delete(self, index):

        if index > self.length() or index < 0:
            return IndexError
        
        curr = self.head
        count = 0
        while count != index - 1:
            count += 1
            curr = curr.next
        
        deleted = curr.next
        after_deleted = deleted.next

        curr.next = after_deleted
        return


a = LinkedList()
a.new_head(1)
a.append_list(4)
a.append_list(6)
a.insert_list(7, 3)
print(a.length())
a.print_list()
a.delete(3)
a.print_list()
print(a.length())

