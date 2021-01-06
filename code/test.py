import random
from net import netPlayer, Net
from minesweeper_csp import *
from API import MineSweeper


DIM_1 = 9
DIM_2 = 9
NMINES = 10

TEST_ROUND = 100


winning_rate = 0

# Testing
print("Testing...")

for _ in range(TEST_ROUND):
    # New game
    game = MineSweeper(dim_1=DIM_1, dim_2=DIM_2, nMines=NMINES)
    game.selectCell((DIM_1 // 2, DIM_2 // 2))  # pick center as first
    # CSP
    while not game.gameOver:
        coordinate = cspPlayer(game)
        if not (coordinate[0] == -1 and coordinate[1] == -1):
            game.selectCell(coordinate)
        else:
            # x, y = netPlayer(game.state)
            # game.selectCell((x, y))
            while True:
                x = random.randint(0, game.dim1 - 1)
                y = random.randint(0, game.dim2 - 1)
                if np.isnan(game.state[x][y]):
                    break
            game.selectCell((x, y))
        if game.victory:
            winning_rate += 1

    # # CNN
    # while not game.gameOver:
    #     x, y = netPlayer(game.state)
    #     game.selectCell((x, y))
    #     if game.victory:
    #         winning_rate += 1

print("Winning rate:", winning_rate / TEST_ROUND)
