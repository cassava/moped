#!/usr/bin/env python
# -*- coding: utf-8 -*-
# stringutils.py

# Various functions pertaining to Strings
# Copyright © 2004, 2008, 2011 Ben Morgan <neembi@googlemail.com>
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

# Unix style quote splitting
def split(string):
    """Split up a string, paying attention to quotes; returns a list."""
    results = [[], []]
    level = 0
    free = True
    single = False
    for word in string.split():
        if free and (word.count('"') % 2 == 1):
            level += 1
            free = False
            single = False
            word = word.replace('"', '')
        elif free and (word.count('\'') % 2 == 1):
            level += 1
            free = False
            single = True
            word = word.replace('\'', '')
        elif free and (word.count('"') == 2):
            word = word.replace('"', '')
        elif free and (word.count('\'') == 2):
            word = word.replace('\'', '')
        elif not free and not single and (word.count('"') % 2 == 1):
            results[level].append(word.replace('"', ''))
            word = ' '.join(results[level])
            results[level] = []
            free = True
            level -= 1
        elif not free and single and (word.count('\'') % 2 == 1):
            results[level].append(word.replace('\'', ''))
            word = ' '.join(results[level])
            results[level] = []
            free = True
            level -= 1
        
        results[level].append(word)
    
    return results[0]


def join(List):
    """Join a string, paying attention to whether the word was surrounded by quotes"""
    results = []
    for item in List:
        if (' ' in item) or ('\n' in item) or ('\t' in item):
            quote = ('\'' in item and '"' or '\'')
            results.append(quote + item + quote)
        else:
            results.append(item)
    return ' '.join(results)


def numbers(str_input, return_code=0, as_string=False, output_type='float'):
    """Extracts numbers from a string and then returns them"""
    # Written May 2004
    # str_input    =   string to search: required
    # return_code  =   value returned upon failure: [0]
    # as_string    =   if the above is a list or tuple, returns a list of strings only: [0] or 1
    # output_type  =   return types as integer|[float]. If type is integer, dots will be ignored

    previous_char = [['', False], ['', False], ['', False]]; olist = [[]]
    numbercount = 0; isfloatnumber = False

    # Seperate numbers and add to list
    for char in str_input:
        # Add any numberical digits adjacent to each other to the list
        # Include the dots if they are surrounded by numbers
        previous_char[2] = previous_char[1][:]
        previous_char[1] = previous_char[0][:]
        previous_char[0] = [char, False]
        if char.isdigit():
            # The character is a digit, so specify that it is
            previous_char[0] = [char, True]

            # Incrementing the number in the list
            if previous_char[1][1] == False:
                # But not if the previous character is a dot (for floats)
                # or if the list is empty (numbers need to be added)
                if (previous_char[1][0] != '.') and (olist[0] != []):
                    olist.append([])
                    numbercount += 1
                    isfloatnumber = False
            
            # Used to check to see for floating point numbers
            if output_type == 'float':
                if isfloatnumber == False:
                    if (previous_char[2][1] == True) and (previous_char[1][0] == '.'):
                        olist[numbercount].append(previous_char[1][0])
                        isfloatnumber = True

            # Add number to list
            olist[numbercount].append(char)

    if not as_string:
        nlist = []
        for object in [float(''.join(item)) for item in olist]:
            # Convert values that don't need to be float back to integers
            if str(object)[-2] == '.': object = int(object)
            # Now add object to the list
            nlist.append(object)
        # Return the final tuple
        return tuple(nlist)

    # We will return it as a string:
    return tuple([''.join(item) for item in olist])


def onenumber(str_input, return_code=0, output_type='integer'):
    """Find the numbers in a string and return them as the specified output_type"""
    # Written May 2004
    # str_input    =   string to search
    # return_code  =   value returned upon failure
    # output_type  =   value returned normally: integer|float|Decimal
    
    previous_char = [['', False], ['', False], ['', False]]; newlist = []
    isfloatnumber = False
    
    for char in str_input:
        # Add any numerical digits to the list
        # Includes dots if surrounded by numbers
        # However, only 1 dot is included.
        previous_char[2] = previous_char[1][:]
        previous_char[1] = previous_char[0][:]
        previous_char[0] = [char, False]
        if '0' <= char <= '9':
            # Used to check to see for floating point numbers
            if output_type == 'float':
                if isfloatnumber == False:
                    if (previous_char[2][1] == True) and (previous_char[1][0] == '.'):
                        newlist.append(previous_char[1][0])
                        isfloatnumber = True
            newlist.append(char)
            previous_char[0] = [char, True]
            
    # If the string does not contain any numbers
    if not newlist: return return_code
    # Convert the string to a specified format and return it
    if output_type == 'float':
        return float(''.join(newlist))
    elif output_type == 'Decimal':
        return decimal.Decimal(''.join(newlist))
    else: # output_type is 'integer' or undefined
        return int(''.join(newlist))


def whitenums(str_input, return_code=[0], as_string=0, onenumber_arg='float'):
    """Extracts numbers from a string and then returns a list"""
    # Written May 2004
    # Arguments surrounded by squared brackets are the default values
    # str_input    =   string to search: required
    # !(use_punct) =   included punctuation as delimeter as well] <-- Not Implemented Yet
    # return_code  =   value returned upon failure: [0]
    # as_string    =   returns a list of strings only: [0] or 1
    # numbers_arg  =   arguments for function numbers: integer|[float]
    # whitespace   =   use only whitespace to seperate: [0] or 1

    oldlist = (str_object for str_object in str_input.split())
    newlist = []
    for object in oldlist:
        tempvalue = onenumber(object, "None", onenumber_arg)
        # print "%s = %s" % (object, tempvalue)  # useful for debugging
        if not tempvalue == "None":
            # Convert values that don't need to be float back to integers
            if str(tempvalue)[-2] == '.': tempvalue = int(tempvalue)
            # If we should return it as string, do the conversion
            if as_string: tempvalue = str(tempvalue)
            # Now add tempvalue to the list
            newlist.append(tempvalue)
    # If the list is empty
    if not newlist: return return_code
    return newlist

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
