import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
torch.set_default_tensor_type(torch.DoubleTensor)

from API import MineSweeper, dataGenerator


TRAINING_ROUND = 100
BATCH_SIZE = 20
TRAIN_SIZE = 100
TEST_SIZE = 20

DIM_1 = 9
DIM_2 = 9
NMINES = 8
PICK_TIME = 1

EMPTY = 0.0
COVERED = -1.0
MINE = -2.0


class mineDataset(Dataset):
    def __init__(self, size, picks, dim_1, dim_2, nMines):
        super(mineDataset, self).__init__()
        self.state, self.mine = dataGenerator(dataSize=size, pickTime=picks, dim_1=dim_1, dim_2=dim_2, nMine=nMines)
        self.state = np.array(self.state)[:, None, :, :]
        self.mine = np.array(self.mine)[:, None, :, :]

    def __getitem__(self, index):
        return self.state[index], self.mine[index]

    def __len__(self):
        return len(self.state)


def getMState(map):
    mState = map
    for row in range(DIM_1):
        for col in range(DIM_2):
            if mState[row, col] == np.nan:
                mState[row, col] = COVERED
    return mState


def getMMineMap(map):
    mMineMap = map
    for row in range(DIM_1):
        for col in range(DIM_2):
            if mMineMap[row, col] == 1:
                mMineMap[row, col] = MINE
    return mMineMap


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # 1 input image channel, 6 output channels, 3x3 square convolution
        # kernel
        self.conv1 = nn.Conv2d(1, 6, 3, padding=1)
        self.conv2 = nn.Conv2d(6, 16, 3, padding=1)
        # an affine operation: y = Wx + b
        self.fc1 = nn.Linear(16 * DIM_1 * DIM_2, 120)  # 6*6 from image dimension
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, DIM_1 * DIM_2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(BATCH_SIZE, -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


if __name__ == "__main__":

    # Load dataset
    print("Generating Mines...")
    trainingData = mineDataset(size=TRAIN_SIZE, picks=PICK_TIME, dim_1=DIM_1, dim_2=DIM_2, nMines=NMINES)
    testingData = mineDataset(size=TEST_SIZE, picks=PICK_TIME, dim_1=DIM_1, dim_2=DIM_2, nMines=NMINES)
    dataloaderTrain = DataLoader(trainingData, BATCH_SIZE, shuffle=True)
    dataloaderTest = DataLoader(testingData, BATCH_SIZE, shuffle=True)

    # Set the net
    net = Net()

    # Loss function
    criterion = nn.MSELoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    # Training
    print("--- Training Start ---")
    for epoch in range(TRAINING_ROUND):
        loss = 0.0
        for i, data in enumerate(dataloaderTrain):
            state, mineMap = data
            print(state)
            exit()
            optimizer.zero_grad()  # grad = 0
            outputs = net(state)  # forward output
            loss = criterion(outputs, mineMap.view(BATCH_SIZE, -1))  # calculate loss
            loss.backward()  # backward gradient propagation
            optimizer.step()  # optimize using grad

        # Validation test
        validationLoss = 0
        with torch.no_grad():
            for data in dataloaderTest:
                state, mineMap = data
                # predict
                outputs = net(state)
                # print(outputs[0])
                # print(mineMap.view(BATCH_SIZE, -1)[0])
                # exit()
                validationLoss += criterion(outputs, mineMap.view(BATCH_SIZE, -1))
        print(validationLoss)
        # print('[Epoch %d] validationLoss: %d' % (epoch + 1, validationLoss))
    print("--- Training Done ---")





    # # Set the game
    # mState = np.zeros((DIM_1, DIM_2))     # state
    # mProbMap = np.zeros((DIM_1, DIM_2))   # predict mine probability map
    # mMineMap = np.zeros((DIM_1, DIM_2))   # true mine map
    # mEdge = np.zeros((DIM_1, DIM_2))      # edge matrix: define edge tiles
    #
    # # Training
    # for _ in range(TRAINING_ROUND):
    #     # Net setup
    #     loss = 0.0
    #     # start the game
    #     game = MineSweeper()
    #     # First pick: start from center to get more information
    #     game.selectCell((DIM_1//2, DIM_2//2))
    #     mMineMap = game.mines   # mines were generated after first click!
    #     # mMineMap = getMMineMap(game.mines)
    #     while not game.gameOver:
    #         # Set mState
    #         mState = getMState(game.state)
    #         # Get input and truth
    #         input, truth = mState, mMineMap
    #         print(input)
    #         print("="*30)
    #         print(truth)
    #         exit()
