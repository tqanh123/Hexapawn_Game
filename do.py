
import time
from copy import deepcopy

import numpy as np
import streamlit as st
from streamlit import session_state
from util import to_string, to_tuple, Round

# Page configuration
st.set_page_config(
    page_title="Gomoku Game",
    page_icon="5️⃣",
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug": "https://github.com/TeddyHuang-00/streamlit-gomoku/issues/new/choose",
        "Get Help": "https://discuss.streamlit.io/t/pvp-gomoku-game-in-streamlit/17403",
        "About": "Welcome to this web-based Gomoku game!\n\nHave any comment? Please let me know through [this post](https://discuss.streamlit.io/t/pvp-gomoku-game-in-streamlit/17403) or [issues](https://github.com/TeddyHuang-00/streamlit-gomoku/issues/new/choose)!\n\nIf you find this interesting, please leave a star in the [GitHub repo](https://github.com/TeddyHuang-00/streamlit-gomoku)",
    },
)


_BLANK = 0
_WHITE = 1
_BLACK = 2
_STAND = 3
_MOVES = 4
_KILL  = 5
_PLAYER_SYMBOL = {
    _BLANK: "➕",
    _WHITE: "⚪",
    _BLACK: "⚫",
    _STAND: "🔘",
    _MOVES: "🟡",
    _KILL : "🔴",

}
_PLAYER_COLOR = {
    _BLANK: "Blank",
    _WHITE: "White",
    _BLACK: "Black",
}

_ROUND_TIMEOUT = 300
_ROUND_COLOR = {
    False: _BLACK,
    True: _WHITE,
}
_ROUND_ANNOTATION = {
    False: "(Opponent)",
    True : "(You)",
}



# Main
TITLE = st.empty()
ROUND_INFO = st.empty()
MESSAGE = st.empty()
BOARD_PLATE = [
    [cell.empty() for cell in st.columns([1 for _ in range(4)])] for _ in range(4)
]
WAIT_FOR_OPPONENT = st.empty()

# Sidebar
SCORE_TAG = st.sidebar.empty()
SCORE_PLATE = st.sidebar.columns(2)
with st.sidebar.container():
    ANOTHER_ROUND = st.empty()
    RESTART = st.empty()
    EXIT = st.empty()
GAME_INFO = st.sidebar.container()

