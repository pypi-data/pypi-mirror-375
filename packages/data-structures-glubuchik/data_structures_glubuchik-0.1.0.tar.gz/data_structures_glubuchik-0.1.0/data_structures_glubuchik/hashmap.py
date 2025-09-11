from dataclasses import dataclass


@dataclass
class Item:
    key: str
    value: int


class Hashmap:
    def __init__(self) -> None:
        self.size = 0
        self.capacity = 32
        self.elements: list[Item] = [None for _ in range(self.capacity)]    
        self.FILL_FACTOR = 0.75

    def hash(self, key: str) -> int:
        hashsum = sum([ord(c) for c in key])
        return hashsum % self.capacity
    
    def realloc(self):
        if self.size / self.capacity >= self.FILL_FACTOR:
            [self.elements.append(None) for _ in range(self.capacity)]
    
    def add(self, key: str, value: int):
        hashed = self.hash(key)
      
        if self.elements[hashed] is not None and self.elements[hashed] != 'REMOVED':
            self.realloc()
            temp = hashed + 1
            while True:
                if self.elements[temp] is None:
                    self.elements[temp] = Item(key, value)
                    self.size += 1
                    break
                if temp == self.capacity - 1:
                    temp -= 1
                
                temp += 1
            
        else:
            self.elements[hashed] = Item(key, value)
            self.size += 1

    def get(self, key: str) -> int:
        hashed = self.hash(key)

        if self.elements[hashed] is not None and self.elements[hashed] != 'REMOVED' and self.elements[hashed].key != key:
            for i in range(hashed + 1, self.capacity + hashed):
                if i > self.capacity - 1:
                    i = i - self.capacity - 1
                if self.elements[i] and self.elements[i].key == key:
                    return self.elements[i].value
            return None
        return self.elements[hashed].value if self.elements[hashed] != 'REMOVED' and self.elements[hashed] is not None else None
    
    def remove(self, key: str):
        hashed = self.hash(key)

        if self.elements[hashed]:
            self.elements[hashed] = 'REMOVED'
            self.size -= 1
        else:
            return IndexError
