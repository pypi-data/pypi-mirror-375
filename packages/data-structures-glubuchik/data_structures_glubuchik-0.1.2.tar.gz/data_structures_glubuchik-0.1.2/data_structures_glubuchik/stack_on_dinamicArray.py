import ctypes


class Stack(object):
    def __init__(self) -> None:
        self.count = 1
        self.size = 0
        self.capacity = 1
        self.stack = self.make_stack(self.capacity)

    def __str__(self) -> str:
        s = ''
        for i in range(self.size):
            s += f'{self.stack[i]} '
        
        return s

    def cap(self):
        return self.capacity
    
    def len(self):
        return self.size
    
    def resize(self, new_cap):
        new_stack = self.make_stack(new_cap)

        for i in range(self.size):
            new_stack[i] = self.stack[i]
        
        self.stack = new_stack
        self.capacity = new_cap

    def push(self, element):
        if self.size == self.capacity:
            self.resize(2 * self.capacity)

        self.stack[self.size] = element
        self.size += 1

    def pop(self) -> any:
        if self.size == 0:
            print('error, stack size = 0')
        elem = self.stack[self.size - 1]
        self.stack[self.size - 1] = 0
        self.size -= 1

        if self.size == self.capacity / 4:
            self.resize(self.capacity / 2)

        return elem
        
    def make_stack(self, new_cap):
        return (new_cap * ctypes.py_object)()
