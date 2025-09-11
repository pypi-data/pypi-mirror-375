class BinarySearchTree:
    def __init__(self, data) -> None:
        self.data = data
        self.left = None
        self.right = None

    def search(self, value):     
        if value <= self.data and self.left:
            return self.left.search(value)
        elif value > self.data and self.right:
            return self.right.search(value)
        
        return value == self.data
        
    def insert(self, value):       
        if value <= self.data and self.left:
            self.left.insert(value)
        elif value <= self.data:
            self.left = BinaryTree(value)

        elif value > self.data and self.right:
            self.right.insert(value)
        else:
            self.right = BinaryTree(value)

    def delete_Tree(self):
        self.data = None
        self.left = None
        self.right = None
    
    def min_val_node(node):
        curr = node
        while curr.left is not None:
            curr = curr.left
        return curr

    def delete(self, value):
        if self is None:
            return -1
        
        if value < self.data:
            self.left = BinaryTree.delete(self.left, value)
        elif value > self.data:
            self.right = BinaryTree.delete(self.right, value)

        else:
            if self.left is None and self.right is None:
                self = None
            
            elif self.left is None:
                self = self.right
            elif self.right is None:
                self = self.left

            else:
                min_val = BinaryTree.min_val_node(self.right)
                self.data = min_val.data
                self.right = BinaryTree.delete(self.right, min_val.data)
