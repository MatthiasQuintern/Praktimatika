import matplotlib.pyplot as plt
import functions as fun
import numpy as np


def rangeplot(f: fun.MathFunction, xmin=0, xmax=1, steps=1000, fig=None, ax=None, title=None, xlabel=None, ylabel=None, xscale="linear", yscale="linear", fontsize="14"):
    """
    :param f:       MathFunction object
    :param xmin:    minimal x-value
    :param xmax:    maximum x-value
    :param fig:     pyplot figure object
    :param steps:   how many points are calculated
    :param title:   title pf the plot
    :param xlabel:  x-axis label
    :param ylabel:  y-axis label
    :param xscale:  "linear", "log", "symlog", "logit", ..
    :param yscale:  "linear", "log", "symlog", "logit", ..
    :return:        matplotlib figure object, matplotlib axes object
    """
    # figure:
    # figsize=None, dpi=None, facecolor=None, edgecolor=None, linewidth=0.0, frameon=None, subplotpars=None, tight_layout=None, constrained_layout=None
    # create a new figure is none is given:
    plt.rcParams['font.size'] = fontsize
    if not fig:
        fig = plt.figure(figsize=(8, 4), dpi=None, linewidth=1.0, frameon=None, subplotpars=None, tight_layout=True, constrained_layout=None)
    if not ax:
        ax = fig.add_subplot(xlabel=xlabel, ylabel=ylabel, xscale=xscale, yscale=yscale)

    dx = abs(xmax - xmin) / steps
    # np.arange seems to leave out the upper value, so x1+dx gives x1 as the highest value
    x = np.arange(xmin, xmax + dx, dx)
    y = np.empty([steps + 1])

    for i in range(0, steps + 1, 1):
        y[i] = f.calc(x[i])
    ax.plot(x, y)

    if title:
        ax.set_title(title, fontsize=14)
    # plt.imsave("meinbild.png")
    # plt.show()
    print(x, y)
    return fig, ax
"""
x = fun.V("x")
f = fun.Exp(fun.Prod(complex(0, 1), x))
# print(f.calc(np.pi/2))
bild, achse = rangeplot(f, 0, 100, steps=10, title="Mein Plot")
achs2 = bild.add_subplot()
achs2.plot([0, 0.5, 0.8], [1, 3, 4])
bild.savefig("a.png")
plt.show()
print(type(bild))
"""