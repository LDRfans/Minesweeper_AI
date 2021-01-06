"""
MineSweeper Game API.
You can play the game in terminal.
e.g. type 3, 0 to uncover the tile in Row_3, Col_0.
"""
LENGTH = 9
WIDTH = 9
NMINES = 10

LOGIC = 1
MINE = -1
nGames = 1000
import numpy as np
import random

# the "game board", with state
class MineSweeper:
    def __init__(self):
        # params
        self.dim1 = LENGTH
        self.dim2 = WIDTH
        self.totalCells = self.dim1 * self.dim2
        self.nMines = NMINES
        self.mines = np.zeros([self.dim1, self.dim2])
        self.neighbors = np.zeros([self.dim1, self.dim2])
        self.state = np.zeros([self.dim1, self.dim2])
        self.state.fill(np.nan)
        self.initialized = False
        self.gameOver = False
        self.victory = False
        self.step = 0

    def initialize(self, coordinates):  # not run until after first selection!
        # set up mines
        # randomly place mines anywhere *except* first selected location AND surrounding cells
        # so that first selection is always a 0
        # weird, yes, but that's how the original minesweeper worked
        availableCells = range(self.totalCells)
        selected = coordinates[0] * self.dim2 + coordinates[1]
        offLimits = np.array(
            [selected - self.dim2 - 1, selected - self.dim2, selected - self.dim2 + 1, selected - 1, selected,
             selected + 1, selected + self.dim2 - 1, selected + self.dim2,
             selected + self.dim2 + 1])  # out of bounds is ok
        availableCells = np.setdiff1d(availableCells, offLimits)
        self.nMines = np.minimum(self.nMines,
                                 len(availableCells))  # in case there are fewer remaining cells than mines to place
        minesFlattened = np.zeros([self.totalCells])
        minesFlattened[np.random.choice(availableCells, self.nMines, replace=False)] = 1
        self.mines = minesFlattened.reshape([self.dim1, self.dim2])
        # set up neighbors
        for i in range(self.dim1):
            for j in range(self.dim2):
                nNeighbors = 0
                for k in range(-1, 2):
                    if 0 <= i + k < self.dim1:
                        for l in range(-1, 2):
                            if 0 <= j + l < self.dim2 and (k != 0 or l != 0):
                                nNeighbors += self.mines[i + k, j + l]
                self.neighbors[i, j] = nNeighbors
        # done
        self.initialized = True

    def clearEmptyCell(self, coordinates):
        x = coordinates[0]
        y = coordinates[1]
        self.state[x, y] = self.neighbors[x, y]
        if self.state[x, y] == 0:
            for i in range(-1, 2):
                if 0 <= x + i < self.dim1:
                    for j in range(-1, 2):
                        if 0 <= y + j < self.dim2:
                            if np.isnan(self.state[x + i, y + j]):
                                self.clearEmptyCell((x + i, y + j))

    def selectCell(self, coordinates):
        self.step += 1
        if self.mines[coordinates[0], coordinates[1]] > 0:  # condition always fails on first selection
            self.gameOver = True
            self.victory = False
        else:
            if not self.initialized:  # runs after first selection
                self.initialize(coordinates)
            self.clearEmptyCell(coordinates)
            if np.sum(np.isnan(self.state)) == self.nMines:
                self.gameOver = True
                self.victory = True

