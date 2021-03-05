import matplotlib.pyplot as plt
import functions as fun
import numpy as np


def rangeplot(f: fun.MathFunction, xmin=0, xmax=1, steps=1000, fig=None, dpi=300, ax=None, title=None, xlabel=None, ylabel=None, xscale="linear", yscale="linear", fontsize="14"):
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
    plt.rcParams.update({
        "font.size": fontsize,
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica"]})

    if not fig:
        fig = plt.figure(figsize=(8, 4), dpi=dpi, linewidth=1.0, frameon=None, subplotpars=None, tight_layout=True, constrained_layout=None)
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
        ax.set_title(title, fontsize=fontsize)
    # plt.imsave("meinbild.png")
    # plt.show()
    print(x, y)
    return fig, ax


def plot(xdata, ydata, marker=None, line="-", color=None, label=None,       # line options
         fig=None, ax=None, dpi=300,                                        # figure/axes options
         title=None, xlabel=None, ylabel=None, legend=False, fontsize="13", # labels....
         grid="major", gline="-", gcolor="#777",
         xlim=None, ylim=None, xscale="linear", yscale="linear",                                  # axes options
         show=True):
    """
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

    # todo:
        If the color is the only part of the format string, you can
        additionally use any  `matplotlib.colors` spec, e.g. full names
        (``'green'``) or hex strings (``'#008000'``).
    """
    plt.rcParams.update({
        "font.size": fontsize,
        # "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Avant Garde", "Computer Modern Sans serif"]})
    # Create format string: fmt = '[marker][line][color]'
    fmt = ""
    if marker:
        fmt += marker
    if line:
        fmt += line
    if color:
        fmt += color


    # figure:
    # figsize=None, dpi=None, facecolor=None, edgecolor=None, linewidth=0.0, frameon=None, subplotpars=None, tight_layout=None, constrained_layout=None
    # create a new figure is none is given:
    if not fig:
        fig = plt.figure(figsize=(8, 4), dpi=dpi, linewidth=1.0, frameon=None, subplotpars=None, tight_layout=True, constrained_layout=None)
    if not ax:
        ax = fig.add_subplot(xlabel=xlabel, ylabel=ylabel, xscale=xscale, yscale=yscale)

    ax.plot(xdata, ydata, fmt, label=label)

    ax.minorticks_on()

    if label or legend:
        ax.legend()

    if title:
        ax.set_title(title, fontsize=fontsize)

    if grid == "major" or grid == "minor" or grid == "both":
        ax.grid(b=True, which=grid, linestyle=gline, color=gcolor)

    if xlim:
        ax.set_xlim(*xlim)

    if ylim:
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
