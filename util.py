import numpy as np
import time

class Round:
    def __init__(self) -> None:
        self.BOARD = np.array(
            [
                [2, 2, 2, 2],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 1],
            ],
            dtype = int
        )
        self.PLAYER = _WHITE
        self.TURN = self.PLAYER
        self.SCORE = (0, 0)
        self.HISTORY = []
        self.WINNER = _BLANK
        self.TIME = time.time()
        self.MOVES = []
    # def update_board(self, ex, ey, current_player):
    #     self.BOARD[ex][ey] = current_player

# --- Config ---
_BLANK = 0
_BLACK = 2
_WHITE = 1
_MOVE = 3
_PLAYER_SYMBOL = {
    _BLANK: "▭",
    _MOVE: "▬",
    _WHITE: "♙",
    _BLACK: "♟",
}
_PLAYER_COLOR = {
    _BLANK: "Blank",
    _WHITE: "White",
    _BLACK: "Black",
}

# Convert D7 to (3,6) and back...
to_string = lambda move: " ".join(
    ["ABCDEFGHIJ"[move[i][0]] + str(move[i][1] + 1) for i in (0, 1)]
)
to_tuple = lambda s: ("ABCDEFGHIJ".index(s[0]), int(s[1:]) - 1)
convert2 = lambda coord: (coord[2] - coord[0] - 1, coord[1])
convert = lambda coord: coord[1] - coord[0] - 1