class Logic_inference:
      def __init__(self, state):
        self.neighborSet = {}
        self.dim1 = LENGTH
        self.dim2 = WIDTH
        self.state = state.copy()
        self.edgeDict = dict()
        self.mines = list()
        self.selectCell = list()
      
      # Update the state of the game  
      def stateUpdate(self, states):
        self.state = states.copy()
        for mine in self.mines:
          #assert(np.isnan(self.state[mine[0], mine[1]]))
          self.state[mine[0], mine[1]] = MINE

      # Input a coordinate return a set contains (x,y) of the neighbors
      def getNeighbors(self, coordinate):
        x = coordinate [0]
        y = coordinate [1]
        neighbors = []
        for i in range(-1, 2):
          if 0 <= x + i < self.dim1: 
            for j in range(-1, 2):
              if 0 <= y + j < self.dim2 and (i * j + i + j) != 0:
                neighbors.append((x + i, y + j))
        return neighbors
      
 
      def logicInference(self,state):
        self.selectCell = list()
        self.stateUpdate(state)
        self.edgeDictUpdate()
        self.basicRule1()
        self.basicRule2()
        #self.basicRule3()
        self.selectCell = set(self.selectCell)
        self.selectCell = list(self.selectCell) 
        return self.selectCell
        
          


      # Update the self.edgeDict 
      def edgeDictUpdate(self):
        self.edgeDict = dict()
        for x in range(self.dim1):
          for y in range(self.dim2):
            if np.isnan(self.state[x,y]):
              continue
            neighbors = self.getNeighbors((x,y))
            nanSet = list()
            for nb in neighbors:
              if np.isnan(self.state[nb[0], nb[1]]):
                nanSet.append(nb)              
            if len(nanSet) != 0:
              self.edgeDict.update({(x, y): nanSet})

      def mineUpdate(self,coordinate):
        self.mines.append(coordinate)
        assert(np.isnan(self.state[coordinate[0], coordinate[1]]))
        self.state[coordinate[0], coordinate[1]] = MINE

      # Search the edgeDict to find the # uncover neighbors equals to the cell 
      def basicRule1(self):
        for key in self.edgeDict.keys():
          if self.state[key[0], key[1]] == (len(self.edgeDict[key]) + self.mineCount(key)):
            for item in self.edgeDict[key]:
              self.mineUpdate(item)

      
      def basicRule2(self):
        for key in self.edgeDict.keys():
          if self.state[key[0], key[1]] == self.mineCount(key):
            for cell in self.edgeDict[key]:
              if np.isnan(self.state[cell[0], cell[1]]):
                self.selectCell.append(cell)

      def basicRule3(self):
        keys = self.edgeDict.keys()
        for cell in keys:
          neighbors = self.getNeighbors(cell)
          for nb in neighbors:
            if self.state[cell[0], cell[1]] == self.state[nb[0], nb[1]] and nb in keys:
              if set_issubset(self.edgeDict[cell], self.edgeDict[nb]):
                diff = set_difference(self.edgeDict[cell], self.edgeDict[nb])
                self.selectCell.extend(diff)

      def basicRule4(self):
        keys = self.edgeDict.keys()
        for cell in keys:
          neighbors = self.getNeighbors(cell)
          




      # Count the marked mines around the coordinate
      def mineCount(self, coordinate):
        count = 0
        for nb in self.getNeighbors(coordinate):
          if self.state[nb[0], nb[1]] == MINE :
            count += 1
        return count

def set_difference(a,b):
  set_a = set(a)
  set_b = set(b)
  if set_a.issubset(set_b):
    return list(set_b - set_a)
  if set_b.issubset(set_a):
    return list(set_a - set_b)
    
def set_issubset(a, b):
  set_a = set(a)
  set_b = set(b)                  
  if set_a.issubset(set_b) or set_b.issubset(set_a):
    return True
  return False        

if __name__ == "__main__":
  result = list()
  win = 0
  for i in range(nGames):
    print(i)
    print("***********")
    game = MineSweeper()
    logic = Logic_inference(game.state)
    print("%dx%d Grid with %d Mines" % (game.dim1, game.dim2, game.nMines))
    func = LOGIC + 1
    while True:
      print(game.state)
      if game.victory:
        print("You WIN!!!")
        win += 1
        break

      
      #func = eval(input("Random choose:0, Logic inference:1  "))
      if func == LOGIC:
        selectCells = logic.logicInference(game.state)
        print(selectCells)
        if len(selectCells) == 0:
          print("random")
          while True:
            x = random.randint(0, game.dim1 - 1)
            y = random.randint(0, game.dim2 - 1)
            if np.isnan(game.state[x,y]):
              break
          game.selectCell((x,y))
        else:
          for item in selectCells:
            print("Logic",item)
            #print(game.state)
            x = item[0]
            y = item[1]
            game.selectCell((x,y))
            #print("****************")
            #print(game.state)
      else:
        print("random")
        x = random.randint(0, game.dim1 - 1)
        y = random.randint(0, game.dim2 - 1)
        game.selectCell((x,y))
      if game.gameOver and not game.victory:
        print("BOOM!!!")
        print(game.state)
        break
    result.append(game.step)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  print(result)
  print(sum(result) / nGames)
  print(win)









# 1000 9x9 10 MINES LOGIC 28.382
# 1000 9x9 10 MINES RANDOM 9.114
