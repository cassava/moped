#!/usr/bin/env python
# -*- coding: utf-8 -*-
# moped.py

name = "Moped"
version = "2.15"
author = "Ben Morgan <uv.sound@gmail.com>"
date = "17. November 2010"
license = "GNU General Public License"

import sys
import os
import random
import re
import optparse

import communication
import mpdcommunal
import mopedparser


class Options():
    addall = False
    advance = True
    append = False
    blacklist_on = False
    blacklist = []
    clear = False
    config = True
    crop = 0
    dryrun = False
    gtk = False
    insert = 0
    intelligent = False
    metacrop = -1
    play = True
    shuffle = True
    filter_duplicates = False
    
    config_path = os.environ['HOME'] + "/.moped"
    config_contents = ''
    cmd_options = {}
    cmd_args = ''
    
    def __init__(self):
        self._load_config()
        self._parse_options()
        if self.cmd_options.config:
            self._apply_config()
        self._apply_options()
        self._finalize()
    
    def _load_config(self, path=config_path):
        try:
            comm.send(2, "loading config file: '%s'" % path)
            istream = open(path, 'r')
            contents = istream.read()
            istream.close()
            return contents
        except IOError:
            # There is no config file, which is perfectly fine
            pass
    
    def _apply_config(self, contents=config_contents):
        try:
            # You see why this is dangerous!
            eval(contents)
        except:
            # If there are invalid commands, then it just won't work
            pass
    
    def _parse_options(self):
        optparser = optparse.OptionParser()
        
        optparser.usage = \
        """\b\b\b\b\b\b\b%s version %s  (%s)""" % (name, version, date)
        """\n"""
        """MPD Moped -- Driving your MPD playlists where they need to go!\n"""
        """Moped is an advanced playlist manipulator for the Music Player Daemon,\n"""
        """also known as MPD. The purpose is to provide a flexible and easy way\n"""
        """to add music to the playlist, as well as perform other extra tasks.\n"""
        """\n"""
        """  For a better understanding of how to use moped see the source file.\n"""
        """  The directions for the most recent features are best in the source.\n"""
        """\n"""
        """When adding all songs you can still add or remove some songs.\n"""
        """Some commands require arguments, other commands intuitively do not.\n"""
        """Copying a song or performing a dry search allows no other operation.\n"""
        """\n"""
        """You can search many different tags of songs, as well as use shortcuts:\n"""
        """'title', 'artist',  'album', 'genre', 'year', 'file', and 'any',\n"""
        """    't', 'a' 'ar', 'b' 'al',     'g',    'y',    'f', and   'x'.\n"""
        """\n"""
        """Distributed under the %s.""" % license
        
        # This still overrides the config. Way to fix that would be to apply config
        # before even loading these options, and then use the config values as default here.
        optparser.add_option("-i", "--insert", dest="insert", type="int", default=0, \
            help="insert the song(s) how many places after current")
        optparser.add_option("-a", "--append", dest="append", action="store_true", \
            help="append the song(s) at the end of the playlist, implies -t")
        optparser.add_option("-d", "--all-songs", dest="addall", action="store_true", \
            help="just insert all songs, assumes --crop --append")
        optparser.add_option("-s", "--ishuffle", dest="intelligent", action="store_true", default=False, \
            help="shuffle intelligently (by artist)")
        optparser.add_option("-n", "--no-shuffle", dest="shuffle", action="store_false", default=True, \
            help="do not shuffle the songs that are added")
        optparser.add_option("-c", "--crop", dest="crop", action="count", default=0, \
            help="crop playlist and count saved songs")
        optparser.add_option("-l", "--clear", dest="clear", action="store_true",
            help="clear playlist")
        optparser.add_option("-t", "--no-advance", dest="play", action="store_false", default=True, \
            help="do not play (the next song) if stopped")
        optparser.add_option("-x", "--filter-duplicates", dest="filter_duplicates", action="store_true", \
            help="filter out same songs being added to the playlist")
        optparser.add_option("-b", "--blacklist", dest="blacklist", action="store_true", \
            help="use the blacklist; creates a slowdown")
        optparser.add_option("-v", "--verbose", action="count", dest="verbosity", default=1, \
            help="how verbose? -v = status, -vv = debug messages")
        optparser.add_option("-q", "--quiet", dest="quiet", action="count", default=0, \
            help="how quiet? -q = errors, -qq = nothing at all, ever")
        optparser.add_option("-f", "--no-config", dest="config", action="store_false", default=True, \
            help="do not load the config file")
        optparser.add_option("-g", "--gtk", dest="gtk", action="store_true", \
            help="use a graphical command line enterpreter")
        optparser.add_option("-u", "--dryrun", dest="dryrun", action="store_true", \
            help="perform a dry search")
        
        options, args = optparser.parse_args()
        
        # Set verbosity settings
        firstverbosity = options.verbosity
        options.verbosity = options.verbosity - options.quiet
        comm.verbosity = options.verbosity
        
        if not args \
            and not options.addall \
            and not options.gtk \
            and not options.crop \
            and not options.clear \
            and not options.blacklist:
            print(optparser.format_help())
            sys.exit(2)
        
        # In case they want gui command-line
        if options.gtk:
            # Attempt to enable the gui.
            if comm._enable_gui():
                inlines = comm._gtk_get("Enter in command line arguments:", "Moped :: Command")
                if not inlines:
                    comm.send(2, "user pressed cancel or entered in only whitespace")
                    sys.exit(1)
                options, args = optparser.parse_args( inlines.split() )
                options.gtk = True
            else:
                # Cannot import wx, that is why this happends
                sys.exit(16)
        
        # Apply any extra verbosity settings
        options.verbosity = options.verbosity - options.quiet
        if options.verbosity == 1:
            # If the verbosity options were not changed put them first setting
            options.verbosity = firstverbosity
        comm.verbosity = options.verbosity
        
        self.cmd_options = options
        self.cmd_args = ' '.join(args)
    
    def _apply_options(self):
        self.insert = self.cmd_options.insert
        self.append = self.cmd_options.append
        self.addall = self.cmd_options.addall
        self.crop = self.cmd_options.crop
        self.clear = self.cmd_options.clear
        self.shuffle = self.cmd_options.shuffle
        self.intelligent = self.cmd_options.intelligent
        self.filter_duplicates = self.cmd_options.filter_duplicates
        self.blacklist_on = self.cmd_options.blacklist
        self.play = self.cmd_options.play
        self.config = self.cmd_options.config
        self.gtk = self.cmd_options.gtk
        self.dryrun = self.cmd_options.dryrun
    
    def _finalize(self):
        # Sort out the value of metacrop
        if self.clear or self.crop > 0:
            self.metacrop = self.crop


