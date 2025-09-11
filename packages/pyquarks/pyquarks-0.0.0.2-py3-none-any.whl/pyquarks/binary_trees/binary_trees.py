# declaration of variables :nerd:
tree = []
NullPtr = -1
RootPtr = -1

# node template using dictionaries
def create_node(data):
    return {'LftPtr': NullPtr, 'Data': data, 'RgtPtr': NullPtr}

###################
# Inserting Nodes #
###################

def insert_node(value):
    global RootPtr

    # creates a node and adds it to the tree
    new_node = create_node(value)
    new_node_index = len(tree)
    tree.append(new_node)

    # sets the root node
    if RootPtr == NullPtr:
        RootPtr = new_node_index
        return

    # loop to find the correct position within tree
    current = RootPtr
    while True:
        if value < tree[current]['Data']:
            # left if the value is smaller
            if tree[current]['LftPtr'] == NullPtr:
                tree[current]['LftPtr'] = new_node_index
                return
            current = tree[current]['LftPtr']
        else:
            # right if the value is bigger
            if tree[current]['RgtPtr'] == NullPtr:
                tree[current]['RgtPtr'] = new_node_index
                return
            current = tree[current]['RgtPtr']

############
# Searches #
############

# return_parent=True returns the parent index
def search_byval(value, return_parent=False): # searches by data in node
    current = RootPtr
    parent = NullPtr
    is_left = False # cache parent data

    while current != NullPtr:
        if tree[current]['Data'] == value:
            if return_parent:
                return current, parent, is_left # return node index, parent index, and side
            return current # return node index
        elif value < tree[current]['Data']:
            parent = current
            is_left = True
            current = tree[current]['LftPtr'] # move to left
        else:
            parent = current
            is_left = False
            current = tree[current]['RgtPtr'] # move to right

    if return_parent:
        return NullPtr, NullPtr, False # not found
    return NullPtr


# return_parent=True does same thing as above
def search_byind(index, return_parent=False): # searches for a node by its index
    if not (0 <= index < len(tree)) or tree[index] is None:
        if return_parent:
            return None, None, False # invalid index or deleted node
        return None

    current = RootPtr
    parent = NullPtr
    is_left = False

    while current != NullPtr:
        if current == index:
            if return_parent:
                return tree[current], tree[parent] if parent != NullPtr else None, is_left
            return tree[current]
        elif tree[index]['Data'] < tree[current]['Data']:
            parent = current
            is_left = True
            current = tree[current]['LftPtr']
        else:
            parent = current
            is_left = False
            current = tree[current]['RgtPtr']

    if return_parent:
        return None, None, False
    return None

##################
# Deleting Nodes #
##################

# deletes a node by value or index, comes with deleting all its children and such
def delete_node(value, by='val'):
    global RootPtr

    # search mode selector
    if by == 'val':
        current, parent, is_left = search_byval(value, return_parent=True)
    elif by == 'ind':
        node, parent, is_left = search_byind(value, return_parent=True)
        current = value if node else NullPtr
    else:
        print("Invalid search mode. syntax: by='val'")
        return

    # invalid node handler
    if current == NullPtr or tree[current] is None:
        print("Invalid node")
        return

    # get child pointers
    left = tree[current]['LftPtr']
    right = tree[current]['RgtPtr']

    # delete left and right nodes
    if left != NullPtr and tree[left] is not None:
        tree[left] = None
    if right != NullPtr and tree[right] is not None:
        tree[right] = None

    # delete node
    tree[current] = None

    # emancipation
    if parent != NullPtr:
        if is_left:
            tree[parent]['LftPtr'] = NullPtr
        else:
            tree[parent]['RgtPtr'] = NullPtr
    else:
        RootPtr = NullPtr # root deletion handler

##############
# Print Tree #
##############

# prints the whole tree
def print_tree():
    for i, node in enumerate(tree):
        if node is not None:
            print("Index", str(i), ": Data=", str(node['Data']), "LftPtr=", str(node['LftPtr']), "RgtPtr=", str(node['RgtPtr']))
        else:
            print("Index", str(i), ": Deleted")

def visualize(index=RootPtr, depth=0):
    if index == NullPtr or index >= len(tree) or tree[index] is None:
        return

    # print current node with depth
    print("-" * depth + str(tree[index]['Data']))

    # increase depth (recursion)
    visualize(tree[index]['LftPtr'], depth + 1)
    visualize(tree[index]['RgtPtr'], depth + 1)


# And that is IT
# plug in values and enjoy the show

# temp values
# insert_node(69)
# insert_node(6)
# insert_node(75)
# insert_node(45)
# insert_node(2)
# insert_node(420)