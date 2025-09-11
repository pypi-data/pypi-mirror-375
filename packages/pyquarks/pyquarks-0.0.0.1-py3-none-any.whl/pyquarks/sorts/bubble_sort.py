# a temporary array
# temp = [4, 2, 8, 3, 10, 12, 6, 8]

def bubble_sort(array): # get the array as an input to the function
    n = len(array) # using a variable n to make life easier (it gets the length of said array)
    for i in range(n - 1): # so loops from 0 to length-1
        for j in range(n - i - 1): # loops from 0 to length - 1 (added the -i because the values in the top are sorted, and dont have to be checked again.)
            if array[j] > array[j + 1]: # if current value is bigger than the next value
                array[j], array[j + 1] = array[j + 1], array[j] # swap values (yes, thats a thing)

# print(bubble_sort(temp)) # how it would work in theory is it executes the function within the print and prints it directly