# Draw the board
class Hexpawn():
    def __init__(self, players, size=(4, 4)) -> None:
        self.size = M, N = size
        # Initialize the game
        if "ROUND" not in session_state:
            session_state.ROUND = Round()
        p1, p2 =[], []
        for i, col in enumerate(session_state.ROUND.BOARD):
            for j, cell in enumerate(col):
                if cell == _BLACK: p1.append((i, j))
                elif (cell == _WHITE or cell == _STAND): p2.append((i, j))
                
        p = [[(i, j) for j in range(N)] for i in [0, M - 1]]

        for i, d, goal, pawns in [(0, -1, 0, p2), (1, 1, M - 1, p1)]:
            players[i].direction = d
            players[i].goal_line = goal
            players[i].pawns = pawns


        self.players = players
        self.current_player = session_state.ROUND.PLAYER
        self.clicked_buttons = session_state.ROUND.MOVES
        print("init")
        print(self.clicked_buttons)
    

    def possible_moves(self):
        moves = []
        opponent_pawns = self.opponent().pawns
        d = self.player().direction
        for i, j in self.player().pawns:
            if (i + d, j) not in opponent_pawns:
                moves.append(((i, j), (i + d, j)))
            if (i + d, j + 1) in opponent_pawns:
                moves.append(((i, j), (i + d, j + 1)))
            if (i + d, j - 1) in opponent_pawns:
                moves.append(((i, j), (i + d, j - 1)))

        return list(map(to_string, [(i, j) for i, j in moves]))
    
    def pawn_moves(self, x, y):
        moves = []
        opponent_pawns = self.opponent().pawns
        d = self.player().direction

        if (x + d, y) not in opponent_pawns:
            moves.append((x + d, y))
        if (x + d, y + 1) in opponent_pawns:
            moves.append((x + d, y + 1))
        if (x + d, y - 1) in opponent_pawns:
            moves.append((x + d, y - 1))

        return moves
        # return moves

    def make_move(self, move):
        move = list(map(to_tuple, move.split(" "))) 
        ind = self.players[self.current_player - 1].pawns.index(move[0])
        self.player().pawns[ind] = move[1]

        if move[1] in self.opponent().pawns:
            self.opponent().pawns.remove(move[1])

    def update_BOARD(self, move):
        move = list(map(to_tuple, move.split(" ")))

        bx = int(move[0][0])
        by = int(move[0][1])
        ex = int(move[1][0])
        ey = int(move[1][1])
        session_state.ROUND = deepcopy(session_state.ROUND)
        # session_state.ROUND.update_board(ex, ey, self.current_player)
        session_state.ROUND.BOARD[ex, ey] = self.current_player
        session_state.ROUND.BOARD[bx][by] = 0

        while ( session_state.ROUND.MOVES != []):
            session_state.ROUND.MOVES.pop()
            self.clicked_buttons.pop()
        print("update_BOARD")
        print(session_state.ROUND.MOVES)
        print(session_state.ROUND.BOARD)
        # self.draw_board(True)


    # Check if winner emerge from move
    def check_win(self) -> int:
        if self.lose():
            winner = self.opponent_index()
        return winner
    
    def lose(self):
        return any([i == self.opponent().goal_line for i, j in self.opponent().pawns]) or (
            self.possible_moves() == []
        )

    def is_over(self):
        return self.lose()
    
    def opponent_index(self):
        return 2 if (self.current_player == 1) else 1

    def player(self):
        return self.players[self.current_player - 1]

    def opponent(self):
        return self.players[self.opponent_index() - 1]

    def switch_player(self):
        self.current_player = self.opponent_index()
        session_state.ROUND.PLAYER = self.current_player
    
    def copy(self):
        return deepcopy(self)

    def get_move(self):
        return self.player.ask_move(self)

    def play_move(self, move):
        result = self.make_move(move)
        self.switch_player()
        return result

    def show(self):
        f = (
            lambda x: "1"
            if x in self.players[0].pawns
            else ("2" if x in self.players[1].pawns else ".")
        )
        print(
            "\n"
            .join(
                [
                    " ".join([f((i, j)) for j in range(self.size[1])])
                    for i in range(self.size[0])
                ]
            )
        )

    # Triggers the board response on click
    def handle_click(self, x, y):
        if session_state.ROUND.BOARD[x][y] == (_BLANK or _STAND or self.opponent_index()):
            pass

        elif session_state.ROUND.BOARD[x][y] == (_MOVES or _KILL):
            session_state.ROUND.MOVES.append((x, y))
            session_state.ROUND = deepcopy(session_state.ROUND)
            for i in range(self.size[0]):
                if session_state.ROUND.BOARD[x][y] == _MOVES:
                    session_state.ROUND.BOARD[x][y] = _BLANK
            self.clicked_buttons = session_state.ROUND.MOVES

        elif session_state.ROUND.WINNER == _BLANK:
            session_state.ROUND = deepcopy(session_state.ROUND)
            session_state.ROUND.BOARD[x][y] = _STAND
            
            if (len(session_state.ROUND.MOVES) != 0):
                while session_state.ROUND.MOVES != []:
                    x = session_state.ROUND.MOVES.pop()
                    session_state.ROUND.BOARD[x[0]][x[1]] = _BLANK

            session_state.ROUND.MOVES.append((x,y))
            moves = self.pawn_moves(x, y)
            # print(moves)
            for cell in (moves):
                session_state.ROUND.BOARD[cell[0]][cell[1]] = _MOVES
        
        print("handle_click")
        # print(self.clicked_buttons)
        # print(session_state.ROUND.MOVES)
        print(session_state.ROUND.BOARD)
    
    # Draw board
    def draw_board(self, response: bool):
        unique_id = time.time()
        if response:
            for i, row in enumerate(session_state.ROUND.BOARD):
                for j, cell in enumerate(row):
                    BOARD_PLATE[i][j].button(
                        _PLAYER_SYMBOL[cell],
                        key=f"{i}:{j}:{unique_id}",
                        on_click=self.handle_click,
                        args=(i, j),
                    )
        else:
            for i, row in enumerate(session_state.ROUND.BOARD):
                for j, cell in enumerate(row):
                    BOARD_PLATE[i][j].write(
                        _PLAYER_SYMBOL[cell],
                        key=f"{i}:{j}:{unique_id}",
                    )

    # Game process control
    def play(self, nmoves=1000, verbose=True):
        draw_info()
        game_control()

        history = []
        if verbose:
            self.show()
            # self.draw_board(True)

        for self.nmove in range(1, nmoves + 1):

            if self.is_over():
                self.draw_board(False)
                session_state.ROOM.WINNER = session_state.ROOM.PLAYER
                session_state.ROOM.SCORE = (
                    session_state.ROOM.SCORE[0]
                    + int(session_state.ROOM.WINNER == _WHITE),
                    session_state.ROOM.SCORE[1]
                    + int(session_state.ROOM.WINNER == _BLACK),
                )
                break
            else:
                self.draw_board(True)
            if (session_state.ROUND.PLAYER == _WHITE):
                while (len(self.clicked_buttons) != 2): ok = 1
            move = self.player().ask_move(self)
            history.append((deepcopy(self), move))
            self.make_move(move)
            self.update_BOARD(move)
            print("updated")
            if verbose:
                print(
                    "\nMove #%d: player %d plays %s :"
                    % (self.nmove, self.current_player, str(move))
                )
                self.show()

            self.switch_player()
            self.draw_board(True)

        history.append(deepcopy(self))

        return history
    
