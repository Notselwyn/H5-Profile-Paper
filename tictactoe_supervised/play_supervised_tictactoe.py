import pickle
import zmq


class Game:
    def __init__(self, board: list=[0]*9, model=None, lport=None, sport=None):
        self.original_board = board
        self.board = board
        self.model = model
        self.rpc_lport = lport
        self.rpc_sport = sport
        self.ask_index = 0
        self.last_cell = -1

        if model is None:
            if lport is None:
                self.ask_array = [self.ask_player_cell, self.ask_player_cell]
            else:
                self.ask_array = [self.ask_player_cell, self.ask_rpc_cell()]
        else:
            if lport is None:
                self.ask_array = [self.ask_player_cell, self.ask_model_cell]
            else:
                self.ask_array = [self.ask_model_cell, self.ask_rpc_cell]

        if self.rpc_lport is not None:
            self.rpc_scontext = zmq.Context()
            self.rpc_ssocket = self.rpc_scontext.socket(zmq.PUB)
            self.rpc_ssocket.connect(f"tcp://localhost:{sport}")

            self.rpc_lcontext = zmq.Context()
            self.rpc_lsocket = self.rpc_lcontext.socket(zmq.SUB)
            self.rpc_lsocket.bind(f"tcp://localhost:{lport}")

            print("sent pakket:", self.rpc_ssocket.send(b"INI"))
            print("touched down confirmed:", self.rpc_lsocket.recv())

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
            elif self.ask_array[i] == self.ask_rpc_cell:
                print(f"Player {i+1} is a RPC server")

    def ask_player_cell(self):
        cell = int(input("Choose a cell (1-9): "))-1
        while cell < 0 or cell > 8 or self.board[cell] != 0:
            print("Invalid cell!")
            cell = int(input("Choose a cell (1-9): "))-1
        self.last_cell = cell
        return self.last_cell

    def ask_model_cell(self):
        if self.model is not None:
            cell = self.model.predict([self.board])[0]
            if self.board[cell] != 0:
                print(f"The ML made a mistake by picking invalid cell {cell+1}")
                cell = self.model.predict([self.board])[0]
            print(f"The ML model picked cell {cell+1}")
        else:
            cell = int(input("Choose a cell (1-9): "))-1
        self.last_cell = cell
        return self.last_cell

    def ask_rpc_cell(self):
        self.rpc_socket.send(f"REQ,{self.last_cell}")
        self.last_cell = int(self.rpc_socket.recv())
        return self.last_cell

    def play(self):
        self.print_players()
        while True:
            print(self.__repr__())
            self.board[self.ask_array[self.ask_index]()] = 1
            self.ask_index = (self.ask_index + 1) % 2
            if (winner := self.get_winner()) != 0:
                break
            print(self.__repr__())
            self.board[self.ask_array[self.ask_index]()] = 2
            self.ask_index = (self.ask_index + 1) % 2
            if (winner := self.get_winner()) != 0:
                break

        print(self.__repr__())
        if self.rpc_port is not None:
            self.rpc_socket.send("RST")
        if winner == 3:
            print("It's a draw!")
        else:
            print(f"Player {winner} won!")

        if "n" not in input("Play again? [Y/n]: ").lower():
            self.reset()
            self.shuffle_ask_array()
            self.play()
        else:
            self.rpc_socket.send("EXT")



with open("supervised_tictactoe.pkl", "rb") as f:
    tictactoe_ml_model = pickle.load(f)

rpc_sport = None
rpc_lport = None
#if "y" in input("Do you want to run RPC for the C++ AI? [y/N]: ").lower():
#    rpc_sport = int(input("C++ RPC port (1-65535): "))
#    rpc_lport = int(input("Own listen port (1-65535): "))
rpc_sport = 12345
rpc_lport = 12346
Game(model=tictactoe_ml_model, lport=rpc_lport, sport=rpc_sport).play()