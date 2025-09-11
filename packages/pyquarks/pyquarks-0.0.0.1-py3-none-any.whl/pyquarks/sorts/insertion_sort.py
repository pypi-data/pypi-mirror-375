# temp = [4, 2, 8, 3, 10, 12, 6, 8]

def insertion_sort(array): 
    for i in range(1, len(array)):
        j = i - 1
        while j >= 0 and array[j] > array[i]:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = array[i]

# print(insertion_sort(temp))