def game_control():
    if (session_state.ROUND.WINNER != _BLANK):
        ANOTHER_ROUND.button(
            "Another round",
            on_click=another_round,
            help="Clear board and swap first player",
        )

    RESTART.button(
        "Restart",
        on_click=restart,
        help="Clear the board as well as the scores",
    )
        
# Restart the game
def restart() -> None:
    session_state.ROUND = Round()

# Continue new round
def another_round() -> None:
    session_state.ROUND = deepcopy(session_state.ROUND)
    session_state.ROUND.BOARD = np.zeros(shape=(4, 4), dtype=int)
    session_state.ROUND.PLAYER = -session_state.ROUND.PLAYER
    game.current_player = session_state.ROUND.PLAYER
    session_state.ROUND.WINNER = _BLANK

# Infos
def draw_info() -> None:
        # Text information
        TITLE.subheader("**5️⃣ Gomoku Game in Streamlit**")
        
        GAME_INFO.markdown(
            """
            ---

            ## A simple Gomoku game.


            <a href="https://en.wikipedia.org/wiki/Gomoku#Freestyle_Gomoku" style="color:#FFFFFF">Freestyle Gomoku</a>

            - no restrictions
            - swap first player
            - 5 by 5 board
            - no regrets

            Enjoy!

            ##### by <a href="https://github.com/TeddyHuang-00" style="color:#FFFFFF">TeddyHuang-00</a> • <a href="https://github.com/TeddyHuang-00/streamlit-gomoku" style="color:#FFFFFF">Github repo</a>

            ##### <a href="mailto:huang_nan_2019@pku.edu.cn" style="color:#FFFFFF">Contact</a>
            """,
            unsafe_allow_html=True,
        )
        # History scores
        SCORE_TAG.subheader("Scores")
        SCORE_PLATE[0].metric("White", session_state.ROUND.SCORE[0])
        SCORE_PLATE[1].metric("Black", session_state.ROUND.SCORE[1])
        # Additional information
        if session_state.ROUND.WINNER != _BLANK:
            ROUND_INFO.write(
                f"#### **{_PLAYER_COLOR[session_state.ROUND.WINNER]} wins!**"
            )
        else:
            ROUND_INFO.write(
                f"#### **{_PLAYER_SYMBOL[session_state.ROUND.PLAYER]} {_PLAYER_COLOR[session_state.ROUND.PLAYER]}'s turn...**"
            )

if __name__ == "__main__":
    from players import AI_Player, Human_Player
    from NegaMax import Negamax
    scoring = lambda game: -100 if game.lose() else 0
    ai = Negamax(10, scoring)
    game = Hexpawn([Human_Player(),  AI_Player(ai)])

    # game.draw_info()
    # print("main")
    game.play()
