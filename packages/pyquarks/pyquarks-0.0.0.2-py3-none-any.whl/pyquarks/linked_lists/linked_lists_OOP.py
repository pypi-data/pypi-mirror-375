class Node: # Created a class called Node
    def __init__(self, data): # initialize it, (btw this is the constructor. runs automatically when you use this class)
        self.data = data # data from input
        self.next = None # set next to none

class LinkedList:
    def __init__(self):   # note: self is used when you refer to the object's attributes. basically like,
         self.head = None # let's say there are 2 objects of the same class. to know which object's attribute we're
                          # referring to, we use self.
                          # head is the root pointer, basically. if none, the list is empty

    def insert(self, data):
        new_node = Node(data) # using the other class here as a template
        if self.head == None: # if it's none (doesnt have a value)
            self.head = new_node # head points to the new node
        else: # if there are values
            current = self.head # start at head node
            while current.next: # simple loop to check if current.next has a value
                current = current.next # increments and keeps going
            current.next = new_node # sets the new node where the value is 'None'

    def delete_byval(self, value): # deletes by value
        current = self.head
        prev = None

        while current: # while it has a value (equal to `while current is not None:`)
            if current.data == value: # if the value of the current node's data matches
                if prev: # if there's a node before us
                    prev.next = current.next # basically connects the node before us to the node after us
                else: self.head = current.next # connects the head node to the next node
                return
            prev = current # to cache the previous node
            current = current.next # get the next node
        print("Value not found.")

    def delete_byind(self, index): # deletes by index
        if index < 0: # simple check
            print("Invalid index.")
            return

        current = self.head
        prev = None
        count = 0

        while current: # simple loop
            if count == index: # if we found it
                if prev: prev.next = current.next # if theres a value before, we link that to the next node
                else: self.head = current.next # if not, we set the head node to the next node
                return
            prev = current
            current = current.next
            count += 1

        print("Index out of bounds.")

    def display(self): # prints.
        current = self.head
        result = [] # an array which contains the results
        while current: # while value exists
            result.append(current.data) # append
            current = current.next # go to next node
        print(result) # print it