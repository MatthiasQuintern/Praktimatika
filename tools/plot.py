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
    xdata = np.arange(xmin, xmax, dx)
    ydata = np.empty([steps])
    for i in range(0, steps, 1):
        ydata[i] = f(xdata[i])
    fig, ax = plot(xdata, ydata, **keywords)
    return fig, ax


def plot(xdata=None, ydata=None, marker=None, line="-", color=None, label=None,                   # line options
         xerr=None, yerr=None,
         # ecolor=None, elinewidth=None, capsize=None, barsabove=False, lolims=False, uplims=False, xlolims=False, xuplims=False, errorevery=1, capthick=None
         fig=None, dpi=300, figsize=None,                                               # figure/axes options
         tight_layout=True, constrained_layout=False,
         ax=None, xlim=None, ylim=None, xscale="linear", yscale="linear",               # axes options
         title=None, xlabel=None, ylabel=None, legend=False, fontsize="13",             # labels options
         grid="major", gline="-", gcolor="#888",                                        # grid options
         show=False):
    """
        data:
            :param xdata:
            :param ydata:
        errors
            :param xerr:    x-Errors, float or array-like, shape(N,) or shape(2, N)
            :param yerr:    y-Errors, float or array-like, shape(N,) or shape(2, N)
        line options
            :param label:   a label to use in the legend
            :param color:   b g r c m y k w
            :param line:    - -- -. :
            :param marker:  .,ov^<>1234sp*hH+Dd|_
        figure options
            :param fig:     pass an existing pyplot figure object
            :param dpi:     resolution of the figure
            :param figsize: x/y size of the figure, array-like, shape(2)
            :param fontsize:
            :param tight_layout:
            :param constrained_layout:
        axis options
            :param ax:      pass an existing axis object
            :param title:   title pf the plot
            :param xlabel:  x-axis label
            :param ylabel:  y-axis label
            :param legend:  wether to turn on the legend. is automatically set True if a label for the data is given
            :param xscale:  "linear", "log", "symlog", "logit", ..
            :param yscale:  "linear", "log", "symlog", "logit", ..
            :param xlim:    limits for the x-axis, array-like, shape(2)
            :param ylim:    limits for the y-axis, array-like, shape(2)
        grid options
            :param grid:    "major", "minor", "both", "none"
            :param gcolor   grid color, see 'color'
            :param gline    grid line style, see 'line'
        other
            :param show:    wether to call plt.show() at the end
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
        "font.sans-serif": ["Helvetica", "Avant Garde", "Computer Modern Sans serif"],
        "font.family": "sans-serif"})

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

    # create new figure is none is given
    if not fig:
        fig = plt.figure(figsize=fsize, dpi=dpi, linewidth=1.0, frameon=True, subplotpars=None, tight_layout=tight_layout, constrained_layout=constrained_layout)
    # create new axis if none is given
    if not ax:
        ax = fig.add_subplot(xlabel=xlabel, ylabel=ylabel, xscale=xscale, yscale=yscale)

    # check which data is given
    # xdata -> vertical lines
    # ydata -> horizontal lines
    # xdata and ydata -> plot
    # xdata and ydata and (xerr or yerr) -> errorbar

    if xdata is not None and ydata is not None:
        # if errors are given, use errorbar. else use plot
        if xerr is not None or yerr is not None:
            ax.errorbar(xdata, ydata, xerr=xerr, yerr=yerr, color=color, marker=marker, linestyle=line, label=label, ecolor=color, capsize=4)
        else:
            ax.plot(xdata, ydata, color=color, marker=marker, linestyle=line, label=label)

    elif xdata is not None:
        ax.vlines(xdata, colors=color, linestyles=line, label=label)

    elif ydata is not None:
        ax.hlines(ydata, colors=color, linestyles=line, label=label)

    else:
        return None, None

    # turn on the legend if a label is given or legend=True
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
