import string


# ---------- Class InitGame ----------


class InitGame:
    def __init__(self):
        self.board_dimensions = self.set_board_dimensions()
        self.knight_cords = self.set_knight_cords()
        self.is_human = self.set_player()

    def set_board_dimensions(self):
        while True:
            try:
                user_input = input("Enter your board dimensions: ").split()
                col, row = map(int, user_input)
                if row < 1 or col < 1:
                    raise ValueError
                return {"row": row, "column": col}
            except ValueError:
                print("Invalid dimensions!")

    def set_knight_cords(self):
        while True:
            try:
                input_str = input("Enter the knight's starting position: ").split()
                x, y = map(int, input_str)
                if not (1 <= x <= self.board_dimensions["column"]
                        and 1 <= y <= self.board_dimensions["row"]):
                    raise ValueError
                return {"column": x, "row": y}
            except ValueError:
                print("Invalid position!")

    def set_player(self):
        while True:
            answer = input("Do you want to try the puzzle? (y/n): ")
            if answer not in ("y", "n"):
                print("Invalid input!")
                continue
            return answer == "y"


# ---------- Class Board ----------


class Board:
    def __init__(self, init_game):
        self.visited_cells = 0
        self.size = {
            "column": init_game.board_dimensions["column"],
            "row": init_game.board_dimensions["row"]
        }
        self.total_cells = self.size["column"] * self.size["row"]
        self.state = self.zero_state()

    def zero_state(self):
        return [[0 for _ in range(self.size["column"])]
                for _ in range(self.size["row"])]

    def get_cell(self, x, y):
        return self.state[y][x]

    def set_cell(self, x, y, value):
        self.state[y][x] = value


# ---------- Class Knight ----------


class Knight:
    def __init__(self, init_game):
        self.cords = {
            "column": init_game.knight_cords["column"] - 1,
            "row": init_game.board_dimensions["row"]
            - init_game.knight_cords["row"]
        }
        self.moves = [(2, 1), (1, 2),
                      (-2, 1), (-1, 2),
                      (-2, -1), (-1, -2),
                      (2, -1), (1, -2)]

    def set_cords(self, x, y):
        self.cords["column"] = x
        self.cords["row"] = y


# ---------- Class Game ----------


