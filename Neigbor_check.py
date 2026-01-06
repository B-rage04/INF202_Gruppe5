def neigbor_check(cell1, cell2):
    if cell1[0] in cell2 and cell1[1] in cell2:
        return True
    elif cell1[1] in cell2 and cell1[2] in cell2:
        return True
    elif cell1[0] in cell2 and cell1[2] in cell2:
        return True
    else:
        return False
