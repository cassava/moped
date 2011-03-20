#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mpdcommunal.py

# The MPD CommunAL - MPD Communication Abstraction Layer
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
import re
import mpdclient3

class MpdCommunal():
    """MpdCommunal is a class that provides methods to communicate to mpd and
    manipulate the mpd playlist in ways which mpdclient2 is unable to.
    """
    
    def __init__(self, comm_pipe=None, comm_enabled=True):
        """commpipe is an object to send messages to"""
        # The interface to the MPD Daemon
        self.mpd = mpdclient3.MPDClient()
        self.host = 'localhost'
        self.port = 6600
        
        # Songs withheld as hostages ;-)
        self.hostages = []
        # The flags that are used when a regex search is made
        self.regexflags = re.I
        # Current song information
        self.status={}
        self.playlistlength=0
        self.currentsong=0
        self.state='play'
        
        # Determine where messages are sent to
        if not comm_enabled:
            self.comm = SimpleCommunication(False)
        else:
            if comm_pipe is not None:
                self.comm = comm_pipe
            else:
                self.comm = SimpleCommunication()
        self.update()
    
    def connect(self):
        """start communication with the mpd daemon"""
        try:
            if self.mpd._sock:
                self.mpd.disconnect()
            self.mpd.connect(self.host, self.port)
        except:
            self.comm.send(0, "err, mpd connection is faulty")
            raise MpdCommunalError("error, mpd connection is faulty")
    
    def update(self):
        self.connect()
        """update the mpd connection and current song information"""
        self.status = self.mpd.status()
        self.state = self.status['state']
        self.playlistlength = int(self.status['playlistlength'])
        if 'song' in self.status:
            self.currentsong = int(self.status['song'])
        else:
            self.currentsong = 0
    
    def playlist(self):
        """get the playlist"""
        return self.mpd.playlistinfo()
    
    def songlist(self):
        """get the playlist, but strip extra information"""
        playlist = self.playlist()
        for song in playlist:
            del song['pos']
            del song['id']
        return playlist
    
    def play(self):
        """play"""
        self.mpd.play()
    
    def playsong(self, song):
        """play given song in playlist"""
        self.mpd.play(song)
    
    def next(self):
        """play next song"""
        if self.state == 'stop':
            if self.currentsong < (self.playlistlength - 1):
                self.mpd.play(self.currentsong + 1)
        else:
            self.mpd.next()
    
    def addall(self):
        """add all songs to the playlist"""
        self.comm.send(1, "adding all songs to playlist...")
        self.mpd.add("")
    
    def append(self, songlist):
        """append the list of songs to the playlist"""
        self.comm.send(2, "adding %d song%s to playlist..." % \
            (len(songlist), (len(songlist)!=1 and 's' or '')) )
        for song in songlist:
            self.comm.send(1, "adding: '%s'" % song['file'])
            self.mpd.add(song['file'])
    
    def insert(self, songlist, advance=0):
        """insert the list of songs to the playlist"""
        self.comm.send(2, "inserting %d song%s to playlist at C+%d..." % \
            (len(songlist), (len(songlist)!=1 and 's' or ''), 1+advance) )
        increase = 1
        for song in songlist:
            self.comm.send(1, "inserting: '%s'" % song['file'])
            self.mpd.add(song['file'])
            self.mpd.move(self.playlistlength+increase-1, self.currentsong+increase+advance)
            increase = increase + 1
    
    def remove(self, songlist):
        """remove the list of songs from the playlist"""
        if len(songlist) > 0:
            self.comm.send(2, "removing %d song%s from playlist..." % \
                (len(songlist), (len(songlist)!=1 and 's' or '')) )
            playlistids = {}
            for item in self.mpd.playlistinfo():
                if item['file'] not in playlistids:
                    playlistids[item['file']] = [int(item['id'])]
                else:
                    playlistids[item['file']].append(int(item['id']))
            removeids = []
            for item in songlist:
                if item['file'] in playlistids:
                    self.comm.send(1, "removing: '%s'" % item['file'])
                    removeids.append(playlistids[item['file']])
            for ids in removeids:
                for num in ids:
                    self.mpd.deleteid(num)
    
    def clear(self):
        """clears the playlist"""
        self.comm.send(1, "clearing playlist")
        self.mpd.clear()
    
    def crop(self):
        """crops the playlist"""
        self.comm.send(1, "cropping playlist")
        self.mpd.move(self.currentsong, 0)
        for i in range(self.playlistlength-1, 0, -1):
            self.mpd.delete(i)
    
    def metacrop(self, withhold):
        """clears the playlist and withholds the specified number of songs"""
        if withhold == 0:
            self.clear()
        elif withhold == 1:
            self.crop()
        elif withhold > 1:
            self.save(withhold)
            self.crop()
            self.restore()
    
    def shuffle(self):
        """shuffle the entire mpd playlist"""
        self.mpd.shuffle()
    
    def save(self, number):
        """takes note of the songs which will later be inserted"""
        available_songs = self.playlistlength - self.currentsong
        if available_songs > 1:
            if number > available_songs:
                number = available_songs
            self.comm.send(2, "saving %d songs" % number)
            for i in range(1, number):
                self.hostages.append(self.mpd.playlistinfo(self.currentsong+i)[0])
    
    def restore(self):
        """inserts the saved songs back to the playlist"""
        if len(self.hostages) > 0:
            self.comm.send(2, "restoring 1+%d songs" % len(self.hostages))
            self.append(self.hostages)
    
    def regex_search(self, query, pattern):
        """a single search for a single type with a regex pattern"""
        try:  # first see if the pattern is valid
            matcher = re.compile(pattern, self.regexflags)
        except:
            self.comm.send(0, "err, regex pattern is invalid.")
            raise MpdCommunalRegexError("error, regex pattern is invalid")
        database = self.mpd.listallinfo()
        flags = self.regexflags
        typelist = []
        for item in (i for i in database if query in i):
            if item[query] not in typelist:
                typelist.append(item[query])
        results = []
        for item in typelist:
            if matcher.search(item) != None:
                results.append(item)
        songlist = []
        for item in results:
            self.comm.send(2, "searching '%s' '%s'..." % (query, item))
            songlist.extend(self.mpd.search(query, item))
        return songlist
    
    def search(self, query, text, regex=False):
        """a simple search for a single type and a single text"""
        if regex:
            return self.regex_search(query, text)
        else:
            self.comm.send(2, "searching '%s' '%s'..." % (query, text))
            return self.mpd.search(query, text)
    
    def multi_search(self, queries, regex=False):
        """a multi search with many types and many texts"""
        # Expect that queries is in the form: [[type, args], [type, args]]
        songlist = []
        for pair in queries:
            self.comm.send(2, "searching '%s' '%s'..." % (pair[0], pair[1]))
            songlist.extend(self.search(pair[0], pair[1], regex))
        return songlist
    
    def filter_action(self, songlists):
        """A filter function for filtering out songs that are not in all lists,
        Thus only the songs that are in all of the lists will be included.
        """
        results = []
        for song in songlists[0]:
            songValid = True
            for i in range(1, len(songlists)):
                if song not in songlists[i]:
                    songValid = False
                    break
            if songValid: results.append(song)
        return results
    
    def filterout_action(self, songlist, removelist):
        """A filter function for filtering out songs from songlist
        that are in the list removelist. Thus songlist will be returned
        without whatever is in removelist.
        """
        for song in removelist:
            while song in songlist:
                songlist.remove(song)
        return songlist
    
    def filter_search(self, queries, regex=False):
        """a filter (multi) search in which the queries must agree"""
        # Expect that queries is in the form: [[type, args], [type, args]]
        workspace = []
        for pair in queries:
            self.comm.send(2, "searching '%s' '%s'..." % (pair[0], pair[1]))
            workspace.append(self.search(pair[0], pair[1], regex))
        return self.filter_action(workspace)
    
    def total_search(self, queries, regex=False):
        """a do-all search which combines the filter and multi search"""
        # Expect that queries is in the form: ([[type, args],], [[type, args], [type, args],])
        # Thus, the second item will get filtered, and the first will not.
        # This function is deprecated due to complexity.
        songlist = []
        for query in queries:
            if len(query) > 1:
                songlist.extend( self.filter_search(query, regex) )
            else:
                self.comm.send(2, "searching '%s' '%s'..." % (query[0][0], query[0][1]))
                songlist.extend(self.search(query[0][0], query[0][1], regex))
        return songlist

class MpdCommunalError(Exception):
    """If there are any problems in MpdCommunal, then [a derivative of] this will be raised."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MpdCommunalRegexError(MpdCommunalError):
    """If there are problems compiling the regex pattern, MpcRegexError gets raised."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SimpleCommunication():
    """SimpleCommunication is a drop-in class which offers basic console communication."""
    def __init__(self, enable=True):
        self.enabled = enable
    def send(self, level, text):
        if self.enabled: print(text)

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
