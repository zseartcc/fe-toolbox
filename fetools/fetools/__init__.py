import os

__all__ = ["pause", "clear", "VRC", "VSTARS", "VERAM"]


#########################
# Lib-level constants
#########################

VRC = "vrc"
VSTARS = "veram"
VERAM = "veram"


#########################
# Misc. helpers
#########################

def pause():
    """ Does 'Press any key to continue' """
    if os.name == "nt":
        print()
        os.system("pause")
    else:
        input("\nPress Enter to continue . . . ")

def clearscreen():
    """ Clear the terminal/command prompt """
    os.system("cls" if os.name=="nt" else "clear")