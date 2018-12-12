#! /usr/bin/python3.6
import matplotlib.pyplot as plt
import math
import numpy as np
import sys


# plot(): plots the correlation graph
def plot(x, y):
    plt.plot(x, y, 'ro')
    plt.axis([-15, 15, 0, 20000])
    plt.show()
 

# pearson(): finds the correlation coefficient between X and Y
def pearson(X, Y):
    N = len(X)
    if N != len(Y):
        return None
    sqrX = [x**2 for x in X]
    sqrY = [y**2 for y in Y]
    XY = []
    for i in range(N):
        XY.append(X[i]*Y[i])
    r = (N*sum(XY) - sum(X)*sum(Y)) / math.sqrt((N*sum(sqrX)-sum(X)**2)*(N*sum(sqrY)-sum(Y)**2))
    return r


# spikeFlag(): checks that a user is not increasing their bet by a large margin (spiking)
def spikeFlag(x, y, won, tableMin, filename):
    for i in range(1, len(y)):
        if (y[i] - y[i-1]) > 4*tableMin:
            if won[i-1] == "False":
                if x[i] > 2:
                    return "Flag spike! for game: " + str(i)
    return "none"
    

# Main Method: read game data into lists and run analysis methods
if __name__ == "__main__":
    x = []
    y = []
    won = []
    with open(sys.argv[1]) as f:
        for line in f:
            vals = line.split()
            won.append(vals[0])
            x.append(float(vals[2]))
            y.append(float(vals[1]))
    f.close()

    print(pearson(x, y))
    print(np.corrcoef(x, y)[0, 1])
    print(spikeFlag(x, y, won, 10, sys.argv[1]))
    plot(x, y)
