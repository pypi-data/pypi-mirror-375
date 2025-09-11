import ctypes


class DinamicArray(object):
    def __init__(self) -> None:
        self.size = 0
        self.capacity = 1
        self.array = self.make_array(self.capacity)

    def __str__(self) -> str:
        s = ''
        for i in range(self.size):
            s += f'{self.array[i]} '
        return s

    def cap(self):
        return self.capacity
    
    def len(self):
        return self.size
    
    def resize(self, new_cap):
        new_array = self.make_array(new_cap)

        for i in range(self.size):
            new_array[i] = self.array[i]
        
        self.array = new_array
        self.capacity = new_cap

    def append(self, element):
        if self.size == self.capacity:
            self.resize(2 * self.capacity)

        self.array[self.size] = element
        self.size += 1

    def delete(self):
        if self.size == 0:
            print('error, array size = 0')
        self.array[self.size - 1] = 0
        self.size -= 1

        if self.size == self.capacity / 4:
            self.resize(self.capacity / 2)

    def insert(self, index, element):
        if index < 0 or index > self.size:
            print('error, index is out of range')

        if self.size == self.capacity:
            self.resize(2 * self.capacity)

        for i in range(self.size - 1, index - 1, -1):
            self.array[i + 1] = self.array[i]

        self.array[index] = element
        self.size += 1

    def remove(self, index):
        if index < 0 or index > self.size:
            print('error, index is out of range')
        if self.size == 0:
            print('error, array size = 0')

        if index == self.size - 1:
            self.array[index] = 0
            self.size -= 1
            return

        for i in range(index, self.size - 1):
            self.array[i] = self.array[i + 1]
        
        self.array[self.size - 1] = 0
        self.size -= 1
        
    def make_array(self, new_cap):
        return (new_cap * ctypes.py_object)()
    
    def get_by_index(self, index):
        return self.array[index]
    


