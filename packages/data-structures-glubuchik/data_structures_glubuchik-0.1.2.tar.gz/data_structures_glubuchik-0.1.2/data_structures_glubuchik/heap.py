class BinaryHeap():
    def __init__(self, elements) -> None:
        if elements is not None:
            self.heap(elements)
        else:
            self.elements = []
        self._length = None

    def length(self):
        self._length = len(self.elements)
        return self._length
    
    def add(self, element):
        self.elements.append(element)
        i = self.length() - 1
        parent = int((i - 1) / 2)

        while i < 0 and list[i] > list[parent]:
            list[i]. list[parent] = list[parent], list[i]
            i = parent
            parent = int((i - 1) / 2)

    def heapify(self, i):
        left = 2 * i + 1
        right = 2 * i + 2

        if left < self.length():
            if self.elements[i] < self.elements[left]:
                self.elements[left], self.elements[i] = self.elements[i], self.elements[left]
                self.heapify(left)

        if right < self.length():
            if self.elements[i] < self.elements[right]:
                self.elements[right], self.elements[i] = self.elements[i], self.elements[right]
                self.heapify(right)

    def get_max(self):
        res = self.elements[0]
        self.elements[0] = self.elements[-1]
        self.elements.pop(-1)
        self.heapify(0)
        return res
    
    def heap(self, elements):
        self.elements = elements
        for i in range(int(self.length() / 2 + 1), -1, -1):
            self.heapify(i)
