def stacks(array:list, maxSize:int, func:str, item = None): # the array, its size, and either to push or pop

    def push(item):
        if len(array) < maxSize: # given that the size is less than maxsize
            array.append(item) # it adds a value to the stack
        else:
            print("Stack overflow!") # or throw an error

    def pop():
        if len(array) != 0: # given the length is not zero
            array.pop() # remove the value
        else:
            print("stack underflow!") # or throw an error

    if func == "push": # using the function in order to... well, use the function.
        if item == None: # checking for errors
            raise print("Push operation requires an item! Do stacks(array, maxSize, func, item)") # throw error
        push(item) # or just push
    elif func == "pop": pop() # and the other function
    else: print("Invalid function type. Try using 'push' or 'pop'.") # or an invalid function