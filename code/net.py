import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

torch.set_default_tensor_type(torch.DoubleTensor)

from API import MineSweeper, dataGenerator

IS_TRAIN = 0
IS_PLAY = 0
IS_TEST = 1
TRAINING_ROUND = 400
TESTING_ROUND = 1000
BATCH_SIZE = 40
TRAIN_SIZE = 6000
TEST_SIZE = 600
LR = 0.05
ZOOM_FACTOR = 1
MODEL_PATH = '../model/net_9.pkl'

DIM_1 = 9
DIM_2 = 9
NMINES = 9
PICK_TIME = 7

EMPTY = 0.0
COVERED = -1.0
MINE = -2.0


class mineDataset(Dataset):
    def __init__(self, size, picks, dim_1, dim_2, nMines):
        super(mineDataset, self).__init__()
        self.state, self.mine = dataGenerator(dataSize=size, pickTime=picks, dim_1=dim_1, dim_2=dim_2, nMine=nMines)
        self.edge = edgeDetector(np.array(self.state))
        self.state = np.array(self.state)[:, None, :, :]
        self.mine = np.array(self.mine)[:, None, :, :]
        self.edge = np.array(self.edge)[:, None, :, :]

    def __getitem__(self, index):
        return self.state[index], self.mine[index], self.edge[index]

    def __len__(self):
        return len(self.state)


def getMState(map, dim_1=DIM_1, dim_2=DIM_2):
    mState = np.zeros((dim_1, dim_2))
    for row in range(DIM_1):
        for col in range(DIM_2):
            if np.isnan(map[row, col]):
                mState[row, col] = COVERED
            else:
                mState[row, col] = map[row, col]
    return mState


def getMMineMap(map):
    mMineMap = np.zeros((DIM_1, DIM_2))
    for row in range(DIM_1):
        for col in range(DIM_2):
            if map[row, col] == 1:
                mMineMap[row, col] = MINE
    return mMineMap


def probPicker(state, map):
    minProb = 1
    minX = 0
    minY = 0
    for row in range(DIM_1):
        for col in range(DIM_2):
            if map[row, col] < minProb and np.isnan(state[row, col]):
                minProb = map[row, col]
                minX = row
                minY = col
    return minX, minY


