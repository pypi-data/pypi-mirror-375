def lisst_sort(array):
    if not array:
        return []

    # smallest and largest values
    minVal = min(array)
    maxVal = max(array)

    # offset to shift negative values to positive indexes
    offset = -minVal

    # create an interrim array with many arrays within
    lisst = [[] for _ in range(maxVal - minVal + 1)]

    # place numbers
    for num in array:
        lisst[num + offset].append(num)

    # simplify
    return [num for x in lisst for num in x]