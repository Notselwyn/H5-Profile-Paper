import pickle


class Game:
    def __init__(self, board: list=[0]*9, model=None, dataset=None, gather_stats=False):
        self.original_board = board
        self.board = board
        self.model = model
        self.dataset = dataset
        self.ask_index = 0
        self.last_cell = -1
        self.gather_stats = gather_stats
        self.print = print

        if self.gather_stats:
            self.print = lambda *arg, end=None: None

        if model is None:
            if dataset is None:
                self.ask_array = [self.ask_player_cell, self.ask_player_cell]
            else:
                self.ask_array = [self.ask_player_cell, self.ask_dataset_cell]
        else:
            if dataset is None:
                self.ask_array = [self.ask_player_cell, self.ask_model_cell]
            else:
                self.ask_array = [self.ask_model_cell, self.ask_dataset_cell]
                #self.ask_array = [self.ask_dataset_cell, self.ask_model_cell]

    def __repr__(self):
        st = ""
        for p, i in enumerate(self.board):
            if p % 3 == 0 and p != 0:
                st += "\n"
            st += str(i) + " "
        return st

    def reset(self):
        self.board = self.original_board
        self.ask_index = 0
        self.last_cell = -1

    def shuffle_ask_array(self):
        self.ask_array = self.ask_array[::-1]

    def get_winner(self):
        for i in (1, 2):  # bless github copilot rofl
            for j in range(3):
                if self.board[j] == i and self.board[j + 3] == i and self.board[j + 6] == i:  # horizontal
                    return i
                if self.board[j * 3] == i and self.board[j * 3 + 1] == i and self.board[j * 3 + 2] == i:  # vertical
                    return i
            if self.board[0] == i and self.board[4] == i and self.board[8] == i:  # diagonal
                return i
            if self.board[2] == i and self.board[4] == i and self.board[6] == i:  # diagonal
                return i
        if self.board.count(0) == 0:
            return 3
        return 0

    def print_players(self):
        for i in range(len(self.ask_array)):
            if self.ask_array[i] == self.ask_player_cell:
                print(f"Player {i+1} is a human")
            elif self.ask_array[i] == self.ask_model_cell:
                print(f"Player {i+1} is a ML model")
            elif self.ask_array[i] == self.ask_dataset_cell:
                print(f"Player {i+1} is a dataset")

    def ask_player_cell(self):
        cell = int(input("Choose a cell (1-9): "))-1
        while cell < 0 or cell > 8 or self.board[cell] != 0:
            self.print("Invalid cell!")
            cell = int(input("Choose a cell (1-9): "))-1
        self.last_cell = cell
        return self.last_cell

    def ask_model_cell(self):
        cell = self.model.predict([self.board])[0]
        if cell < 0:
            return cell
        if self.board[cell] != 0:
            self.print(f"The ML made a mistake by picking invalid cell {cell+1}")
            cell = self.model.predict([self.board])[0]
        self.print(f"The ML model picked cell {cell+1}")
        self.last_cell = cell
        return self.last_cell

    def ask_dataset_cell(self):
        s = 0
        for p, x in enumerate(self.board):
            s += x * (3 ** p)+1
        with open(self.dataset) as f:
            best = int(f.readlines()[s].split(",")[1])
        self.print(f"The dataset picked cell {best+1}")
        self.last_cell = best
        return best

    def play(self):
        if not self.gather_stats:
            self.print_players()
        if self.gather_stats:
            self.board = [2 if x == 1 else 1 if x == 2 else x for x in self.board]
        while True:
            self.print(self.__repr__())
            ncell = self.ask_array[self.ask_index]()
            if ncell < 0:
                self.print(f"Player {self.ask_index+1} capitalized because it thought the game would end in ", end="")
                if ncell == -2:
                    self.print("a win")
                elif ncell == -3:
                    self.print("a loss")
                elif ncell == -4:
                    self.print("a draw")
                else:
                    self.print("an invalid state")
                winner = ncell
                break

            self.board[ncell] = self.ask_index+1
            self.ask_index = (self.ask_index + 1) % 2
            if (winner := self.get_winner()) != 0:
                break

        if not self.gather_stats:
            self.print(self.__repr__())
            if winner == 3:
                self.print("It's a draw!")
            elif winner != 0:
                self.print(f"Player {winner} won!")

        if self.gather_stats:
            return winner
        elif "n" not in input("Play again? [Y/n]: ").lower():
            self.reset()
            self.shuffle_ask_array()
            self.play()

    def stats(self):
        with open(self.dataset) as f:
            lines = f.readlines()[1:]

        results = {}
        i = 0
        self.print_players()
        for l in lines:
            self.board = [int(x) for x in l.split(",")[0]]
            if self.get_winner() == 0:
                r = self.play()
                if r not in results:
                    results[r] = 0
                results[r] += 1
                if i % 50 == 0:
                    print(results)
                i += 1


with open("supervised_tictactoe.pkl", "rb") as f:
    tictactoe_ml_model = pickle.load(f)

Game(model=tictactoe_ml_model, dataset="../tictactoe_dataset.csv", gather_stats=True).stats()
#Game(model=tictactoe_ml_model).play()