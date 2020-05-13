#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Other utilities."""

import os
import sys

try:
    import winsound
except ModuleNotFoundError:
    pass


def makeSound(duration=1):
    """Make a sound for two seconds.

    On linux you need to instal sox:
    sudo apt install sox

    On windows you need install winsound:
    pip install winsound
    """
    uname = sys.platform.lower()
    if os.name == 'nt':
        uname = 'win'
    if uname.startswith('linux'):
        uname = 'linux'

    duration = duration*1000  # milliseconds
    freq = 440  # Hz

    if uname == 'win':
        try: winsound.Beep(freq, duration)
        except: print('Warning: myModules.makeSound cannot generate sound.')
    else:
        try: os.system('play -nq -t alsa synth {} sine {}'.format(duration/1000, freq))
        except: print('Warning: myModules.makeSound cannot generate sound.')


def sayOutLoud(message):
    """Make a sound.

    You need to install the speech-dispatcher package in Ubuntu (or the
    corresponding package on other distributions).
    """
    os.system('spd-say "' + str(message) + '"')


def query_yes_no(question, default="yes"):
    """Ask a yes/no question and return answer.

    Args:
        question (str): is a string that is presented to the user.
        default ('yes', 'no' or None): is the presumed answer if the user just hits
            <Enter>. If None an answer is required of the user.

    Returns
        True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "Y": True, "YES": True, "YE": True,
             "no": False, "n": False, "No":True, "NO":True, "N":True}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt + '\n')
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
