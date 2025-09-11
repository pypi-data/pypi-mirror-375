#!python
import numpy
import sys
import os

import matplotlib.pyplot as plt
import numpy as np


if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.argv[0])+"/..")
    from py3toolset.txt_color import col, Color
    if(len(sys.argv) > 1):
        filename = sys.argv[1]
    else:
        print(col(Color.RED,"Error: I need a data file to plot."))
        print(col(Color.GREEN, "USAGE: "+sys.argv[0]+" xyz_file [<xlabel> [<ylabel>]]"))
        print("For example: "+col(Color.GREEN, "USAGE: "+sys.argv[0]+"")+" URpdffrq.xyz")
        exit()
    xlabel,ylabel = "U", "f"
    if(len(sys.argv) > 2):
        xlabel = sys.argv[2]
    if(len(sys.argv) > 3):
        ylabel = sys.argv[3]
    
    f = open(filename)
    lines = f.readlines()
    f.close()
    x, y, d = [], [], []
    for l in lines:
        fields = l.split()
        fields = [float(f) for f in fields]
        if(len(x) == 0 or x[-1] != fields[0]):
            x += [fields[0]]
            d += [[fields[2]]] 
        else:
            d[-1] += [fields[2]]
        if(len(x) <= 1):
            y += [fields[1]]
    print("x=", x)
    print("y=", y)
    print("d=", d)
    print(len(d), len(d[0]), len(d[1]))
    print(len(x), len(y))
    max_dlen = max([len(e) for e in d])
    # y must be equal to the density row max size
    if(len(y) < max_dlen):
        # complete too small y range, with its delta
        ydelta = max(1, int(y[1] - y[0]))
        y += [float(i) for i in range(int(y[-1]), ydelta * max_dlen, ydelta)] 
    # equalize density rows, filling with zeros
    for i in range(0, len(d)):
        if(len(d[i]) < max_dlen):
            d[i] += [ 0 for i in range(len(d[i]), max_dlen)]
#    print(len(d), len(d[0]), len(x), len(y)) 
    y = numpy.array(y)
    x = numpy.array(x)
    d = numpy.array(d)
    fig = plt.figure()
    plt.pcolormesh(y, x, d)#, cmap="Greys")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Prob.')
    print(col(Color.YELLOW,"Saving graph into "+filename+".png"))
    plt.savefig(filename+".png", dpi=300)
    plt.show()
