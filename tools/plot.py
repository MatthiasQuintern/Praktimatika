import matplotlib.pyplot as plt
import numpy as np
import re


def range_plot(f, xmin=0, xmax=1, steps=1000,  **keywords):
    """
    Plots a function in an area
    :param f:           a python function, depending on one variable
    :param xmin:        lower x-limit
    :param xmax:        upper x-limit
    :param steps:       count of points calculated
    :param keywords:    see 'tools.tool.plot' for all keyword options
    :return:            matplotlib figure, matplotlib axis
    """
    dx = abs(xmax - xmin) / steps
    # np.arange seems to leave out the upper value, so x1+dx gives x1 as the highest value
    xdata = np.arange(xmin, xmax, dx)
    ydata = np.empty([steps + 1])

    for i in range(0, steps + 1, 1):
        ydata[i] = f(xdata[i])
    fig, ax = plot(xdata, ydata, **keywords)
    return fig, ax


def plot(xdata, ydata, marker=None, line="-", color=None, label=None,       # line options
         fig=None, ax=None, dpi=300, figsize=None,                                     # figure/axes options
         title=None, xlabel=None, ylabel=None, legend=False, fontsize="13", # labels....
         grid="major", gline="-", gcolor="#888",
         xlim=None, ylim=None, xscale="linear", yscale="linear",                                  # axes options
         show=True):
    """
    :param figsize:
    :param grid:    "major", "minor", "both"
    :param gcolor   wie color
    :param gline    wie line
    :param dpi:
    :param label:
    :param color:   b g r c m y k w
    :param line:    - -- -. :
    :param marker:  .,ov^<>1234sp*hH+Dd|_
    :param xdata:
    :param ydata:
    :param fig:     pyplot figure object
    :param ax:      axes object
    :param title:   title pf the plot
    :param xlabel:  x-axis label
    :param ylabel:  y-axis label
    :param xscale:  "linear", "log", "symlog", "logit", ..
    :param yscale:  "linear", "log", "symlog", "logit", ..
    :return:        matplotlib figure object, matplotlib axes object


            **Markers**

        =============    ===============================
        character        description
        =============    ===============================
        ``'.'``          point marker
        ``','``          pixel marker
        ``'o'``          circle marker
        ``'v'``          triangle_down marker
        ``'^'``          triangle_up marker
        ``'<'``          triangle_left marker
        ``'>'``          triangle_right marker
        ``'1'``          tri_down marker
        ``'2'``          tri_up marker
        ``'3'``          tri_left marker
        ``'4'``          tri_right marker
        ``'s'``          square marker
        ``'p'``          pentagon marker
        ``'*'``          star marker
        ``'h'``          hexagon1 marker
        ``'H'``          hexagon2 marker
        ``'+'``          plus marker
        ``'x'``          x marker
        ``'D'``          diamond marker
        ``'d'``          thin_diamond marker
        ``'|'``          vline marker
        ``'_'``          hline marker
        =============    ===============================

        **Line Styles**

        =============    ===============================
        character        description
        =============    ===============================
        ``'-'``          solid line style
        ``'--'``         dashed line style
        ``'-.'``         dash-dot line style
        ``':'``          dotted line style
        =============    ===============================

        Example format strings::

            'b'    # blue markers with default shape
            'or'   # red circles
            '-g'   # green solid line
            '--'   # dashed line with default color
            '^k:'  # black triangle_up markers connected by a dotted line

        **Colors**

        The supported color abbreviations are the single letter codes

        =============    ===============================
        character        color
        =============    ===============================
        ``'b'``          blue
        ``'g'``          green
        ``'r'``          red
        ``'c'``          cyan
        ``'m'``          magenta
        ``'y'``          yellow
        ``'k'``          black
        ``'w'``          white
        =============    ===============================
        and the ``'CN'`` colors that index into the default property cycle.

    """
    plt.rcParams.update({
        "font.size": fontsize,
        # "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Avant Garde", "Computer Modern Sans serif"]})

    # Check if marker, line and color are valid, set None otherwise
    if not (isinstance(marker, str) and marker in ".,ov^<>1234sp*hH+Dd|_:"):
        marker = None
    if not (isinstance(line, str) and line in "--.:"):
        line = None
    if not (isinstance(color, str) and re.fullmatch(r"([bgrcykw])|(#[\da-fA-F]{3})|(#[\da-fA-F]{6})", color)):
        color = None

    fsize = None
    # check if valid figsize is given

    try:
        if not isinstance(figsize, str) and len(figsize) == 2:
            fsize = figsize
    except TypeError:
        pass

    # figure:
    # figsize=None, dpi=None, facecolor=None, edgecolor=None, linewidth=0.0, frameon=None, subplotpars=None, tight_layout=None, constrained_layout=None
    # create a new figure is none is given:
    if not fig:
        fig = plt.figure(figsize=fsize, dpi=dpi, linewidth=1.0, frameon=True, subplotpars=None, tight_layout=True, constrained_layout=None)
    if not ax:
        ax = fig.add_subplot(xlabel=xlabel, ylabel=ylabel, xscale=xscale, yscale=yscale)
    ax.plot(xdata, ydata, color=color, marker=marker, linestyle=line, label=label)

    if label and legend:
        ax.legend()

    if title:
        ax.set_title(title, fontsize=fontsize)

    if grid == "major" or grid == "minor" or grid == "both":
        if grid == "minor" or "both":
            ax.minorticks_on()
        ax.grid(b=True, which=grid, linestyle=gline, color=gcolor)

    if xlim:
        if xlim[0] != xlim[1]:
            ax.set_xlim(*xlim)

    if ylim:
        if ylim[0] != ylim[1]:
            ax.set_ylim(*ylim)

    # plt.imsave("meinbild.png")
    if show:
        plt.show()

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
# plt.grid(True)
