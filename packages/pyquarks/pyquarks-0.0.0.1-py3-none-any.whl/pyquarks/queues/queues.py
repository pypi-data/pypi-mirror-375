def queues(array:list, maxSize:int, func:str, data=None):

    def enter(new): # add a new value to stack
        if len(array) < maxSize: # given less than max size
            array.append(new) # add a value
        else:
            print("Queue overflow!") # or throw an error

    def leave():
        if len(array) != 0: # given too less ig
            for i in range(len(array) - 1): # so there is no overflow error when iterating
                array[i] = array[i + 1] # shift all values
            array.pop() # remove last value
        else:
            print("Queue underflow!") # or throw an error

    if func == 'enter':
        if data == None:
            print("Try using `queues(array, maxSize, func, data)`")
        enter(data)
    elif func == 'leave':
        leave()
    else:
        print("Invalid function. Try using 'enter' or 'leave'.")