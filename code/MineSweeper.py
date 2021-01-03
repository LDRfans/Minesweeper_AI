"""
MineSweeper Game API.
You can play the game in terminal.
e.g. type 3, 0 to uncover the tile in Row_3, Col_0.
"""
LENGTH = 6
WIDTH = 6
NMINES = 7

MINE = -1
import numpy as np


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
        self.state = state
        self.edgeDict = dict()
        self.mines = list()
      
      # Update the state of the game  
      def stateUpdate(self, states):
        self.state = states
        for mine in self.mines:
          assert(np.isnan(self.state[mine[0], mine[1]]))
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
      

      def logicInference(self):
          
        
        
          


      # Update the self.edgeDict 
      def edgeDictUpdate(self):
        self.edgeDict = dict()
        for x in range(self.dim1):
          for y in range(self.dim2):
            if np.isnan(self.state[x,y]):
              continue
            neighbors = self.getNeighbors(x,y)
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
        selectCell = list()
        for key in self.edgeDict.keys():
          if self.state[key[0],key[1]] == self.mineCount(key):
            selectCell.append(self.edgeDict[key])
            return selectCell

      def basicRule3(self):
        
          



      # Count the marked mines around the coordinate
      def mineCount(self, coordinate):
        count = 0
        for nb in self.getNeighbors(coordinate):
          if self.state[nb[0],nb[1]] == MINE :
            count += 1
        return count
                  
          














if __name__ == "__main__":
    # Init the game
    game = MineSweeper()
    print("%dx%d Grid with %d Mines" % (game.dim1, game.dim2, game.nMines))
    # Play
    while True:
        print(game.state)
        if game.victory:
            print("You WIN!!!")
            break
        y, x = map(lambda var: int(var), input("(y, x) coordinate: ").split(","))
        game.selectCell((y, x))
        if game.gameOver:
            print("BOOM!!!")
            break
