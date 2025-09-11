class queues_OOP:
    def __init__(self, maxSize):
        self.array = []
        self.maxSize = maxSize
    
    def enter(self, new): # add a new value to stack
        if len(self.array) < self.maxSize: # given less than max size
            self.array.append(new) # add a value
        else:
            print("Queue overflow!") # or throw an error

    def leave(self):
        if len(self.array) != 0: # given too less ig
            for i in range(len(self.array) - 1): # so there is no overflow error when iterating
                self.array[i] = self.array[i + 1] # shift all values
            self.array.pop() # remove last value
        else:
            print("Queue underflow!") # or throw an error