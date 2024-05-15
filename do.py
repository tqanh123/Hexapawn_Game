
import time
from copy import deepcopy

import numpy as np
import streamlit as st
from streamlit import session_state
from util import to_string, to_tuple, Round, _BLACK, _KILL, _BLANK, _MOVES, _PLAYER_COLOR, _PLAYER_SYMBOL, _STAND, _WHITE

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
class Hexapawn():
    def __init__(self, players, size=(4, 4)) -> None:
        self.size = M, N = size
        # Initialize the game
        if "ROUND" not in session_state:
            session_state.ROUND = Round()
        p1, p2 =[], []
        for i, col in enumerate(session_state.ROUND.BOARD):
            for j, cell in enumerate(col):
                if (cell == _BLACK or cell == _KILL): p1.append((i, j))
                elif (cell == _WHITE or cell == _STAND): p2.append((i, j))
                
        p = [[(i, j) for j in range(N)] for i in [0, M - 1]]

        for i, d, goal, pawns in [(0, -1, 0, p2), (1, 1, M - 1, p1)]:
            players[i].direction = d
            players[i].goal_line = goal
            players[i].pawns = pawns


        self.players = players
        self.current_player = session_state.ROUND.PLAYER
        self.clicked_buttons = session_state.ROUND.MOVES
    

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
        session_state.ROUND.BOARD[ex, ey] = self.current_player
        session_state.ROUND.BOARD[bx][by] = _BLANK

        while ( session_state.ROUND.MOVES != []):
            session_state.ROUND.MOVES.pop()
            self.clicked_buttons.pop()


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
        if (session_state.ROUND.BOARD[x][y] == _MOVES or session_state.ROUND.BOARD[x][y] == _KILL):
            session_state.ROUND.MOVES.append((x, y))
            session_state.ROUND = deepcopy(session_state.ROUND)
            for i in range(self.size[0]):
                if session_state.ROUND.BOARD[x][i] == _MOVES:
                    session_state.ROUND.BOARD[x][i] = _BLANK
                elif session_state.ROUND.BOARD[x][i] == _KILL:
                    session_state.ROUND.BOARD[x][i] = self.opponent_index()
            self.clicked_buttons = session_state.ROUND.MOVES
            # print("handle_click _MOVES/KILL")

        elif (session_state.ROUND.WINNER == _BLANK and session_state.ROUND.BOARD[x][y] == self.current_player):
            session_state.ROUND = deepcopy(session_state.ROUND)
            session_state.ROUND.BOARD[x][y] = _STAND
            
            if (len(session_state.ROUND.MOVES) != 0):
                h = session_state.ROUND.MOVES.pop()
                session_state.ROUND.BOARD[h[0]][h[1]] = self.current_player
                k = h[0]+self.player().direction

                if (session_state.ROUND.BOARD[k][h[1]] == _MOVES):
                    session_state.ROUND.BOARD[k][h[1]] = _BLANK
                if (h[1] + 1 < self.size[0] and session_state.ROUND.BOARD[k][h[1] + 1] == _KILL):
                    session_state.ROUND.BOARD[k][h[1] + 1] = self.opponent_index()
                if (h[1] - 1 >= 0 and session_state.ROUND.BOARD[k][h[1] - 1] == _KILL):
                    session_state.ROUND.BOARD[k][h[1] - 1] = self.opponent_index()

            session_state.ROUND.MOVES.append((x,y))

            moves = self.pawn_moves(x, y)
            for cell in (moves):
                if session_state.ROUND.BOARD[cell[0]][cell[1]] != self.opponent_index():
                    session_state.ROUND.BOARD[cell[0]][cell[1]] = _MOVES
                else:
                    session_state.ROUND.BOARD[cell[0]][cell[1]] = _KILL

    
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

        history = []
        if verbose:
            self.show()

        while True:

            if self.is_over():
                self.draw_board(False)
                session_state.ROUND.WINNER = self.opponent_index()
                session_state.ROUND.SCORE = (
                    session_state.ROUND.SCORE[0]
                    + int(session_state.ROUND.WINNER == _WHITE),
                    session_state.ROUND.SCORE[1]
                    + int(session_state.ROUND.WINNER == _BLACK),
                )
                break
            else:
                self.draw_board(True)

            if (session_state.ROUND.PLAYER == _WHITE and len(self.clicked_buttons) != 2): break
            move = self.player().ask_move(self)
            history.append((deepcopy(self), move))
            self.make_move(move)
            self.update_BOARD(move)
            if verbose:
                print(
                    "\nMove #%d: player %d plays %s :"
                    % (session_state.ROUND.TURN, self.current_player, str(move))
                )
                MESSAGE.write(
                    "\nMove #%d: player %d plays %s :"
                    % (session_state.ROUND.TURN, self.current_player, str(move))
                )
                self.show()
            self.switch_player()
            session_state.ROUND.TURN += 1
        
        draw_info()
        game_control()
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
    session_state.ROUND.BOARD = np.array(
            [
                [2, 2, 2, 2],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 1],
            ],
            dtype = int
        )
    session_state.ROUND.PLAYER = _WHITE
    session_state.ROUND.WINNER = _BLANK
    session_state.ROUND.TURN = 1

# Infos
def draw_info() -> None:
        # Text information
        TITLE.subheader("**5️⃣ Gomoku Game in Streamlit**")
        
        GAME_INFO.markdown(
            """
            ---

            ## A simple Hexapawn game.


            <a href="https://en.wikipedia.org/wiki/Hexapawn" style="color:#FFFFFF">info about Hexapawn</a>

            - no restrictions
            - 4 by 4 board
            - no regrets

            Enjoy!

            ##### by <a href="https://github.com/tqanh123/Hexapawn_Game" style="color:#FFFFFF">TeddyHuang-00</a> • <a href="https://github.com/tqanh123/Hexapawn_Game" style="color:#FFFFFF">Github repo</a>

            ##### <a href="mailto:...." style="color:#FFFFFF">Contact</a>
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
    game = Hexapawn([Human_Player(),  AI_Player(ai)])

    # game.draw_info()
    # print("main")
    game.play()
