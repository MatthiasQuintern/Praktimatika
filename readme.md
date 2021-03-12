# Praktimatika

## Dependencies
Praktimatika needs other python libraries for some features. Install them with pip or conda.

### Mandatory
- npyscreen:        Terminal User Interface
- windows-curses    Terminal User Interface. Only needed by *Windows* users.
- sympy:            symbolic mathmatics in python

### Optional (but recommended) Dependencies
- pandas:       copying to clipboard and importing xlsx, ods ...

## Usage
Praktimatika can not be run from an IDE. You have to run it from a terminal emulator (e.g. Windows PowerShell).
To start the application open your terminal, navigate to the location of the "Praktimatika.py" and type:
`python Praktimatika.py` on Windows and `python3 Praktimatika.py` on Linux

## Usage in scripts
If you want to use functions from the programm in a python script, you can just import the needed module. The User Interface is strictly separated from mathmatical functionality, so everything can be used outside Praktimatika.
For example, to use the *Smart Import* Function in a script you can use:
`from tools import sheet_read as sr`
`arrays = sr.get_vecs(sr.read_table("path_to_your_spread_sheet/spread_sheet.xlsx"))`
If your script is inside another folder than the Praktimatika files, use
`import sys`
`sys.path.append("path_to_praktimatika_folder")`
before the import statement.

## Sessions
All data (functions, arrays, figures...) are saved as dictionaries of a "PKTSession" object. These sessions-objects can be saved and loaded with python `pickle`.

## Plotting
Showing the plots interactively with matplotlib.pylot is currently not working. But figures can be saved as images with the "Save Image" Button.