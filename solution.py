#For this project, I construct a program that can solve a sudoku containing diagonals and naked twins.
#I add the diagonal units to the unit lists and add the naked_twins() function to the reduce_puzzle() function.
rows = 'ABCDEFGHI'
cols = '123456789'
index = [0,1,2,3,4,5,6,7,8]
assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board, record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy. First perform the  depth-first search and propagation.
    Args:
    values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
    the values dictionary with the naked twins eliminated from peers.
    Input: The sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    n_t = []
    for box in values:
        if len(values[box]) == 2:
            for peer in peers[box]:
                if box < peer and values[peer] == values[box]:
                    n_t.append([box,peer])
    for nt in n_t:
        unitss = [u for u in unitlist if nt[0] in u and nt[1] in u]
        for unit in unitss:
            for box in unit:
                if box != nt[0] and box != nt[1]:
                   values[box] = values[box].replace(values[nt[0]][0],'')
                   assign_value(values, box, values[box]) 
                   values[box] = values[box].replace(values[nt[0]][1],'')
                   assign_value(values, box, values[box])
    if len([box for box in values.keys() if len(values[box]) == 0]):
       return False
    return values
def cross(A, B):
    """
    Cross product of elements in A and elements in B.
    Input: Two variables in string form.
    Ouput: A variable in string form.
    """
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
#For diagonal units, I just create two units and add them to the rest of unit list.
diagonal_units = [[rows[d]+cols[d] for d in index],[rows[8-d]+cols[d] for d in index[::-1]]]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
    grid(string) - A grid in string form.
    Returns:
    A grid in dictionary form.
    Keys: The boxes, e.g., 'A1'
    Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    Input: A grid in string form.
    Output: A grid in dictionary form.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
    values(dict): 
    Input: A sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
            assign_value(values, peer, values[peer])
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
                assign_value(values, dplaces[0], values[dplaces[0]])
    return values

def reduce_puzzle(values):
    """
    Iterate only_choice(), eliminate() and naked_twins(). If at some point, there is a box with  no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after the iterations, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = only_choice(values)
        values = eliminate(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagration, try all possible values.
    Iterate with reduce_puzzle() first. Check if it fails or solves it.
    Choose minimum possibility box, and use recurrence for each resulting sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    newvalues = reduce_puzzle(values)
    if newvalues is False:
        return False
    if all(len(newvalues[s]) == 1 for s in boxes):
        return newvalues
    n,s = min((len(newvalues[s]),s) for s in boxes if len(newvalues[s]) > 1)
    for value in newvalues[s]:
        newsudoku = newvalues.copy()
        newsudoku[s] = value
        attempt = search(newsudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.

    Input: A grid in string form.
    Output: The final sudoku grid.
    """
    grid = grid_values(grid)
    return search(grid)

if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
