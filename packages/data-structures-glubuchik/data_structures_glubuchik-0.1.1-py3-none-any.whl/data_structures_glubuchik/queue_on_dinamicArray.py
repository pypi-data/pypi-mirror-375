import ctypes

class Queue(object):
    def __init__(self) -> None:
        self.head = 0
        self.tail = 0
        self.size = 0
        self.capacity = 1
        self.queue = self.make_queue(self.capacity)

    def __str__(self) -> str:
        s = ''
        for i in range(self.head, self.head + self.size):
            s += f'{self.queue[i]} '
        
        return s

    def cap(self):
        return self.capacity
    
    def len(self):
        return self.size
    
    def resize(self, new_cap):
        new_queue = self.make_queue(new_cap)

        for i in range(self.head, self.head + self.size):
            new_queue[i - self.head] = self.queue[i]
        
        self.queue = new_queue
        self.capacity = new_cap
        self.head = 0
        self.tail = self.size

    def push(self, element):
        if self.size == self.capacity:
            self.resize(2 * self.capacity)
            
        self.queue[self.tail] = element
        self.tail += 1
        self.size += 1


    def pop(self):
        if self.size == 0:
            print('error, queue size = 0')
        element = self.queue[self.head]
        self.queue[self.head] = 0
        self.head += 1
        self.size -= 1

        if self.size == self.capacity / 4:
            self.resize(self.capacity // 2)

        return element
        
    def make_queue(self, new_cap):
        return (new_cap * ctypes.py_object)()
