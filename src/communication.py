#!/usr/bin/env python
# -*- coding: utf-8 -*-
# communication.py

# User interface communication abstraction layer
# Copyright © 2008, 2009, 2011 Ben Morgan <neembi@googlemail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import sys
import os

# This class is primarily useful for where once the program has started,
# there is no further interaction with the user. And it is useful for
# programs which want to be both gui and console, but not restrict
# the user to either. If it is primarily a console based program, then
# this class is not as useful for it.

# While I wait for the old wxPython to work with Python 3.0
# I am using zenity as my method for graphical communication.
# It is certainly inferior to wxPython, but I cannot do anything about that.

class UserCommunication():
    """UserCommunication is a class which provides a flexible system with which
    one can easily and effectively communicate various messages to the user,
    based on the verbosity of the message.
    """
    
    console=True        # Use console communication
    verbosity=1         # Console verbosity level
    gui=False           # Use gui communication, only accepts level 0 messages
    auto_quit=False     # Does the program quit on an error
    
    # Default captions
    default_info_caption="Some Information For You"
    default_ask_caption="What is Your Opinion?"
    default_error_caption="An Error Occurred"
    
    # Verbosity levels can be determined separately, but as a guide, these are good:
    #   0 = error, something went wrong
    #   1 = basic, altering something
    #   2 = status, just letting you know
    #   3 = debug, programming specific, what method, class, loop info, etc
    
    # If you want to set the default captions, do that manually
    def __init__(self, console=True, verbosity=1, gui=False):
        self.console = console
        self.verbosity = verbosity
        if gui:
            self._enable_gui()
    
    # Returns True or False if succeeds or fails.
    # If it fails, it is because it cannot import wx,
    # and then the console will be used instead.
    def _enable_gui(self):
        self.gui = True
        return True
    
    def _gtk_get(self, prompt, caption):
        prompt = prompt.replace('"', '\\"')
        with os.popen('zenity --entry --text="%s"' % prompt) as istream:
            return istream.read().strip()
    
    def _console_get(self, prompt):
        return input(prompt)
    
    # Get something from the user, this can only be one at a time
    def get(self, prompt, caption=default_ask_caption ):
        if self.gtk:
            return _gtk_get(prompt, caption)
        else:
            return _console_get(prompt)
    
    # Send a message to the user.
    # an output of 0 disables gui and 1 disables console
    def send(self, level, text, caption=default_error_caption, output=2):
        if self.verbosity >= level:
            if self.console and output!=1:
                if level == 0:
                    print(text, end='\n', file=sys.stderr)
                else:
                    print(text, end='\n')
            if self.gui and level==0 and output!=0:
                text = text.replace('"', '\\"')
                os.popen('zenity --info --text="%s"' % text)


class ConsoleCommunication():
    def __init__(self):
        # disable the entire system by setting verbosity = -1
        self.verbosity = 0
    
    def get(self, prompt):
        return input(prompt)
    
    def send(self, level, text, newline=True):
        if self.verbosity >= level:
            if level == 0:
                print(text, end=(newline and '\n' or ''), file=sys.stderr)
            else:
                print(text, end=(newline and '\n' or ''))
    
    def write(self, text):
        print(text, end='')

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
