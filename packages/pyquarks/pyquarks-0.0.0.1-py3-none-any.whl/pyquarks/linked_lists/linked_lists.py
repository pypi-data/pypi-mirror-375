# I explained this file like I would to a baby so ask away if u have any doubts lol

################
# Creating LLs #
################

# declaring vars
array = []
NullPtr = -1
StartPtr = NullPtr
FreeListPtr = 0

# empty node template
def create_node(data=None, next_ptr=NullPtr):
    return {'data': data, 'next': next_ptr}

# initialize list size and such
def initialize_list(size):
    global array, FreeListPtr # global vars

    # using the template to create dictionaries within an array of range size
    array = [create_node(next_ptr = i + 1) for i in range(size)]
    
    # setting the last node's next value to -1 (NullPtr = -1) and marking the end
    array[-1]['next'] = NullPtr

    # used later to insert nodes from index 0
    FreeListPtr = 0

###################
# Inserting Nodes #
###################

def insert_node(value):
    global StartPtr, FreeListPtr # global vars

    if FreeListPtr == NullPtr: # check for free space
        print("No free space!")
        return

    new_node_index = FreeListPtr # the place in which a new node will be inserted at
    FreeListPtr = array[FreeListPtr]['next'] # updating to point to next free node

    array[new_node_index]['data'] = value # store value in data
    array[new_node_index]['next'] = NullPtr # store next value as -1

    # If list is empty or value smaller than the first one
    if StartPtr == NullPtr or value < array[StartPtr]['data']:
        # value inserted at the first
        array[new_node_index]['next'] = StartPtr
        # update start pointer
        StartPtr = new_node_index

    # if there are values, find the sorted order and insert there
    else:
        prev = StartPtr # start searching from the beginning
        current = array[StartPtr]['next'] # next node

        # loop until the right place is found
        while current != NullPtr and array[current]['data'] < value:
            prev = current
            current = array[current]['next']

        # link between previous and current nodes
        array[new_node_index]['next'] = current
        array[prev]['next'] = new_node_index

####################
# Searching Values #
####################

def find_element(value):
    current = StartPtr # start from beginning

    # simple loop when not the end
    while current != NullPtr:
        if array[current]['data'] == value:
            return current # return the index if found
        current = array[current]['next'] # move to the next node

    return NullPtr # value not found

##############################
# Delete Nodes - With Values #
##############################

def delete_node(value):
    global StartPtr, FreeListPtr # global vars
    current = StartPtr # start from beginning
    prev = NullPtr # keep in memory the last node

    # simple loop to find the node to delete
    while current != NullPtr and array[current]['data'] != value:
        prev = current
        current = array[current]['next']

    # if we reached the end, the value wasnt found
    if current == NullPtr:
        print("Value not found.")
        return

    # unlink the nodes
    if prev == NullPtr:
        StartPtr = array[current]['next'] # user for the first node
    else:
        array[prev]['next'] = array[current]['next'] # used for the other nodes

    # cleared node and added a free list
    array[current]['data'] = None
    array[current]['next'] = FreeListPtr
    FreeListPtr = current

###################
# Printing Values #
###################

def display_list():
    current = StartPtr
    result = []

    # simple loop again
    while current != NullPtr:
        result.append(array[current]['data'])
        current = array[current]['next']

    print(result)


# That is it
# Now using the functions we've created to manipulate data
# just plug in values, and you'll get answers



# Just some tests, you can try them if u want ig
# initialize_list(10) # creates 10 empty nodes
# insert_node(6) # inserts 6
# insert_node(2) # inserts 2 before 6
# insert_node(8) # inserts 8 after 6
# display_list() # should print [2, 6, 8]
# print(find_element(6)) # should print the index of value 6 (0, i think)
# delete_node(8) # delete 8 from the list
# display_list() # should print [2, 6]