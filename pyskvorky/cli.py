"""Get input arguments"""
from argparse import ArgumentParser


def get_cli_args():
    """Get input arguments"""
    parser = ArgumentParser(description="Unlimited Tic-Tac-Toe is a grown-up version of the classic 3x3 game, played by two players on an infinite two-dimensional board. Players try to place 5 consecutive markers in a row (vertical, horizontal or diagonal). The game starts by placing an X marker on any square, usually (0, 0), the 'center' of the infinite board. CONTROLS: arrows move the cursor, return enters player's move, escape quits the game. ALTERNATIVE CONTROLS: WASD as arrows, QEZX move the cursor diagonally, R back to the last move's position, C to the center of the field, space enters a move, shift-Q quits the game.", epilog="Enjoy!")

    parser.add_argument("-x", "--X_player", default="bot", metavar="<module name> or 'human'",
                        help="assign a player to X marker: default X player is 'bot'")
    parser.add_argument("-o", "--O_player", default="human", metavar="<module name> or 'human'",
                        help="assign a player to O marker: default O player is 'human'")
    parser.add_argument("-r", "--reverse", action="store_true",
                        help="reverse players; i.e. swap assignments to markers X and O")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="pause bot vs bot game after each move")
    parser.add_argument("-s", "--sleep", nargs="?", default=0, const=0.1, type=float, metavar="seconds",
                        help="run sleep timer after each move")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

    args = parser.parse_args()

    x_player = args.X_player
    o_player = args.O_player
    if args.reverse:
        x_player, o_player = o_player, x_player
    sleep_time = args.sleep
    step_moves = args.debug and (x_player != "human") and (o_player != "human")

    return x_player, o_player, sleep_time, step_moves
