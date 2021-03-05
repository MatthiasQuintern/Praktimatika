import re


def latex_table(form, vectors: dict, first_line="", box=True, decimal_sep=",", significant_digits=2):
    """
    Converts Vectors to a latex table
    :param decimal_sep:
    :param significant_digits:
    :param form:            form string: contains format with vector names
    :param vectors:         dictionaries, contains vectorname: vector
    :param first_line:      first line of the table (eg to include units)
    :param box:
    :return:
    """
    # if not box, make hline and | to empty characters
    hline = ""
    vline = " "
    if box:
        hline = r"\hline"
        vline = "|"

    form = form.replace(" ", "").split("&")
    latex_form = ""  # the |l|c|c| thing
    # get one line for each vector value (vector length), assumed that all vectors have the same length
    lines = ["$" for i in range(len(list(vectors.values())[0]))]

    for j in range(len(form)):
        latex_form += f"{vline}c"
        for i in range(len(lines)):
            # if val pm uncert pair
            if re.fullmatch(".+pm.+", form[j]):
                lines[i] += str(vectors[form[j].split("pm")[0]][i]) + r"\pm" + str(vectors[form[j].split("pm")[1]][i])
            else:
                lines[i] += str(vectors[form[j]][i])
            # if at end
            if j == len(form) - 1:
                lines[i] += "$\t\t" + r"\\ " + hline + "\n"
            else:
                lines[i] += "$\t& $"
    latex_form += vline

    output = r"\begin{table}[h]" + "\n\t" + r"\centering" + "\n\t" + r"\begin{tabular}{" + latex_form + "}\n\t\t" + hline + "\n"
    for line in lines:
        output += "\t\t" + line
    output += "\t" + r"\end{tabular}" + "\n\t" + r"% \caption{}" + "\n\t" + r"% \label{tab:}" + "\n" + r"\end{table}" + "\n"

    return output


def get_significant_pair(value, uncert, sig_digits):
    """
    0,1238123 0,3487583
    :param value:
    :param uncert:
    :param sig_digits:
    :return:
    """
    sig_val = ""
    for char in value:
        pass