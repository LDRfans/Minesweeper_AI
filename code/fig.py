import matplotlib.pyplot as plt
import numpy as np

loss = []

fo = open("trainingLoss.txt")
lines = fo.readlines()
for line in lines:
    loss.append(float(line.replace('\n','').replace('\r','')))
# print(loss)
# exit()

x = list(range(len(loss)))
plt.plot(x, loss, color='red', linewidth=1, linestyle='-')
plt.xlabel('epoch')
plt.ylabel('validation_loss')
plt.title("9x9 Map, 10 Mines")
# plt.show()
plt.savefig('net.png', dpi=600)
plt.close('all')
