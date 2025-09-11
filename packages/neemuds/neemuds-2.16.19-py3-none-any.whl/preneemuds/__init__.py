from os import environ
from os.path import os
import sys
import traceback

from py3toolset.dep import check_mod_pkg
from py3toolset.txt_color import col, Color, print_frame


try:

    if(not check_mod_pkg("numpy")):
        raise Exception("numpy module not found. You must install it, read the README.")

except Exception as e:
    traceback.print_exc(file=sys.stdout)
    msg = str(e)
    if(not msg.lower().startswith("error")):
        msg = "Error: " + msg
    print_frame(msg, Color.RED, centering=False)
    exit()
