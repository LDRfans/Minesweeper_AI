from net import netPlayer, Net
from API import MineSweeper


DIM_1 = 9
DIM_2 = 9
NMINES = 9


game = MineSweeper(dim_1=DIM_1, dim_2=DIM_2, nMines=NMINES)
game.selectCell((DIM_1 // 2, DIM_2 // 2))  # pick center as first

while not game.gameOver:
    x, y = netPlayer(game.state)
    print(x, y)
    game.selectCell((x, y))
    if game.victory == True:
        print("Win")
