def neigbor_check(cell1, cell2):
    if cell1[0] in cell2 and cell1[1] in cell2:
        return True
    elif cell1[1] in cell2 and cell1[2] in cell2:
        return True
    elif cell1[0] in cell2 and cell1[2] in cell2:
        return True
    else:
        return False

a = 0
b = 0

for n in range(len(cells[11])):

    for i in range(len(cells[11])):

        if neigbor_check(cells[11].data[n], cells[11].data[i]) and not n==i and n > i:
            a+=1
        if n == i:
            b += 1

print(a,b)