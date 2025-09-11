def linear_search(array, search_val): # input target array and search value
    flag = False

    for i in range(0, len(array)): # simple loop
        if array[i] == search_val: # comparator
            print("value found at place", i + 1) # output found
            flag = True # set flag
    if flag == False: print("value not found.") # invalid value