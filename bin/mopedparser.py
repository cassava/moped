#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mopedparser.py

# This is the argument parsing development file for Moped 2.0
# This is one of my masterpieces, version 1.0 completed
# at 1:11am the 27th of November 2008
# Ben Morgan

name = "Moped Argument Parser"
version = "1.4.1"
author = "Ben Morgan"
date = "6th of September, 2009"
license = "GNU General Public License"
email = "uv.sound@gmail.com"

import re
import random

import stringutils


class ArgumentParser():
    """ArgumentParser takes care of argument parsing in Moped.
    In most cases, calling parse_argument_string(string) will suffice.
    """
    
    def __init__(self, mpdcommunal):
        self.mpc = mpdcommunal
        self.syntax_pattern = '[r+!]*<[^>]*>|[\\w!]+:.*?(?= [\\w!]+:| [r+!]*<|$)|^ ?.*?(?= [\\w!]+:| [r+!]*<|$)'
        self.escapable_chars = {'\'':'&squo;',
                                '"':'&dquo;',
                                '<':'&lt;',
                                '>':'&gt;',
                                ':':'&colon;'
                                }
        self.escaped_chars = {'&squo;':'\'',
                              '&dquo;':'"',
                              '&lt;':'<',
                              '&gt;':'>',
                              '&colon;':':'
                              }
        self.valid_flags = {'!':'exclude',
                            'r':'remove',
                            '+':'nofilter',
                            'e':'regex',
                            'm':'multiple',
                            's':'single',
                            '=':'noshuffle',
                            '~':'shuffle',
                            }
        self.search_shortcuts = {'a':'artist',
                                 'b':'album',
                                 't':'title',
                                 'n':'track',
                                 'g':'genre',
                                 'y':'year',
                                 'f':'file',
                                 'x':'any'
                                 }
        self.default_search = 't'
        self.default_song_grouping = 's'
        self.check_for_errors = True
        self.remove_duplicates = True
        self.shuffle = True
        self.shuffle_intelligent = False
        self.shuffle_criteria = 'a'
        # The shuffle_xfactor setting is a tricky one. Put it too high,
        # and you will have an evenly distributed playlist, but only in
        # the beginning. Make it too low and it becomes much more random
        # as opposed to ordered. Thus, an xfactor of 1 is totally random.
        self.shuffle_xfactor = 1.75
        self.not_found = []
        self.filter_not_found = []
        
    
    def __is_escaped_in_quotes(self, string, location):
        """Internal function to help determine whether a character should be
        escaped or not. Only works with replace_innocent_characters().
        """
        single = string.count('\'', 0, location)
        double = string.count('"', 0, location)
        # now test to see if any are implicitly escaped
        if string[location] == '\'':
            # test single quotes
            if double % 2 == 1:
                return True
        elif string[location] == '"':
            # test double quotes
            if single % 2 == 1:
                return True
        else:
            # test whatever character
            if double % 2 == 1:
                return True
            elif single % 2 == 1:
                return True
        # in this case it is the real deal
        return False
    
    def songlist_search(self, songlist, search, pattern):
        results = []
        pattern = pattern.lower()
        if search == 'any':
            for song in songlist:
                for search_id in song:
                    if search_id.lower().find(pattern) > -1:
                        results.append(song)
                        break
        else:
            for song in songlist:
                try:
                    if song[search].lower().find(pattern) > -1:
                        results.append(song)
                except KeyError:
                    # In case it is a directory...
                    pass
        return results
    
    def ishuffle(self, songlist):
        """Intelligent shuffling which uses an algorithm to shuffle"""
        # This is a CPU intensive process, thus it is recommended
        # to only use this function on small songlists.
        criteria = self.search_shortcuts[self.shuffle_criteria]
        # Sort songs into a dictionary based on the criteria
        dictionary = {}
        for song in songlist:
            if song[criteria] not in dictionary:
                dictionary[song[criteria]] = []
            dictionary[song[criteria]].append(song)
        # The probability starts with the number of songs
        # Maybe using a list would be better?
        probabilities = {}
        for key in dictionary:
            probabilities[key] = len(dictionary[key])
        # Start the sorting process
        shuffled_list = []
        while( len(dictionary) > 0 ):
            # Populate the probability list
            population = []
            for key in probabilities:
                for i in range(probabilities[key]):
                    population.append(key)
            # Choose the lucky one
            choice = random.choice(population)
            song = random.choice(dictionary[choice])
            shuffled_list.append(song)
            dictionary[choice].remove(song)
            # Adjust the probabilities and dictionary
            length = len(dictionary[choice])
            if length > 0:
                probabilities[choice] = length
            else:
                del dictionary[choice]
                del probabilities[choice]
            for key in probabilities:
                if key != choice:
                    probabilities[key] = int(probabilities[key] * self.shuffle_xfactor)
        # Return the list that has been shuffled
        return shuffled_list
    
    def unique(self, List):
        """Makes sure that every item inside is unique"""
        i = 0
        while i < len(List):
            try:
                del inlist[List.index(List[i], i + 1)]
            except:
                i += 1
        return List
    
    def replace_section(self, string, new, start, end=None):
        """Replace a section in a string with new"""
        if end is None:
            end = start + 1
        return string[:start] + new + string[end:]
    
    def sanitize(self, string):
        """Replace explicitely and implicitely escaped characters in string
        as defined by ArgumentParser.escabable_chars.
        Returns sanitized string.
        """
        # Replace the explicitely escaped characters
        for char in self.escapable_chars:
            string = string.replace('\\'+char, self.escapable_chars[char])
        # Replace the implicitely escaped characters in [:<>'"],
        # that is, those that are found inside a pair of quotes
        starting_position = 0
        while True:
            break_outer = True
            for location in range(starting_position, len(string)):
                if string[location] in self.escapable_chars:
                    if self.__is_escaped_in_quotes(string, location):
                        starting_position = location + len(self.escapable_chars[string[location]])
                        string = self.replace_section(string, self.escapable_chars[string[location]], location)
                        break_outer = False
                        break
            if break_outer: break
        # Return the sanitized string
        return string
    
    def restore(self, string):
        """Restore the internally escaped characters with their originals"""
        for char in self.escaped_chars:
            string = string.replace(char, self.escaped_chars[char])
        return string
    
    def syntax_check(self, string):
        """Check for syntax errors in a sanitized string,
        If an error is found, then MopedSyntaxError is raised.
        """
        if string.count('<') != string.count('>'):
            raise MopedSyntaxError("There are an unequal amount of '<' and '>' signs", string)
        elif string.count('\'') % 2 != 0:
            raise MopedSyntaxError("There is an odd number of single quotation marks", string)
        elif string.count('"') % 2 != 0:
            raise MopedSyntaxError("There is an odd number of double quotation marks", string)
        elif string.count('<') > 1:
            raise MopedSyntaxError("There are more than one '<' chars", string)
        elif string.count('>') > 1:
            raise MopedSyntaxError("There are more than one '>' chars", string)
    
    def separate_into_units(self, string, pattern=None):
        """Take a sanitized string and split it into separate strings"""
        if pattern is None:
            pattern = self.syntax_pattern
        parser = re.compile(pattern)
        results = []
        match = ''
        while True:
            if string == '': break
            m = parser.search(string)
            if m is not None:
                match = m.group()
                results.append(match)
                string = string.replace(match, '', 1).strip()
            else:
                break
        return results
    
    def parse_argument_list(self, unit_list):
        """Takes list units and returns tuple (insert_list, remove_list)"""
        insert_list = []
        remove_list = []
        exclude_from_insert = []
        exclude_from_remove = []
        # Fill up the four different lists by going through each unit
        self.mpc.update()
        for unit in unit_list:
            if '<' in unit:
                flags, string = self._parse_group(unit)
                songlist = self._process_group(flags, string)
            else:
                flags, search, string = self._parse_unit(unit)
                songlist = self._process_unit(flags, search, string)
            # Now determine to which list to add it to
            if 'r' in flags:
                if '!' in flags:
                    exclude_from_remove.extend(songlist)
                else:
                    remove_list.extend(songlist)
            elif '!' in flags:
                exclude_from_insert.extend(songlist)
            else:
                insert_list.extend(songlist)
        # From the lists, remove what is to be excluded
        insert_list = self.mpc.filterout_action(insert_list, exclude_from_insert)
        remove_list = self.mpc.filterout_action(remove_list, exclude_from_remove)
        # Return the two lists
        return insert_list, remove_list
    
    def _parse_unit(self, string):
        """Parse a unit with all of its flags"""
        split = string.split(':')
        # What if there was just a search term?
        if len(split) > 1:
            all_flags = split[0]
            pattern = split[1].strip()
        else:
            all_flags = self.default_search
            pattern = string.strip()
        # Append the correct flags to their appropriate destinations
        flags = ''
        search = ''
        for char in all_flags:
            if char in self.valid_flags:
                flags += char
            elif char in self.search_shortcuts:
                search += char
        return flags, search, pattern
    
    def _process_unit(self, flags, search, string):
        """Takes a parsed unit, processes it and returns a list of songs"""
        # Every mpdcommunal search is called out from this function.
        # All the final expanding of shortcuts and escapes are done here.
        # First start with the prep work:
        if ('m' not in flags) and ('s' not in flags):
            if len(search) > 1:
                flags += 'm'
            else:
                flags += self.default_song_grouping
        searches = []
        for char in search:
            searches.append(self.search_shortcuts[char])
        regex = ('e' in flags)
        songlist = []
        # Determine whether there are more queries or not, and act accordingly:
        if 'm' in flags:
            arguments = stringutils.split(string)
            # If there are not enough search types for all the arguments,
            # then copy the last one for all of the rest.
            while len(searches) < len(arguments):
                searches.append(searches[-1])
            for i in range( len(arguments) ):
                restored_text = self.restore(arguments[i])
                search_list = self.mpc.search(searches[i], restored_text, regex)
                if len(search_list) == 0:
                    self.not_found.append([searches[i], restored_text, regex])
                else:
                    songlist.extend(search_list)
        else:
            # Even though this is a single word, it still needs to be split
            # in order to get rid of the quotes
            string = ' '.join(stringutils.split(string))
            restored_text = self.restore(string)
            songlist = self.mpc.search(searches[0], restored_text, regex)
            if len(songlist) == 0:
                self.not_found.append([searches[0], restored_text, regex])
        return songlist
    
    def _parse_group(self, string):
        """Parse a [filter] group with all of its flags"""
        flags = string[:string.find('<')]
        args = string[string.find('<')+1:-1]
        return flags, args
    
    def _process_group(self, flags, string):
        """Takes a parsed group, processes it and returns a list of songs"""
        # Receives a string without the '<' and the '>' characters
        units = self.separate_into_units(string)
        songlist = []
        # Determine what kind of group it is and what action is necessary
        if '+' in flags:
            excludelist = []
            for unit in units:
                uflags, usearch, ustring = self._parse_unit(unit)
                if '!' in uflags:
                    excludelist.extend( self._process_unit(uflags, usearch, ustring) )
                else:
                    songlist.extend( self._process_unit(uflags, usearch, ustring) )
        else:
            list_of_songlists = []
            for unit in units:
                uflags, usearch, ustring = self._parse_unit(unit)
                list_of_songlists.append( self._process_unit(uflags, usearch, ustring) )
            songlist = self.mpc.filter_action(list_of_songlists)
        if len(songlist) == 0:
            #note: consider not reporting if + is in the flags
            self.filter_not_found.append([string, flags])
        # Everything sorted, '!' and 'r' flags are handled by the caller
        return songlist
    
    def post_process(self, songlist):
        """Perform various processing to the final level"""
        # Shuffling as well as removing duplicates happen here.
        # This is an experimental function!
        if self.remove_duplicates:
            songlist = self.unique(songlist)
        if self.shuffle:
            if self.shuffle_intelligent:
                songlist = self.ishuffle(songlist)
            else:
                random.shuffle(songlist)
        return songlist
    
    def process(self, string):
        """This is the main function of this class.
        It takes the raw string of arguments and parses them,
        returning a tuple of lists (insert_list, remove_list).
        """
        # Check first that it's not empty
        string = string.strip()
        # Otherwise sanitize will escape characters that shouldn't be,
        # Because sometimes an input string will come in quotes, like
        # if it is from bash.
        string = string.strip("'")
        if string == '':
            return ([], [])
        # The given string represents the entire argument string,
        # which may look like: "a: artist ts: one track\'s +<a: group b:album>"
        # 1. replace the innocent characters -- that are not syntax
        #    get a string back: "a: artist ts: one track&squo;s +<a: group b:album>"
        string = self.sanitize(string)
        # 2. Now take the sanitized string and break it into a list
        #    get a list back: ["a: artist", "ts: one track&squo;s", "+<a: group b:album>"]
        unit_list = self.separate_into_units(string)
        # 3. In each of the units, check for errors, raise upon finding one
        if self.check_for_errors:
            for unit in unit_list:
                self.syntax_check(unit)
        # If it gets this far, then there are presumably no obvious errors,
        # If error checking is disabled, the overall results are unforeseeable.
        # 4. Hand the whole list to parse_argument_list, which will take the whole
        #    level, process it quite a bit, hand off jobs to other functions,
        #    and eventually returns a list of songs to insert and remove.
        #    parse_argument_list(unit_list) is quite high level still.
        insert_list, remove_list = self.parse_argument_list(unit_list)
        # 5. Extra processing -- shuffling or removing duplicates
        if self.shuffle or self.remove_duplicates:
            insert_list = self.post_process(insert_list)
        # 6. Finally, return the lists of songs
        return (insert_list, remove_list)

class MopedError(Exception):
    """A generic error which Moped may raise"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MopedSyntaxError(MopedError):
    """Raised if there is a syntax error in the command line arguments"""
    def __init__(self, value, string):
        """value: what the error was
        string: what string triggered the error
        """
        self.value = value
        self.string = string
        self.representation = value + ': ' + string
    def __str__(self):
        return repr(self.representation)

