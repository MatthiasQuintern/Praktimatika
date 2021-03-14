import re

from tools import tool


def latex_table(formstring, vectors: dict, first_line="", box=True, decimal_sep=",", significant_digits=2):
    """
    Converts Vectors to a latex table
    :param decimal_sep:
    :param significant_digits:
    :param formstring:              form string: contains format with array names, eg "v & w pm uw"
    :param vectors:                 dictionaries, contains vectorname: array
    :param first_line:              first line of the table (eg to include units)
    :param box:
    :return:
    """
    # if not box, make hline and | to empty characters
    hline = ""
    vline = " "
    if box:
        hline = r"\hline"
        vline = "|"

    form = formstring.replace(" ", "").split("&")
    latex_form = ""  # the |l|c|c| thing
    # get one line for each array value (array length), assumed that all vectors have the same length
    lines = ["$" for i in range(tool.get_max_vec_length(list(vectors.values())))]

    for j in range(len(form)):
        latex_form += f"{vline}c"
        # get the processed arrays
        if re.fullmatch(".+pm.+", form[j]):
            v = tool.str_to_processed_arr(form[j].split("pm")[0], arrdict=vectors)[1]
            uv = tool.str_to_processed_arr(form[j].split("pm")[1], arrdict=vectors)[1]
        else:
            v = tool.str_to_processed_arr(form[j], arrdict=vectors)[1]
            uv = None
        for i in range(len(lines)):
            # if val pm uncert pair
            try:

                if uv is not None:
                    lines[i] += str(v[i]).replace(".", decimal_sep) + r"\pm" + str(uv[i]).replace(".", decimal_sep)
                else:
                    lines[i] += str(v[i]).replace(".", decimal_sep)
            except IndexError:
                lines[i] += "-"
            finally:
                # if at end
                if j == len(form) - 1:
                    lines[i] += "$\t\t" + r"\\ " + hline + "\n"
                else:
                    lines[i] += "$\t& $"
    latex_form += vline

    output = r"\begin{table}[h]" + "\n\t" + r"\centering" + "\n\t" + r"\begin{tabular}{" + latex_form + "}\n\t\t" + hline + "\n\t\t"
    output += f"%{formstring}\n"
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


def number_to_latex(number, dec_sep=","):
    # turn number to string and replace e-xx with \cdot 10^{-xx}
    num = str(number)
    match = re.search(r"e-?\d+", num)
    if match:
        num.replace(match.group(), "")
        return num + r"\cdot 10^{"+match.group().replace("e", "")+"}"

    return num
n = 123456789e8
n1 = 12345678.9123456789

print(number_to_latex(n), number_to_latex(n1))