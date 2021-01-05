import random

from API import MineSweeper


GEN_NUM = 10
PICK_TIME = 1
DIM_1 = 9
DIM_2 = 9
NMINES = 8


for _ in range(GEN_NUM):
    game = MineSweeper(DIM_1, DIM_2, NMINES)
    # Pick PICK_TIME times
    for i in range(PICK_TIME):
        x = random.randint(0, DIM_1-1)
        y = random.randint(0, DIM_2-1)
        # if picks a mine, pick another
        if game.mines[x, y] == 1:
            i = i - 1
            continue
        game.selectCell((x, y))
    print("* "*20)
    print(game.state)
    print("- "*20)
    print(game.mines)
