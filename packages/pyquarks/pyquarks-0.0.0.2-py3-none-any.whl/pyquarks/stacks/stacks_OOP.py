class stacks_OOP():
    def __init__(self, maxSize): # constructor, construct arraysize and array within
        self.array = []
        self.maxSize = maxSize
    
    def push(self, item):
        if len(self.array) < self.maxSize: # given that the size is less than maxsize
            self.array.append(item) # it adds a value to the stack
        else:
            print("Stack overflow!") # or throw an error

    def pop(self):
        if len(self.array) != 0: # given the length is not zero
            self.array.pop() # remove the value
        else:
            print("stack underflow!") # or throw an error