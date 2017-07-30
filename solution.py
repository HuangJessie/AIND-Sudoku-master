assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values
 
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """    
    # For each unit in unitlist, find 
    for unit in unitlist:       
        for u in unit:
            # Proceed only when there are only 2 digits
            if len(values[u]) == 2:
               # Find the naked twins
                twin_key = [ t for t in unit if values[u] == values[t] and u != t]
                # Proceed when the naked twins exit:
                if len(twin_key)>0:
                    # Find other boxes in unit to be updated
                    neq_key = [n for n in unit if values[n] != values[u] ]
                    # Eliminate the naked twins as possibilities for their peers           
                    for n in neq_key:
                        for digit in values[u]:  
                            #values[n] = values[n].replace(digit,'')
                            values = assign_value(values, n, values[n].replace(digit,''))     
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]


rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Include 2 diagonal units for Diagonal Sudoku
diag_1 = [[r+c for (r,c) in zip(rows,cols)]]
diag_2 = [[r+c for (r,c) in zip(rows,cols[::-1])]]
# Added the 2 diagonal units to list
unitlist = diag_1 + diag_2 + row_units + column_units + square_units 
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    if len(grid) == 81:
        # Create Sudoku dictionary
        sudoku_dictionary = dict(zip(boxes, grid))
        for n in sudoku_dictionary:
            # Assign full values if missing
            if sudoku_dictionary[n] == ".":
                sudoku_dictionary[n] = "123456789"
        return sudoku_dictionary
    else:
        return "ERROR: invalid grid length!"

    
def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # Define the total width of the sudoku
    width = 1+max(len(values[s]) for s in boxes)
    # Define lines for the block (3 by 3)
    line = '+'.join(['-'*(width*3)]*3)
    # Loop through each row and print the result, seperate by each 3 digits
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
    # First, find all the solved values 
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    # Go through all the solved values
    for box in solved_values:
        digit = values[box]
        # Eliminate the value from the values of all its peers
        for peer in peers[box]:
            #values[peer] = values[peer].replace(digit,'')
            values = assign_value(values, peer, values[peer].replace(digit,''))
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # Go through all units in the unit list
    for unit in unitlist:
        for n in '123456789':
            box = [u for u in unit if n in values[u]]
            # Find the unit with only one value
            if len(box) == 1:
                #values[box[0]] = n
                values = assign_value(values, box[0], n)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Check is there is still unsolved values before continue
        if solved_values_before < 81:
            # NOTE: in order to have the Sanity check works, Eliminate function should run last
            # Use the Only Choice Strategy
            values = only_choice(values)
            # Use Naked Twins Strategy
            values = naked_twins(values)
            # Use the Eliminate Strategy
            values = eliminate(values)
            # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after      
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if values == False:
        return False

    if len([box for box in values.keys() if len(values[box])==1]) == 81:
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    min_num = min( len(values[box]) for box in values.keys() if len(values[box]) > 1 )
    min_key = [box for box in values.keys() if len(values[box]) == min_num][0] 
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for v in values[min_key]:
        new_values = values.copy()
        new_values = assign_value(new_values, min_key, v)
        new_values = search(new_values)        
        if new_values:
            return new_values    


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """   
    # Create dictionary
    values = grid_values(grid)
    # Solve the puzzle
    values = search(values)
    return values
    
    
if __name__ == '__main__':
    diag_sudoku_grid ='9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................' 

    
    #'2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'


    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
        
        

