import pickle

LOWERBOUND, EXACT, UPPERBOUND = -1, 0, 1
inf = float("infinity")


def negamax(game, depth, origDepth, scoring, alpha=+inf, beta=-inf, tt=None):
    alphaOrig = alpha

    # Is there a transposition table and is this game in it ?
    lookup = None if (tt is None) else tt.lookup(game)

    if lookup is not None:
        # The game has been visited in the past

        if lookup["depth"] >= depth:
            flag, value = lookup["flag"], lookup["value"]
            if flag == EXACT:
                if depth == origDepth:
                    game.ai_move = lookup["move"]
                return value
            elif flag == LOWERBOUND:
                alpha = max(alpha, value)
            elif flag == UPPERBOUND:
                beta = min(beta, value)

            if alpha >= beta:
                if depth == origDepth:
                    game.ai_move = lookup["move"]
                return value

    if (depth == 0) or game.is_over():
        # NOTE: the "depth" variable represents the depth left to recurse into,
        # so the smaller it is, the deeper we are in the negamax recursion.
        # Here we add 0.001 as a bonus to signify that victories in less turns
        # have more value than victories in many turns (and conversely, defeats
        # after many turns are preferred over defeats in less turns)
        return scoring(game) * (1 + 0.001 * depth)

    if lookup is not None:
        # Put the supposedly best move first in the list
        possible_moves = game.possible_moves()
        possible_moves.remove(lookup["move"])
        possible_moves = [lookup["move"]] + possible_moves

    else:

        possible_moves = game.possible_moves()

    state = game
    best_move = possible_moves[0]
    if depth == origDepth:
        state.ai_move = possible_moves[0]

    bestValue = -inf
    unmake_move = hasattr(state, "unmake_move")

    for move in possible_moves:

        if not unmake_move:
            game = state.copy()  # re-initialize move

        game.make_move(move)
        game.switch_player()

        move_alpha = -negamax(game, depth - 1, origDepth, scoring, -beta, -alpha, tt)

        if unmake_move:
            game.switch_player()
            game.unmake_move(move)

        # bestValue = max( bestValue,  move_alpha )
        if bestValue < move_alpha:
            bestValue = move_alpha
            best_move = move

        if alpha < move_alpha:
            alpha = move_alpha
            # best_move = move
            if depth == origDepth:
                state.ai_move = move
            if alpha >= beta:
                break

    if tt is not None:

        assert best_move in possible_moves
        tt.store(
            game=state,
            depth=depth,
            value=bestValue,
            move=best_move,
            flag=UPPERBOUND
            if (bestValue <= alphaOrig)
            else (LOWERBOUND if (bestValue >= beta) else EXACT),
        )

    return bestValue


class Negamax:
    def __init__(self, depth, scoring=None, win_score=+inf, tt=None):
        self.scoring = scoring
        self.depth = depth
        self.tt = tt
        self.win_score = win_score

    def __call__(self, game):
        """
        Returns the AI's best move given the current state of the game.
        """

        scoring = (
            self.scoring if self.scoring else (lambda g: g.scoring())
        )  # horrible hack

        self.alpha = negamax(
            game,
            self.depth,
            self.depth,
            scoring,
            -self.win_score,
            +self.win_score,
            self.tt,
        )
        return game.ai_move