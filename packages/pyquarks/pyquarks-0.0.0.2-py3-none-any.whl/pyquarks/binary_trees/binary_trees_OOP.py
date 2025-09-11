class TreeNode: # Template used
    def __init__(self, data): # Constructor
        self.data = data # contains random crap
        self.left = None # smaller side
        self.right = None # bigger side

class BinaryTree:
    def __init__(self):
        self.root = None # set root to none

    def insert(self, value): # function insert
        new_node = TreeNode(value) # new_node is an object of class TreeNode, containing data
        if self.root is None: # if there are no values in the tree yet
            self.root = new_node # root set to new node's index
        else: # if not, use the recursive function (syntax current_node, new_node)
            self._insert_recursive(self.root, new_node)

    def _insert_recursive(self, current, new_node): # a recursive function which checks the right path using... well, recursion.
        if new_node.data < current.data: # compares data of new node with the current node (left side counterpart)
            if current.left is None: # checks if there's an existing node
                current.left = new_node # if not, creates a node
            else:
                self._insert_recursive(current.left, new_node) # else, reuses the function to find an end
        else: # right side counterpart
            if current.right is None: # existing node check
                current.right = new_node # creation
            else:
                self._insert_recursive(current.right, new_node) # recur until the end is found

    def search(self, value): # easier way to call recursive search (looks more elegant)
        return self._search_recursive(self.root, value)

    def _search_recursive(self, current, value): # recursive search system
        if current is None:
            return None
        if current.data == value: # checks the data of node current with input value
            return current # returns node
        elif value < current.data: # if smaller, goes to the left
            return self._search_recursive(current.left, value) # recur
        else: # vice versa
            return self._search_recursive(current.right, value)

    # PROBABLY UNNECESSARY
    def visualize(self, node = None, depth = 0, visited = None): # use a function to show the tree, visited is a set of ids
        if visited is None: # if not visited before, it sets to visited
            visited = set()
        if node is None: # if it reached a dead end
            node = self.root # first node
        if node is None or id(node) in visited: # check if this node was visited before
            return
        visited.add(id(node)) # add the ID of said node to the visited list
        print("-" * depth + str(node.data)) # print node
        self.visualize(node.left, depth + 1, visited) # goes to the left node, and sets visited
        self.visualize(node.right, depth + 1, visited) # vice versa

    # WIP

    '''
        def delete(self, value):
            return self._delete_recursive(self.root, value)

        def _delete_recursive(self, current, value):
            prev = None
    '''