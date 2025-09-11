#!python

from neemuds.local_params import parse_local_conf_file
try:
    # dev mode
    from disper96 import main
except:
    # pkg installed via pip
    from pydisper96.disper96 import main


if __name__ == '__main__':
    p = parse_local_conf_file()
    main(p.fS, p.fU, p.ic, p.h, p.f1, p.fM)
