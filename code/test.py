import random
from net import netPlayer, Net
from minesweeper_csp import *
from API import MineSweeper
from MineSweeper import Logic_inference

DIM_1 = 16
DIM_2 = 16
NMINES = 40

TEST_ROUND = 1000

winning_rate = 0
nLogic = 0
nCSP = 0
nNet = 0


# Testing
print("Testing...")

for _ in range(TEST_ROUND):
    # New game
    print("Round:", _, "/", TEST_ROUND)
    game = MineSweeper(dim_1=DIM_1, dim_2=DIM_2, nMines=NMINES)
    game.selectCell((DIM_1 // 2, DIM_2 // 2))  # pick center as first
    # Logic
    logic = Logic_inference(game)
    while not game.gameOver:
        selectCells = logic.logicInference(game.state)
        if len(selectCells) != 0:
            for item in selectCells:
                x = item[0]
                y = item[1]
                game.selectCell((x,y))
                nLogic += 1
            if game.victory:
                winning_rate += 1
            continue
        # CSP
        coordinate = cspPlayer(game)
        if not (coordinate[0] == -1 and coordinate[1] == -1):
            game.selectCell(coordinate)
            nCSP += 1
        else:
            x, y = netPlayer(game.state)
            game.selectCell((x, y))
            nNet += 1
            # while True:
            #     x = random.randint(0, game.dim1 - 1)
            #     y = random.randint(0, game.dim2 - 1)
            #     if np.isnan(game.state[x][y]):
            #         break
            # game.selectCell((x, y))
        if game.victory:
            winning_rate += 1

    # # CNN
    # while not game.gameOver:
    #     x, y = netPlayer(game.state)
    #     game.selectCell((x, y))
    #     if game.victory:
    #         winning_rate += 1

print("Winning rate:", winning_rate / TEST_ROUND)
print(nLogic, nCSP, nNet)
