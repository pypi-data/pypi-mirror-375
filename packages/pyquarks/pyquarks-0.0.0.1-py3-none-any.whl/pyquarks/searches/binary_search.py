def binary_search(array, search_val:int): # gets target array and the value to search for
    l = 0 # left value
    r = len(array) - 1 # right value
    flag = False # if found

    while l <= r: # while left is smaller or equal to right value
        mid = (l + r) // 2 # calculate mid value every loop, and floor it (decimal values get rounded DOWN)
        if array[mid] == search_val: # if the middle value in the array is the search val
            print("value found at place", mid + 1) # show we found it (mid + 1 because starts at 0)
            flag = True # flag found = True
        if array[mid] < search_val: l = mid + 1 # left is removed from search params
        else: r = mid - 1 # right is removed from search params (done by moving boundaries)
    if flag == False: print("value not found.") # throw error