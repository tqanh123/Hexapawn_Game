from util import to_string

class Human_Player:
    def __init__(self, name="Human"):
        self.name = name

    def ask_move(self, game):
        # The str version of every move for comparison with the user input:
        # moveStr = "NO_MOVE_DECIDED_YET"
        # move = []
        # print("human move")
        # while True:
        #     if len(game.clicked_buttons) != 2:
        #         continue

        move = game.clicked_buttons
        print("ask_move")
        print(move)

        return to_string(move)


class AI_Player:
    def __init__(self, AI_algo, name="AI"):
        self.AI_algo = AI_algo
        self.name = name
        self.move = {}

    def ask_move(self, game):
        return self.AI_algo(game)