class Moped():
    def __init__(self, options, parser, mpc):
        self.options = options
        self.parser = parser
        self.mpc = mpc
        # Apply critical settings for the parser
        self.parser.shuffle = self.options.shuffle
        self.parser.shuffle_intelligent = self.options.intelligent
    
    def showsongs(self, insertlist, removelist):
        comm.send(1, "Dry Run")
        if self.options.addall:
            comm.send(1, "adding all songs...")
        if len(insertlist) > 0:
            comm.send(1, "inserting:")
            for song in insertlist:
                comm.send(1, "  " + song['file'])
        if len(removelist) > 0:
            comm.send(1, "\nremoving:")
            for song in removelist:
                comm.send(1, "  " + song['file'])
    
    def play(self):
        comm.send(3, "Moped: in play()")
        # Decide when options.advance should not be used
        if self.options.append:
            self.options.advance = False
        if self.options.advance and (self.mpc.state == 'stop'):
            comm.send(2, "play next")
            self.mpc.next()
        else:
            comm.send(2, "play")
            self.mpc.play()
    
    def run(self):
        comm.send(3, "Moped: in run()")
        # preparation
        comm.send(3, "  parsing the search formula '%s'" % self.options.cmd_args)
        insertlist, removelist = self.parser.process(self.options.cmd_args)
        
        if self.options.blacklist_on:
            comm.send(2, "generating blacklist...")
            for combo in self.options.blacklist:
                removelist.extend(mpc.search(combo[0], combo[1]))
        
        self.mpc.update()
        comm.send(3, "Playlist info before alteration:\n  currentsong=%d, playlistlength=%d, state=%s" % \
            (self.mpc.currentsong, self.mpc.playlistlength, self.mpc.state))
        
        error_list = []
        errors_occurred = False
        # filter duplicates if desired
        if self.options.filter_duplicates:
            comm.send(2, "  filtering already existent songs...")
            original_count = len(insertlist)
            insertlist = self.mpc.filterout_action(insertlist, self.mpc.songlist())
            filtered_count = len(insertlist)
            if filtered_count == 0 and filtered_count < original_count:
                errors_occurred = True
                error_list.append("Filtering duplicates reduced the song insert level to 0.")
        # check if some search results were empty
        if (len(self.parser.not_found) > 0) or (len(self.parser.filter_not_found) > 0):
            errors_occurred = True
            error_list.append("One or more search operations returned with no results:")
            for item in self.parser.not_found:
                error_list.append('\n\t%s \"%s\" %s' % (item[0], item[1], (item[2] and '(regex)' or '')))
            for item in self.parser.filter_not_found:
                error_list.append('\n\tfilter search: "%s<%s>"' % (item[1], item[0]))
            if len(insertlist) == 0:
                self.options.play = False
        
        # run baby run!
        if self.options.dryrun:
            # do a dry run
            self.showsongs(insertlist, removelist)
        else:
            # do the real thing
            # playlist alteration
            if self.options.metacrop > -1:
                self.mpc.metacrop(self.options.metacrop)
                self.options.advance = False
                self.mpc.update()
            # adding songs
            if self.options.addall:
                self.mpc.addall()
                self.mpc.shuffle()
                self.mpc.update()
            if len(insertlist) > 0:
                if self.options.append:
                    self.mpc.append(insertlist)
                    self.options.advance = False
                else:
                    if self.mpc.playlistlength == 0:
                        self.mpc.append(insertlist)
                        self.options.advance = False
                    elif self.mpc.playlistlength < 2:
                        self.mpc.append(insertlist)
                    elif self.mpc.currentsong == self.mpc.playlistlength:
                        self.mpc.append(insertlist)
                    else:
                        self.mpc.insert(insertlist, self.options.insert)
            # removing songs
            if len(removelist) > 0:
                self.mpc.remove(removelist)
            # play
            if self.options.play:
                self.mpc.update()
                self.play()
            
        # if there were errors, then show an error message now
        if errors_occurred:
            comm.send(0, ''.join(error_list))
        


if __name__ == "__main__":
    # Start a communication system
    comm = communication.UserCommunication()
    comm.default_ask_caption = "Moped :: Commandline"
    comm.default_info_caption = "Moped :: Information"
    comm.default_error_caption = "Moped :: Error!"
    # Initialize mpdcommunal, options, parser, and moped
    mpc = mpdcommunal.MpdCommunal(comm)
    parser = mopedparser.ArgumentParser(mpc)
    options = Options()
    moped = Moped(options, parser, mpc)
    
    try:
        moped.run()
    except mopedparser.MopedSyntaxError as error:
        comm.send(0, "MopedSyntaxError, " + error.representation)
        sys.exit(3)
    except mpdcommunal.mpdclient3.CommandError as error:
        comm.send(0, "MPD CommandError: " + error.args[0])
        sys.exit(5)
    except Exception as error:
        comm.send(0, "An unexpected error has occurred!")
        raise error
        sys.exit(128)
    
    # Exit codes are:
    #    1   user cancel
    #    2   misformat commandline
    #    3   moped syntax error
    #    4   mpd connection error
    #    5   mpd command error
    #    8   search results empty
    #   16   dependancy error
    #   32   messenger auto exit
    #  [64]  incomplete code
    #  128   unexpected error


# End of File
