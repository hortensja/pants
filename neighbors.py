from functools import reduce
from math import sin, cos, sqrt
import pylab as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

SONSIAD = 5


def fajna_function(x, y):
    return np.sin(x * y) ** 2 + np.cos(x ** 2 + y ** 2)


def dystance(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def gupia_function(truX, truY, X, Y):
    print(X.shape)
    dupa = np.multiply.reduce(X.shape)
    X = X.reshape(dupa)
    Y = Y.reshape(np.multiply.reduce(Y.shape))
    truX = truX.reshape(np.multiply.reduce(truX.shape))
    truY = truY.reshape(np.multiply.reduce(truY.shape))
    trutruXY = np.array((truX, truY)).T
    eror_table = []
    for i in range(dupa):
        x, y = X[i], Y[i]
        xy = (x, y)
        trutruXY = sorted(trutruXY, key=lambda p: dystance(xy, p))
        neighbors = np.array(trutruXY[:SONSIAD]).T
        meaningless = np.mean(fajna_function(*neighbors))
        eror = abs(meaningless-fajna_function(x,y))
        eror_table.append(eror)
        # return 69
    print(np.mean(eror_table))
    return np.array(eror_table).reshape((10,10))


if __name__ == "__main__":
    print("kupa")

    # Sample data
    side = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(side, side)


    truX, truY = np.random.rand(2, 10, 10)*4-2

    Z = gupia_function(truX, truY, X ,Y)
    # # print(X,Y)
    # Z = fajna_function(X, Y)
    # # print(Z)
    # # Plot the density map using nearest-neighbor interpolation
    #
    fig = plt.figure(facecolor='k')
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_wireframe(X=X, Y=Y, Z=Z)
    plt.show()
