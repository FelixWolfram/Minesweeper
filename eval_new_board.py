from collections import deque
import numpy as np
import random


def check_for_solvable(board: list[list[int]], board_size: int, revealed: set, mine_count: int) -> bool:
    mines = set()
    too_long_something_went_wrong = 0
    not_ended = True    # lets the loop break if it gets stuck, because it would have to guess

    while not_ended:
        if len(revealed) == (board_size ** 2 - mine_count):   # if all fields were revealed
            break
        too_long_something_went_wrong += 1
        if too_long_something_went_wrong > 30:
            return False
        not_ended = False
        all_neighbors = []  # list of all the neighbors
        matrix_lines = []  # maps num in revealed to the matrix row
        matrix_solutions = []
        # get list of cells that contain numbers and are adjacent to at least one unknown cell
        for r, c in revealed:   # for every revealed number
            unrevealed_neighbors = [neighbor for neighbor in find_neighbors(r, c, board_size)
                                    if (neighbor not in revealed) and neighbor not in mines]
                                            # find all neighboring cells and save the ones, that are not revealed

            if unrevealed_neighbors: # if size > 0
                unrevealed_neighbors = [neighbor for neighbor in find_neighbors(r, c, board_size)
                    if (neighbor not in revealed)]

                for unrevealed_neighbor in unrevealed_neighbors:  # for every neighbor cell
                    if unrevealed_neighbor not in all_neighbors:  # if not already added
                        all_neighbors.append(unrevealed_neighbor)  # append all the neighbors to the list

                index = sorted([all_neighbors.index(unrevealed_neighbor) for unrevealed_neighbor in unrevealed_neighbors])
                matrix_lines.append(index)  # append matrix line
                matrix_solutions.append(board[r][c])    # and it's solution to that line

        if len(all_neighbors) == 0: # when every revealed number has only other already revealed numbers or mines as neighbors
            return False

        # we now have for every revealed number the matrix line indexes which are "1" and the solutions to the line
        # we now want to convert the matrix line into a line consistent of only "1" (at the indexes) and fill up the rest with "0"
        # creating the matrix lines and solution to the lines
        matrix_lines_finished = np.array([   #  creates an array containing 0 or 1 for every "matrix_row" in "matrix_rows" and storing it in "matrix_lines"
            [1 if j in matrix_lines[i] else 0 for j in range(len(all_neighbors))] for i in range(len(matrix_lines))
        ])

        # solve the matrix and interpret it
        matrix_solutions = np.array(matrix_solutions)
        solved, matrix_solutions = gaussian_elimination(matrix_lines_finished, matrix_solutions)
        # now check for the lower and upper bound in each row --> if it meats one bound, then there can only be one solution for that row
        # if we know that there is e.g. 1 bomb for a certain index --> lower lower_bound by 1 and solution[i] by one, then perform the check
        for i in range(len(solved) - 1, -1, -1):    # iterate in reverse --> start from the bottom up to use partial solutions
            for j in range(len(all_neighbors)):
                if all_neighbors[j] in revealed and solved[i][j] != 0:     # when we already know that the cell is safe
                    solved[i][j] = 0  # set that index to 0 and subtract it from the solution --> because now there's 1 bomb less to be found
                elif all_neighbors[j] in mines and solved[i][j] != 0: # when we already know there's a bomb for that cell
                    matrix_solutions[i] -= solved[i][j]
                    solved[i][j] = 0    # set that index to 0 and subtract it from the solution --> because now there's 1 bomb less to be found
            upper_bound = 0
            for j in range(len(solved[i])):
                if solved[i][j] > 0:
                    upper_bound += solved[i][j]
            lower_bound = 0
            for j in range(len(solved[i])):
                if solved[i][j] < 0:
                    lower_bound += solved[i][j]

            # when the solution for a row meets the upper or lower bound of the row, there is only one solution for that cell
            # except upper_bound und lower_bound are both "0" --> then the whole line is just "0" and no cell can be revealed or flagged
            if lower_bound == upper_bound == 0:
                continue
            elif matrix_solutions[i] == upper_bound and matrix_solutions[i] >= 0:  # mine(s)
                not_ended = found_mine(solved, i, board_size, revealed, all_neighbors, mines, board)
            elif matrix_solutions[i] == upper_bound and matrix_solutions[i] < 0:  # flag(s)
                not_ended = found_save(solved, i, board_size, revealed, all_neighbors, mines, board)
            elif matrix_solutions[i] == lower_bound and matrix_solutions[i] >= 0:  # flag(s)
                not_ended = found_save(solved, i, board_size, revealed, all_neighbors, mines, board)
            elif matrix_solutions[i] == lower_bound and matrix_solutions[i] < 0:  # mines(s)
                not_ended = found_mine(solved, i, board_size, revealed, all_neighbors, mines, board)
    else:   # when the loop ends without hitting the "break" statement, this will get executed
        return False
    return True # if the "break" statement is reached


# check whether the player has won
def check_for_end(board_size, revealed, mines):
    for r in range(board_size):
        for c in range(board_size):
            if (r, c) not in revealed and (r, c) not in mines:  # when a cell which is not a mine is not revealed yet
                return False     # player has not won (at least not yet)
    # when reaching this point, no empty cells are left which are not mines are left --> player has won
    return True


def found_mine(solved, i, board_size, revealed, all_neighbors, mines, board):
    for j in range(len(solved[i])):
        if solved[i][j] > 0:
            mines.add(all_neighbors[j])
        elif solved[i][j] < 0:
            r, c = all_neighbors[j]
            reveal(r, c, board, board_size, revealed)
    return True