def edgeDetector(state):
    edges = []
    for Idx in range(len(state)):
        edgeMap = np.zeros((DIM_1, DIM_2))
        for row in range(DIM_1):
            for col in range(DIM_2):
                if state[Idx, row, col] == COVERED:
                    for i in range(max(0, row-1), min(DIM_1, row+2)):
                        for j in range(max(0, col-1), min(DIM_2, col+2)):
                            if not state[Idx, i, j] == COVERED:
                                edgeMap[row, col] = 1
        edges.append(edgeMap)
    return edges


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # 1 input image channel, 6 output channels, 3x3 square convolution
        # kernel
        self.conv1 = nn.Conv2d(1, 6, 3, padding=1)
        self.conv2 = nn.Conv2d(6, 10, 3, padding=1)
        self.conv3 = nn.Conv2d(10, 10, 3, padding=1)
        self.conv4 = nn.Conv2d(10, 16, 3, padding=1)
        # self.conv5 = nn.Conv2d(16, 16, 3, padding=1)
        self.conv6 = nn.Conv2d(16, 16, 3, padding=1)
        # an affine operation: y = Wx + b
        self.fc1 = nn.Linear(16 * DIM_1 * DIM_2, 4 * DIM_1 * DIM_2)  # 6*6 from image dimension
        self.fc2 = nn.Linear(4 * DIM_1 * DIM_2, 2 * DIM_1 * DIM_2)
        self.fc3 = nn.Linear(2 * DIM_1 * DIM_2, DIM_1 * DIM_2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        # x = F.relu(self.conv5(x))
        x = F.relu(self.conv6(x))
        x = x.view(-1, self.num_flat_features(x))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return x

    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features


if __name__ == "__main__":

    if IS_TRAIN:
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
        optimizer = optim.SGD(net.parameters(), lr=LR, momentum=0.9)

        # Training
        print("--- Training Start ---")

        best_loss = 10
        overFittingCount = 0

        for epoch in range(TRAINING_ROUND):
            loss = 0.0
            for i, data in enumerate(dataloaderTrain):
                state, mineMap, edgeMap = data
                # print(mineMap)
                # print(state)
                # print(edgeMap)
                # exit()
                optimizer.zero_grad()  # grad = 0
                outputs = net(state)  # forward output
                predict = edgeMap.view(BATCH_SIZE, -1) * outputs
                truth = edgeMap.view(BATCH_SIZE, -1) * mineMap.view(BATCH_SIZE, -1)
                loss = criterion(ZOOM_FACTOR * predict, ZOOM_FACTOR * truth)  # calculate loss
                loss.backward()  # backward gradient propagation
                optimizer.step()  # optimize using grad

            # Validation test
            validationLoss = 0
            with torch.no_grad():
                for data in dataloaderTest:
                    state, mineMap, edgeMap = data
                    # predict
                    outputs = net(state)
                    predict = edgeMap.view(BATCH_SIZE, -1) * outputs
                    truth = edgeMap.view(BATCH_SIZE, -1) * mineMap.view(BATCH_SIZE, -1)
                    validationLoss += criterion(ZOOM_FACTOR * predict, ZOOM_FACTOR * truth)
            print('[Epoch %d] validationLoss: %f' % (epoch + 1, validationLoss))

            # Save model
            if validationLoss < best_loss:
                best_loss = validationLoss
                torch.save(net, MODEL_PATH)
                print("Save best model!")
                overFittingCount = 0
            else:
                overFittingCount += 1
                if overFittingCount > 20:
                    break

        print("--- Training Done ---")


    if IS_PLAY:
        # Load model
        net = torch.load(MODEL_PATH)

        # Start a game
        game = MineSweeper(dim_1=DIM_1, dim_2=DIM_2, nMines=NMINES)
        game.selectCell((DIM_1 // 2, DIM_2 // 2))  # pick center as first
        print("Mines:")
        print(game.mines)
        step = 0
        probMap = np.zeros((DIM_1, DIM_2))
        while not game.gameOver:
            print("* " * 30)
            print(game.state)
            step += 1
            state = getMState(game.state)
            state = torch.Tensor(state).view(1, 1, DIM_1, DIM_2)
            output = net(state)
            probMap = output.view(DIM_1, DIM_2)
            x, y = probPicker(game.state, probMap)
            game.selectCell((x, y))
            print("Step %d, Select (%d, %d)" % (step, x, y))
        print("+ "*15, "OVER", " +"*15)
        if game.victory:
            print("Win! Total steps:", step)
        else:
            print("Game over! Total steps:", step)
        # print(probMap.detach().numpy())

    if IS_TEST:
        # Load model
        net = torch.load(MODEL_PATH)
        # print(net)
        # exit()

        # Testing
        print("Testing start...")
        win = 0
        for round in range(TESTING_ROUND):
            # print(round)
            # Start a game
            game = MineSweeper(dim_1=DIM_1, dim_2=DIM_2, nMines=NMINES)
            game.selectCell((DIM_1 // 2, DIM_2 // 2))  # pick center as first
            while not game.gameOver:
                state = getMState(game.state)
                state = torch.Tensor(state).view(1, 1, DIM_1, DIM_2)
                output = net(state)
                x, y = probPicker(game.state, output.view(DIM_1, DIM_2))
                game.selectCell((x, y))
            if game.victory:
                win += 1

        # Result
        print("Wining rate in %dx%d grid with %d mines: %f" % (DIM_1, DIM_2, NMINES, win/TESTING_ROUND))
