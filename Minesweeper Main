from collections import deque
from new_eval_board import create_game

import customtkinter
import random
import sys


class Minesweeper:
    def __init__(self, master):
        # variables
        self.master = master
        self.board_size = 10
        self.max_board_size = 20
        self.cell_size = int((588 / self.board_size))
        self.new_bord_size = self.board_size    # when the user changes the board size, save it and apply it after the current game
        self.num_mines = round((float(self.board_size) ** 2) * (0.13 + (0.004 * (self.board_size - 10))))
        self.first_click = True
        self.mines = set()  # set, so every index can only appear once + fast lookups
        self.board = [[0 for i in range(self.board_size)] for j in range(self.board_size)]  # first set to None
        self.buttons = [[None for i in range(self.board_size)] for j in range(self.board_size)] # first set to None
        self.game_state_title = None    # title which displays "You won!" or "You lost!"
        self.board_frame = None
        self.revealed = set()
        self.flags = set()
        self.save_colors = {} # for saving colors when changing between flags and revealing
        self.set_flags = False  # for toggling between setting flags and revealing cells
        self.options = [None for i in range(6)] # buttons for option like "Restart", "Solve", "Quit"
        # functions
        self.master.geometry("920x" + str(self.cell_size * self.board_size + 300))    # set the size of the window
        # self.master.geometry("920x888")
        self.create_gui()


    # restart the game --> delete the whole board with its values and draw a new one
    def restart_game(self):
        self.board_size = self.new_bord_size    # change the board size if the user changed it
        self.num_mines = round((float(self.board_size) ** 2) * (0.13 + (0.004 * (self.board_size - 10))))
        self.save_colors = {}

        # Resize window and cells
        self.cell_size = int((588 / self.board_size))
        self.master.geometry("920x" + str((round(self.cell_size / 10) * 10) * self.board_size + 300))

        # Reset game state
        self.game_end = False
        self.game_state_title.configure(text="")
        self.first_click = True # new board, so first click should be a "0" again
        self.mines.clear()  # delete all the mines
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)] # reset board values
        self.revealed.clear()
        self.flags.clear()

        # Clear existing buttons from the frame
        for row in self.buttons:
            for button in row:
                if button is not None:
                    button.destroy()  # Delete all the old buttons --> works with the command "destroy()"

        self.buttons = [[None for _ in range(self.board_size)] for _ in range(self.board_size)] # create board buttons
        self.draw_board()   # draw a new board into the already existing old frame

        # Toggle button to standard
        if self.set_flags:
            self.set_flags = not self.set_flags
            self.options[5].configure(text="Toggle (1)")


    # creates GUI --> Text, Buttons, Board
    def create_gui(self):
        self.game_state_title = customtkinter.CTkLabel(self.master, text="", font=("Helvetica", 28))
        self.game_state_title.pack(pady=15)
        self.create_board_gui()

        options_text = ("Restart", "Solve", "Quit", f"Difficulty: 0 - {self.max_board_size}", "Submit", "Toggle (1)")
        frame_options = customtkinter.CTkFrame(self.master, fg_color="#242424")
        frame_options.pack(padx=10, pady=40)
        for i in range(len(self.options)):
            if i != 3:
                option_button = customtkinter.CTkButton(frame_options, text=str(options_text[i]), font=("Helvetica", 18, "bold"),
                                                        height=40, width=180, corner_radius=20, text_color= "black",
                                                        command=lambda j=i: self.menu(j), fg_color="#4e7498")
            else:
                option_button = customtkinter.CTkEntry(frame_options, font=("Helvetica", 18, "bold"),
                                                       height=40, width=180, corner_radius=20, text_color= "#3c3c3c",
                                                       fg_color="#4e7498", placeholder_text=str(options_text[i]),
                                                       placeholder_text_color="#3c3c3c", border_color="#8c8c8c",
                                                       border_width=4)
            option_button.grid(row=int(i / 3), column=i % 3, padx=23, pady=(0, 30)) # only increases distance to the next element at the bottom
            self.options[i] = option_button


    # map the buttons "Restart", "Solve" and "Quit" to the actions
    def menu(self, index):
        # Restart
        if index == 0:
            self.restart_game()
        # Solve
        elif index == 1:
            if self.set_flags:  # set "set_flags" to disabled
                self.options[5].configure(text="Toggle (1)")
                self.set_flags = not self.set_flags
            # reveal all cells except mines
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if (r, c) in self.flags:
                        self.evaluate_flags(r, c)
                        self.flags.remove((r, c))  # for "Solve" we have to remove our already revealed flags, so the "X" get replaced by the numbers
                    if (r, c) not in self.mines:   # all cells without mines get revealed
                        self.reveal(r, c)
        # Submit button for custom difficulty
        elif index == 4:
            new_difficulty = self.options[3].get()
            self.options[4].focus_set() # set the focus on another widget, so the placeholder text gets shown again
            self.options[3].delete(0, customtkinter.END)  # clears the entry widget from index 0 to the end
            try:
                if 3 < int(new_difficulty) <= self.max_board_size:
                    self.new_bord_size = int(new_difficulty)
            except ValueError:
                pass
            if self.first_click and self.board_size != self.new_bord_size:  # when no move is done yet, but the board size was changed
                self.restart_game() # restart game instantly
        # Toggle
        if index == 5:
            symbol = {
                True  : "🚩",
                False : "1"
            }
            self.set_flags = not self.set_flags
            self.options[5].configure(text=f"Toggle ({symbol[self.set_flags]})")    # toggle symbol in the button
        # Quit
        elif index == 2:
            sys.exit()


    # display all the buttons for the board and map the click on them to a function
    def create_board_gui(self):
        self.board_frame = customtkinter.CTkFrame(self.master)  # create a frame --> with this the whole grid is centered
        self.board_frame.pack(padx=25, pady=0) # pack frame into the window

        # Configure grid rows and columns to expand evenly
        for i in range(self.board_size):
            self.board_frame.grid_rowconfigure(i, weight=1) # weight says how much space the content should take if the container gets bigger
            self.board_frame.grid_columnconfigure(i, weight=1)  # makes sure, every row and column gets the same amount of space in the frame

        self.draw_board()   # in a separate function, so when clicking "Restart" only the board gets drawn --> frame stays and does not get drawn again


    # draw the board in the frame
    def draw_board(self):
        colors = {      # different shades of blue for the board
            0 : "#356089",
            1 : "#4e7498",
            2 : "#1c4c7a",
        }
        for i in range(self.board_size):
            for j in range(self.board_size):
                cell_size = round(self.cell_size/10) * 10   # round to the next factor of 10
                button = customtkinter.CTkButton(self.board_frame, height=cell_size, width=cell_size,   # create a new button
                                                 hover_color= "#9aafc4", text="", corner_radius=0, fg_color=colors[random.randint(0,2)],
                                                 border_width=1, border_color="#242424",
                                                 font=("Helvetica", int(self.cell_size / 1.6), "bold"), text_color="black",
                                                 command= lambda row = i, col = j: self.reveal(row, col)) # add command when clicking on the button
                button.grid(row=i, column=j, padx=0, pady=0, sticky="nsew")    # pack the button into a grid --> specify row, columns and padx/pady
                self.buttons[i][j] = button # save the button, so we can map it to our button-values variable when clicking on it


    # create mines
    def create_mines(self, xrow, xcol):     # "xrow" and "xcol" are the cell that can't contain a mine (clicked cell + the 8 around it)
        while len(self.mines) < self.num_mines:
            row = random.randint(0, self.board_size - 1)
            col = random.randint(0, self.board_size - 1)
            # add "num_mines" amount of mines to the set
            if (row, col) not in self.mines and not (row in xrow and col in xcol): # if not already a mine cell or not in the locked cells
                self.mines.add((row, col))


    # add all the mines to the board
    def create_board(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                if (i, j) in self.mines:    # if there should be a mine in that cell --> add mine
                    self.board[i][j] = 9
                else:
                    self.board[i][j] = 0
        self.calculate_board()


    # calculate all the values for the board
    def calculate_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 9:  # for each bomb check all the 8 cells around it and count the mines
                    for r in range(-1, 2, 1):
                        for c in range(-1, 2, 1):  # check the 8 cells around it
                            if r == 0 and c == 0:  # if it checks the same field
                                continue
                            if (col + c) < 0 or (col + c) > (self.board_size - 1) or (row + r) < 0 or (row + r) > (self.board_size - 1):
                                continue        # if out of range of the field
                            elif self.board[row + r][col + c] != 9:  # if it's not a bomb, increase the count by one
                                self.board[row + r][col + c] += 1


    # reveal the value (by changing the text of the button) when clicking on one
    def reveal(self, row, col):
        # when user wants to set flags and not reveal fields
        if self.set_flags:
            self.set_or_remove_flag(row, col)
            return
        # when the first cell is clicked it should be a "0"
        if self.first_click:
            self.first_click_action(row, col)
        # when a flag is clicked or cell already revealed
        if (row, col) in self.flags:
            return
        elif (row, col) in self.revealed:
            return

        b_colors = {
            0 : "#ae937b",   # different shades of brown for the revealed board
            1 : "#a48972"
        }
        num_col = {
            0 : "black",     # colors for the numbers
            1 : "#1955b0",
            2 : "#c41ca9",
            3 : "#137623",
            4 : "#7a1435",
            5 : "#807815",
            6 : "#db0e76",
            7 : "#f2502d",
            8 : "#8f1109"
        }

        # when clicked on a mine
        if (row, col) in self.mines:   # if a mine is clicked and not marked with a flag
            self.you_lost() # player lost

        # when clicked on a "0" --> reveal all adjacent "0"
        elif self.board[row][col] == 0: # if it's a "0", reveal all adjacent "0"
            reveal_zeros = self.collect_connected_zero(row, col) # store all the cells that should be revealed into the tuples
            while reveal_zeros:
                r, c = reveal_zeros.pop() # reveal cells in the "connected_zero" tuple
                if (r, c) not in self.flags: # do not check, whether it's already in self.revealed --> faster, when we just add it twice
                    self.buttons[r][c].configure(fg_color=b_colors[(r + c) % 2], hover_color="#bbada0")  # alternating colors like a chess board
                    if self.board[r][c] != 0:
                        self.buttons[r][c].configure(text=str(self.board[r][c]), text_color=num_col[self.board[r][c]])
                    self.revealed.add((r, c))

        # if it's neither a mine ("9") nor a "0" (and not a flag)
        else:
            self.buttons[row][col].configure(text=str(self.board[row][col]), fg_color=b_colors[(row+col) % 2], hover_color="#bbada0",
                                             text_color = num_col[self.board[row][col]])
        # at this point, mark cell as revealed
        self.revealed.add((row, col)) # we already added the element if we clicked on a "0" --> then the set just doesn't add the element (no error)
        self.check_for_end()  # check whether the player has won


    # evaluate, whether the flags were set right or wrong
    def evaluate_flags(self, r, c):
        if (r, c) in self.flags and (r, c) not in self.mines:  # when found 🚩, but it's not on a cell with a mine
            self.buttons[r][c].configure(text="X", fg_color=self.save_colors[(r, c)], text_color="#d2122e")
        elif (r, c) in self.flags and (r, c) in self.mines:  # when found 🚩, and it actually is a cell with a mine
            self.buttons[r][c].configure(text="🚩", fg_color="#85d15c")


    # player lost
    def you_lost(self):
        self.game_state_title.configure(text="You Lost!", text_color="red")
        for r in range(self.board_size):  # disable all the board buttons and reveal all the other mines
            for c in range(self.board_size):
                if (r, c) in self.flags:  # when found a flag
                    self.evaluate_flags(r, c)
                elif (r, c) in self.mines:  # when found a mine --> can't be a flag, because we already dealt with them above
                    self.buttons[r][c].configure(text="💣", fg_color="#d2122e")  # reveal mine and mark cell red
                self.buttons[r][c].configure(hover=False, command=None)  # user has to click e.g. "Restart" --> buttons get renewed and work again


    # player won
    def you_won(self):
        self.game_state_title.configure(text="You Won!", text_color="lightgreen")
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r, c) in self.mines:
                    self.evaluate_flags(r, c)
                    self.buttons[r][c].configure(border_width=2, border_color="#d2122e")
                self.buttons[r][c].configure(hover=False, command=None)  # game ended, take away commands and stop changing the hover color


    # set or remove the flag in the selected cell
    def set_or_remove_flag(self, row, col):
        if (row, col) not in self.revealed and (row, col) not in self.flags:  # place or remove flag when clicking on the cell
            if (row, col) not in self.save_colors:  # save the color in that cell
                self.save_colors[(row, col)] = self.buttons[row][col].cget("fg_color")  # store color for the cell in the dict
            self.flags.add((row, col))
            self.buttons[row][col].configure(text="🚩", fg_color="#78b6c4")  # set flag in the window
        elif (row, col) in self.flags:
            self.flags.remove((row, col))
            self.buttons[row][col].configure(text="", fg_color=self.save_colors[(row, col)])  # remove flag


    # delete flags, create mines and board
    def first_click_action(self, row, col):
        for (r, c) in self.flags:  # delete all flags that were set before the first click
            self.buttons[r][c].configure(text="", fg_color=self.save_colors[(r, c)])
            self.flags.remove((r, c))
        self.first_click = False
        self.board, self.mines = create_game(row, col, self.board_size, self.num_mines)

    # check whether the player has won
    def check_for_end(self):
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (((r, c) not in self.revealed and (r, c) not in self.mines)  # when a cell which is not a mine is not revealed yet
                        or ((r, c) in self.revealed and (r, c) in self.mines)): # a mine was revealed
                    return      # player has not won (at least not yet)
        # when reaching this point, no empty cells are left which are not mines are left --> player has won
        self.you_won() # player won


    # if a "0" was found --> check whether other "0" are adjacent --> reveal everything around the "0" at once
    def collect_connected_zero(self, row, col):
        checked_zeros = set()
        reveal_cells = set()
        queue = deque([(row, col)])    # if a NEW "0" is found, append it to this queue
            # --> using queue, popping elements is more efficient
        while queue:    # while queue is not empty
            r, c = queue.pop()  # take the last item (and remove it)
            for ar in range(-1, 2):  # check around the cell for other zeros
                for ac in range(-1, 2):
                    if 0 <= (r + ar) < self.board_size and  0 <= (c + ac) < self.board_size:
                        if self.board[r + ar][c + ac] == 0 and (r + ar, c + ac) not in checked_zeros:  # if it's another new zero next to the current one
                            queue.append((r + ar, c + ac))  # if a "0" which has not been checked yet is found --> append it to the queue
                            checked_zeros.add((r + ar, c + ac)) # save all "0" that have already been checked or added to the queue
                        reveal_cells.add((r + ar, c + ac)) # it's faster, if we just add the element and let the set ignore duplicates
                    else:   # when out of range of the board
                        continue
        return reveal_cells


# System settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# root settings
root = customtkinter.CTk()
root.title("Minesweeper")

# start game
game = Minesweeper(root)

root.mainloop()
