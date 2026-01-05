def neigbor_check(cell1, cell2):
    """
    Checks if two cells are neigbors
    """
    if cell1[0] == cell2[0] and cell1[1] == cell2[1]:
        return True
    elif cell1[1] == cell2[1] and cell1[2] == cell2[2]:
        return True
    elif cell1[0] == cell2[0] and cell1[2] == cell2[2]:
        return True
    else:
        return False