class Game:
    def __init__(self):
        self.possible_moves = ()
        self.init_game = InitGame()
        self.board = Board(self.init_game)
        self.knight = Knight(self.init_game)
        self.player = self.init_game.is_human
        self.display = Display(self)

    def game_start(self):
        # Start the game with the knight's starting position
        start_pos = (self.knight.cords["column"], self.knight.cords["row"])
        self.board.visited_cells += 1
        self.board.set_cell(*start_pos, self.board.visited_cells)

        # Find the possible moves from the starting position and make the bot's work
        possible_moves = self._find_possible_moves(start_pos)
        bot_result = self._bot_turn(possible_moves)

        # If there's no solution, end the game
        if not bot_result:
            print("No solution exists!")
            exit()

        if self.player:
            # Reset the board and visited cells for the player's turn
            self.board.state = self.board.zero_state()
            self.board.visited_cells = 0
            self.possible_moves = possible_moves
            self._players_turn()
        else:
            # If the bot found a solution, display the final state of the board
            print("Here's the solution!")
            self.display_state()

    def _bot_turn(self, moves_list):
        # We check if the steps have run out, if a solution has been found
        if not moves_list:
            return self.board.visited_cells == self.board.total_cells

        # Take the first possible step and try to find a solution from it
        x, y = moves_list[0]
        self.board.visited_cells += 1
        self.board.set_cell(x, y, self.board.visited_cells)

        # Return True if solution has been found
        if self._bot_turn(self._find_possible_moves((x, y))):
            return True

        # If no solution is found, return board state
        # and repeat with the remaining steps
        self.board.set_cell(x, y, 0)
        self.board.visited_cells -= 1
        return self._bot_turn(moves_list[1:])

    def _players_turn(self):
        # Start turn with the knight's starting position
        self.board.set_cell(self.knight.cords["column"], self.knight.cords["row"], "X")
        self.board.visited_cells = 1

        # We calculate how many possible steps there are
        # from positions where the knight can go
        self.count_possible_moves(self.possible_moves)
        self.display_state()

        # Start the player's turn
        while True:
            # If there are no more possible moves,
            # check if the player has gone through all the cells of the board
            # and end the game
            if not self.possible_moves:
                if self.board.visited_cells == self.board.total_cells:
                    print("What a great tour! Congratulations!")
                else:
                    print("No more possible moves!")
                    print(f"Your knight visited {self.board.visited_cells} squares!")
                exit()

            # Mark the previous step as visited
            self.board.set_cell(self.knight.cords["column"],
                                self.knight.cords["row"], "*")

            # Ask the player for a new move and move the knight there
            x, y = self._get_next_move()
            self.knight.set_cords(x, y)
            self.board.set_cell(self.knight.cords["column"], self.knight.cords["row"], "X")
            self.board.visited_cells += 1

            # We remove the calculations of possible steps from the previous move
            # and recalculate them with the new coordinates of the knight
            self.undo_previous_possible_moves()
            self.possible_moves = self._find_possible_moves((x, y))
            self.count_possible_moves(self.possible_moves)

            self.display_state()

    def undo_previous_possible_moves(self):
        for x, y in self.possible_moves:
            if self.board.get_cell(x, y) in ("X", "*"):
                continue
            self.board.set_cell(x, y, 0)

    def _get_next_move(self):
        while True:
            try:
                input_str = input("Enter your next move: ").split()
                x, y = map(int, input_str)
                if not (1 <= x <= self.board.size["column"]
                        and 1 <= y <= self.board.size["row"]):
                    raise ValueError
                x -= 1
                y = self.board.size["row"] - y
                if (x, y) not in self.possible_moves:
                    raise ValueError
                return x, y
            except ValueError:
                print("Invalid move!", end="")

    def _find_possible_moves(self, cords):
        possible_moves = []
        for x, y in self.knight.moves:
            x += cords[0]
            y += cords[1]
            if 0 <= x < self.board.size["column"] \
                    and 0 <= y < self.board.size["row"] \
                    and self.board.get_cell(x, y) == 0:
                possible_moves.append((x, y))
        return possible_moves

    def count_possible_moves(self, cords_list):
        if cords_list:
            cords = cords_list[0]
            n = len(self._find_possible_moves(cords))
            self.board.set_cell(cords[0], cords[1], str(n))
            self.count_possible_moves(cords_list[1:])

    def display_state(self):
        self.display.display_board(self)


# ---------- Class Display ----------


class Display:
    row_border_t = string.Template("$line_number| $line |")

    def __init__(self, game):
        # determine the size of one cell
        self.cell_size = len(str(game.board.total_cells))

        # determine the width of row number
        self.row_num_size = len(str(game.board.size["row"]))

        # create final line with column numbers
        column_num_line = " ".join([f"{number + 1:>{self.cell_size}d}"
                                    for number in range(game.board.size["column"])])
        self.board_final_line = " " * (self.row_num_size + 2) + column_num_line

        # create vertical and horizontal borderline
        border_text = self.row_border_t.substitute(line_number=game.board.size['row'],
                                                   line=column_num_line)
        between_border_width = len(border_text) - self.row_num_size
        self.border = " " * self.row_num_size + "-" * between_border_width

    def display_cell(self, sign=None):
        if sign:
            return " " * (self.cell_size - len(sign)) + sign
        else:
            return "_" * self.cell_size

    def display_board(self, game):
        print(self.border)
        row_number = game.board.size["row"]

        for i in range(len(game.board.state)):
            line = []
            for n in game.board.state[i]:
                if n == 0:
                    line.append(self.display_cell())
                else:
                    line.append(self.display_cell(str(n)))
            row_number_display = f"{row_number:>{self.row_num_size}d}"
            print(self.row_border_t.substitute(line_number=row_number_display,
                                               line=" ".join(line)))
            row_number -= 1

        print(self.border)
        print(self.board_final_line)


# ---------- Start script ----------


def main():
    game = Game()
    game.game_start()


if __name__ == "__main__":
    main()