def found_save(solved,i , board_size, revealed, all_neighbors, mines, board):
    for j in range(len(solved[i])):
        if solved[i][j] > 0:
            r, c = all_neighbors[j]
            reveal(r, c, board, board_size, revealed)
        elif solved[i][j] < 0 and not solved[i][j].any(mines):  # any() returns True if (at least) one item in the array matches the parameter
            mines.add(all_neighbors[j])
    return True



# CHECK ICH NICHT
def gaussian_elimination(A, b):
    A = np.array(A, dtype=float)  # Sicherstellen, dass A als float array vorliegt
    b = np.array(b, dtype=float)  # b ebenfalls als float array behandeln
    rows, cols = A.shape

    for i in range(min(rows, cols)):  # Gehe nur bis zur kleineren Dimension
        # Suche nach dem maximalen Wert in der aktuellen Spalte
        max_row = np.argmax(np.abs(A[i:, i])) + i

        # Vertausche die aktuelle Zeile mit der Zeile mit dem größten Wert
        if i != max_row:
            A[[i, max_row]] = A[[max_row, i]]
            b[[i, max_row]] = b[[max_row, i]]

        # Vermeide Division durch 0
        if A[i, i] == 0:
            continue

        # Setze die Werte unterhalb der Hauptdiagonale auf 0 (Elimination)
        for j in range(i + 1, rows):
            factor = A[j, i] / A[i, i]
            A[j, i:] -= factor * A[i, i:]  # Nur den relevanten Teil der Zeile bearbeiten
            b[j] -= factor * b[i]  # Passe die Lösung entsprechend an

    return A, b



def find_neighbors(row, col, board_size):
    return {(row + r, col + c) for r in range(-1, 2) for c in range(-1, 2)  # create a set out of the neighbors and return it
            if 0 <= (row + r) < board_size and 0 <= (col + c) < board_size}


# revealing cell
def reveal(row, col, board, board_size, revealed):
    # when clicked on a "0" --> reveal all adjacent "0"
    if board[row][col] == 0: # if it's a "0", reveal all adjacent "0"
        reveal_nums, checked_zeros = collect_connected_zero(row, col, board, board_size) # store all the cells that should be revealed into the tuples
        reveal_cells = reveal_nums.union(checked_zeros)
        for reveal_cell in reveal_cells:
            revealed.add(reveal_cell)
    else:
        revealed.add((row, col))


# collecting multiple "0" that are adjacent to each other and their adjacent numbers
def collect_connected_zero(row, col, board, board_size):
    checked_zeros = set()
    reveal_nums = set()
    queue = deque([(row, col)])    # if a NEW "0" is found, append it to this queue
        # --> using queue, popping elements is more efficient
    while queue:    # while queue is not empty
        r, c = queue.pop()  # take the last item (and remove it)
        for ar in range(-1, 2):  # check around the cell for other zeros
            for ac in range(-1, 2):
                if ar == 0 and ac == 0:  # if it checks the same field
                    continue
                if 0 <= (r + ar) < board_size and  0 <= (c + ac) < board_size:
                    if board[r + ar][c + ac] == 0 and (r + ar, c + ac) not in checked_zeros:  # if it's another new zero next to the current one
                        queue.append((r + ar, c + ac))  # if a "0" which has not been checked yet is found --> append it to the queue
                        checked_zeros.add((r + ar, c + ac)) # save all "0" that have already been checked or added to the queue
                    elif board[r + ar][c + ac] != 0:
                        reveal_nums.add((r + ar, c + ac))
                else:   # when out of range of the board
                    continue
    return reveal_nums, checked_zeros



def create_game(row, col, board_size, num_mines):
    trys = 0
    while True:
        trys += 1
        mines = set()
        revealed = set()
        board = [[0 for _ in range(board_size)] for _ in range(board_size)]

        create_mines((row - 1, row, row + 1),(col - 1, col, col + 1), board_size, mines, num_mines)
        create_board(board, board_size, mines)
        reveal(row, col, board, board_size, revealed)

        result = check_for_solvable(board, board_size, revealed, num_mines)
        if result:
            print(trys)
            return board, mines



# create mines
def create_mines(xrow, xcol, board_size, mines, num_mines):     # "xrow" and "xcol" are the cell that can't contain a mine (clicked cell + the 8 around it)
    while len(mines) < num_mines:
        row = random.randint(0, board_size - 1)
        col = random.randint(0, board_size - 1)
        # add "num_mines" amount of mines to the set
        if (row, col) not in mines and not (row in xrow and col in xcol): # if not already a mine cell or not in the locked cells
            mines.add((row, col))


# add all the mines to the board
def create_board(board, board_size, mines):
    for i in range(board_size):
        for j in range(board_size):
            if (i, j) in mines:    # if there should be a mine in that cell --> add mine
                board[i][j] = 9
            else:
                board[i][j] = 0
    calculate_board(board, board_size)



# calculate all the values for the board
def calculate_board(board, board_size):
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] == 9:  # for each bomb check all the 8 cells around it and count the mines
                for r in range(-1, 2, 1):
                    for c in range(-1, 2, 1):  # check the 8 cells around it
                        if r == 0 and c == 0:  # if it checks the same field
                            continue
                        if (col + c) < 0 or (col + c) > (board_size - 1) or (row + r) < 0 or (row + r) > (board_size - 1):
                            continue        # if out of range of the field
                        elif board[row + r][col + c] != 9:  # if it's not a bomb, increase the count by one
                            board[row + r][col + c] += 1
