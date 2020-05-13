#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Support module for dealing with files.

@author: galdino
"""

import os
import sys
from pathlib import Path
import numpy as np
import datetime
from copy import deepcopy
import collections
from .interact import query_yes_no
import json
import warnings

def checkExtension(filepath, extension):
    """Check if file has desired extension.

    Args:
        filepath (str or pathlib.Path): path to file.
        extension (str): string extension. No need to put dot in front of it.

    Returns
        True if file has an extension and it match with `extension`. False if
        it does not match and -1 if file does not have extension.
    """
    filepath = Path(filepath)
    extension = extension.split('.')[-1]

    a = filepath.name.split('.')
    if len(a) > 1:
        ext = a[-1]
        return extension == ext
    else:
        ext = None
        return -1


def rename_files(fileList, values2keep, separator='_', ask=True):
    """Change the filename pattern of several files.

    Args:
        fileList (str or pathlib.Path): list with full file directory paths.
        separator (str, optional): string that separates information chuncks.
        values2keep (list): Each chunk of information (which is
            separated by "separator") is assigned a number based on its position.
            The first info is 0, then 1, and so on. `values2keep` is a list of which
            info chuncks you want to keep and in which order.
        ask (bool): If true, it shows all the new filenames and asks for
            permission to rename.

    Example:
        Suppose a file naming system with like:

        <folder>/000_58949_test0.txt

        <folder>/001_98769_test1.txt

        ...

        Suppose that we want to rename the file like:

        <folder>/test0_58949.txt

        <folder>/test1_98769.txt

        ...

        Then we would run this function with `values2keep=[2, 1]`.
    """
    if ask:
        print('\n' + '='*20)
        print('The following files will be renamed:\n')

    for filePath in fileList:
        filePath = Path(filePath)

        # temporarily remove extension
        a = filePath.name.split('.')
        if len(a) > 1:
            name = ''.join(a[0:-1])
            ext = a[-1]
        else:
            name = filePath.name
            ext = None

        # new name
        a = name.split(separator)
        nameNew = ''
        for idx in values2keep:
            nameNew = nameNew + a[idx] + '_'

        # put extension back
        if ext is None:
            nameNew = nameNew[:-1]
        else:
            nameNew = nameNew[:-1] + '.' + ext

        if ask:
            # print('\n' + '='*20)
            # print('The following files will be renamed:\n')
            print('OLD NAME = ' + filePath.name)
            print('NEW NAME = ' + nameNew)
            print('\n')
        else:
            filePath.rename(filePath.parent / nameNew)

    if ask:
        y = query_yes_no('Change names?', default="yes")
    else:
        print('\nFiles renamed!')
        # print('\n' + '='*20)
        return
    if y or not ask:
        filenamePattern(fileList, values2keep, separator, ask=False)


def get_fileList(dirpath='.', string='*'):
    """Returns a list with all the files containg `string` in its name.

    Args:
        dirpath (str or pathlib.Path, optional): list with full file directory
        paths.
        string (str, optional): string to look for in file names.

    Return:
        list
    """
    dirpath = Path(dirpath)

    if string is not '*':
        string = '*' + string + '*'
    return list(dirpath.glob(string))


def parse_folder(dirpath='.', string='*', separator_list=['_'], reference_position_list=[0]):
    """Returns a dict where values are the file/folders paths inside dirpath.

    The file names (or folder names) are splited at separator in a list of
    strings. The value at reference_position will be used as key.

    Args:
        dirpath (str or pathlib.Path, optional): directory path.
        string (str, optional): string to look for in file/folder names.
        separator_list (list, optional): list of string that separates
            information chuncks in file names.
        reference_position_list (list, optional): Each chunk of information
            (which is separated by "separator") is assigned a number based on
            its position.
            The first info is 0, then 1, and so on. `reference_position` is a
            index representing which value to use as key.

    Returns:
        dictionary

    Examples:
        Suppose we have a folder with the following subfolders:
            >folder_main
                > 0_data0_300-temp

                > 1_data_316-temp

                > 2_whatever_313-temp

                > 3_anotherData_20-gg

                > ...

        We can easily get the path to the subfolder by using:

        >>> folder_main_p = parse_folder(fullpath_to_folder_main)
        >>> folder_main_p[0]
        fullpath_to_folder_main/0_data0_300-temp
        >>> folder_main_p[3]
        fullpath_to_folder_main/3_anotherData_20-gg

        Or, if we want to parse regarding (300, 316, 313, and 20), we can use:

        >>> folder_main_p = parse_folder(fullpath_to_folder_main, separator_list=['_', '-'], reference_position_list=[2, 0])
        >>> folder_main_p[300]
        fullpath_to_folder_main/0_data0_300-temp
        >>> folder_main_p[20]
        fullpath_to_folder_main/3_anotherData_20-gg
    """
    dirpath = Path(dirpath)

    file_list = get_fileList(dirpath=dirpath, string=string)

    parsed_folder = dict()
    for element in file_list:
        for separator, reference_position in zip(separator_list, reference_position_list):
            try:
                reference = reference.split(separator)[reference_position]
            except:
                reference = element.name.split(separator)[reference_position]
        try:
            if reference.isdigit():
                key = int(reference)
            else:
                key = reference
            parsed_folder[key] = element
        except:
            print('Something went wrong parsing element: ')
            print(element)
        del reference

    return parsed_folder


def save_string(string, filePath='./Untitled.txt', checkOverwrite=False):
    """Save string to txt file.

    Args:
        string (str): string to be saved.
        filePath (str or pathlib.Path, optional): path to save file. If no path
            is given, current working directory is used.
        checkOverwrite (bool, optional): if True, it will check if file exists
            and ask if user want to overwrite file.

    Returns:
        1 if successful or -1 otherwise.
    """
    filePath = Path(filePath)

    if checkOverwrite:
        if filePath.exists() == True:
            if filePath.is_file() == True:
                if query_yes_no('File already exists!! Do you wish to ovewrite it?', 'yes') == True:
                    pass
                else:
                    print('filemanip.saveString ERROR: File not saved.')
                    return -1
            else:
                print('filemanip.saveString WARNING: filePath is pointing to a folder. Saving file as Untitled.txt')
                filePath = filePath/'Untitled.txt'

    f = open(str(filePath), 'w')
    f.write(string)
    f.close()
    return 1


def load_string(filePath):
    """Load string from txt file.

    Args:
        filePath (str or pathlib.Path): file path to load.

    Returns:
        string.
    """
    filePath = Path(filePath)

    f = open(str(filePath), 'w')
    text = f.read(string)
    f.close()
    return text


def save_obj(obj, filepath='./Untitled.txt', checkOverwrite=False):
    """Save object (array, dictionary, list, etc...) to a txt file.

    Args:
        obj (object): object to be saved.
        filepath (str or pathlib.Path, optional): path to save file.
        checkOverwrite (bool, optional): if True, it will check if file exists
            and ask if user want to overwrite file.

    Returns:
        1 if successful or -1 otherwise.
    """
    filepath = Path(filepath)

    if checkOverwrite:
        if filepath.exists() == True:
            if filepath.is_file() == True:
                if query_yes_no('File already exists!! Do you wish to ovewrite it?', 'yes') == True:
                    pass
                else:
                    print('filemanip.save_obj ERROR: File not saved.')
                    return -1
            else:
                print('filemanip.save_obj WARNING: filepath is pointing to a folder. Saving file as Untitled.txt')
                filepath = filepath/'Untitled.txt'

    with open(str(filepath), 'w') as file:
         file.write(json.dumps(obj))
    return 1


def load_obj(filepath):
    """Load object (array, dictionary, list, etc...) from a txt file.

    Args:
        filepath (str or pathlib.Path): file path to load.

    Returns:
        object.
    """
    filepath = Path(filepath)

    with open(str(filepath), 'r') as file:
        obj = json.load(file)
    return obj


def save_data(obj, filepath='./untitled.txt', col_labels=True, data_format='% .10e', header='', footer='', delimiter=',', commentFlag='# ', newline='\n', checkOverwrite=False):
    r"""Save an array or a dictionary in a txt file.

    If obj is a dictionary, the ``col_labels`` are the keys of obj.

    Note:
        Use ``*`` in front of a dict key to not save it to the file.

    Args:
        obj (dict, list, or numpy.array): data to be saved to a file.
        filepath (str or pathlib.Path, optional): path to save file.
        col_labels (bool, optional): When obj is a dictonary, col_labels=true
            makes the dict keys to be added to the header as column labels.
        add2header (str, optional): string to add to the file. Use \\n for new line.
            commentFlag is added automatically.
        data_format (string, or list, optional): If obj is a list, fmt can also
            be a list where each fmt element is associated with a column. If
            obj is a dict, fmt can also be a dict with same keys of obj. Then,
            each fmt value is associated with the corresponding column.

            See `np.savetxt <https://numpy.org/doc/stable/reference/generated/numpy.savetxt.html?highlight=savetxt#numpy.savetxt>`_ documentation::

                fmt = (%[flag]width[.precision]specifier)

            * flag can be: '-' for left justify, '+', whch forces to precede

            * result with + or -, or '0' to Left pad the number with zeros
              instead of space (see width).

            * width is the minimum number of characters to be printed.

            * precision is tipically the number of significant digits

            * specifier is the type of notation. Tipically, either 'e' for
              scientific notation of 'f' for decimal floating point.

            * a common fmt strings is: '%.3f' for 3 decimal places.

        header (str, oprional): string that will be written at the beggining of
            the file.
        footer (str, oprional): string that will be written at the end of the
            file.
        delimiter (str, optional): The string used to separate values.
        commentFlag (str, optional): string that indicate line is a comment.
        newline (str, optional): string separating lines.
        checkOverwrite (bool, optional): if True, it will check if file exists
            and ask if user want to overwrite file.

    Returns:
        1 if successful and -1 otherwise.

    See Also:
        :py:func:`load_data`, :py:func:`~manipUtils.figmanip.setFigurePosition`.
    """
    filepath = Path(filepath)

    if checkOverwrite:
        if filepath.exists() == True:
            if filepath.is_file() == True:
                if query_yes_no('File already exists!! Do you wish to ovewrite it?', 'yes') == True:
                    pass
                else:
                    warnings.warn('File not saved.')
                    return -1
            else:
                warnings.warn('filepath is pointing to a folder. Saving file as Untitled.txt')
                filepath = filepath/'Untitled.txt'

    if type(obj) == dict:
        # remove keys that start with star (*)
        obj2 = {key: obj[key] for key in obj if str(key).startswith('*') is False}

        # col labels
        if col_labels:
            for key in obj2:
                header += str(key) + f'{delimiter}'
            header = header[:-(len(delimiter))]

        # dict to array
        obj = []
        for key in obj2:
            obj.append(obj2[key])
        obj = np.array(obj).transpose()

    np.savetxt(filepath, obj, fmt=data_format, delimiter=delimiter, newline=newline, header=header, footer=footer, comments=commentFlag)
    return 1


def _getComments(filepath, commentFlag='#', stopFlag='#'):
    """Extract comments from text files.

    Comments must be indicated at the begining of the line.

    Args:
        filepath (str or pathlib.Path): fullpath to file
        commentFlag (str, optional): string that indicate line is a comment.
        stopFlag (str, optional): string that indicates line to stop looking for
            comments. Use `None` to read all lines in file (useful for reading
            file with comments not only at the beginning). If `stopFlag` is
            equal to `commentFlag` it will read from the first line with
            `commentFlag` and keep reading until `commentFlag` does not apper
            anymore (useful to read comments at the beginning of a file.

    Returns:
        list with comments or -1 if no comment is found.
    """
    comments = []
    filepath = str(Path(filepath))
    l = len(commentFlag)

    if stopFlag is None:
        with open(filepath) as file:
            for line in file:
                if line[0:l] == commentFlag:
                    comments.append(line[:])
    elif stopFlag == commentFlag:
        with open(filepath) as file:
            comment_started = 0
            for line in file:
                if line[0:l] == commentFlag and comment_started == 0:
                    comments.append(line[:])
                    comment_started = 1
                elif line[0:l] == commentFlag and comment_started == 1:
                    comments.append(line[:])
                elif line[0:l] != commentFlag and comment_started == 1:
                    break
    else:
        with open(fullpath) as file:
            for line in file:
                if line[0:len(stopFlag)] != stopFlag:
                    if line[0:len(commentFlag)] == commentFlag:
                        comments.append(line[:])
                else:
                    comments.append(line[:])
                    break

    if comments == []:
        return -1
    else:
        return comments[:]


def load_data(filepath, delimiter=',', commentFlag='#', col_labels=None, force_array=False):
    """Load data from file saved by manipUtils.filemanip.saveDataDict.

    Actualy, it can load data from any txt file if file is minimally
    properly formated.

    Comments must be indicated at the begining of the line and comments are
    permited only at the begining of the file.

    Args:
        filepath (str or pathlib.Path): path to file
        delimiter (str, optional): The string used to separate values.
            By default, comma (,) is used. If whitespaces are used, any
            consecutive whitespaces act as delimiter and columns must have the
            same lenght. Use \t for tab.
        commentFlag (str, optional): lines starting with commentFlag are disregarded.
        col_labels (list, optional): use this if loading data from a file that does
            not have a header or if you want to change the columns labels imported
            from the file. Its lenght must have the same as the number of
            columns in data. To avoid importing a column, use col_labels and
            put an asterisk (*) in front of the label.
        force_array (bool, optional): By default, load_data will return a
            dictionary. If force_array True, it will return a array.

    Returns
        Dictionary or array. The later is used if no header is found and
        ``col_labels`` is None.

    See Also:
        :py:func:`save_data`.
    """
    filepath = Path(filepath)

    # get header
    header = _getComments(filepath, commentFlag=commentFlag, stopFlag=commentFlag)

    # get data
    if delimiter is ' ':
        delimiter = None
    data = np.genfromtxt(str(filepath), delimiter=delimiter, comments=commentFlag)

    # col_labels
    if col_labels is None:
        if header == -1:
            print('filemanip.load_data WARNING. Cannot find header. Importing an array.')
            return data
        elif force_array:
            return data
        else:
            col_labels = header[-1].replace(commentFlag, '').strip()
            col_labels = col_labels.replace('\n', '').split(delimiter)
            # remove empty itens and trailing spaces
            col_labels = [item.strip() for item in col_labels if item != '']

    # create dict
    datadict = {col_labels[i]: data[:, i] for i in range(len(col_labels)) if not col_labels[i].startswith('*')}
    return datadict













#
# def _getComments(fullpath, commentFlag='#', stopFlag='#H'):
#     """Extract comments from text files.
#
#     Comments must be indicated at the begining of the line.
#
#     Args:
#         fullpath (str or pathlib.Path): fullpath to file
#         commentFlag (str, optional): string that indicate line is a comment.
#         stopFlag (str, optional): string that indicates line to stop looking for
#             comments. Use `None` to read all lines in file (useful for reading
#             file with comments not only at the beginning). If `stopFlag` is
#             equal to `commentFlag` it will read from the first line with
#             `commentFlag` and keep reading until `commentFlag` does not apper
#             anymore (useful to read comments at the beginning of a file.
#
#     Returns:
#         list with comments or -1 if no comment is found.
#     """
#     comments = []
#     fullpath = str(Path(fullpath))
#     l = len(commentFlag)
#
#     if stopFlag is None:
#         with open(fullpath) as file:
#             for line in file:
#                 if line[0:l] == commentFlag:
#                     comments.append(line[:])
#     elif stopFlag == commentFlag:
#         with open(fullpath) as file:
#             comment_started = 0
#             for line in file:
#                 if line[0:l] == commentFlag and comment_started == 0:
#                     comments.append(line[:])
#                     comment_started = 1
#                 elif line[0:l] == commentFlag and comment_started == 1:
#                     comments.append(line[:])
#                 elif line[0:l] != commentFlag and comment_started == 1:
#                     break
#     else:
#         with open(fullpath) as file:
#             for line in file:
#                 if line[0:len(stopFlag)] != stopFlag:
#                     if line[0:len(commentFlag)] == commentFlag:
#                         comments.append(line[:])
#                 else:
#                     comments.append(line[:])
#                     break
#
#     if comments == []:
#         return -1
#     else:
#         return comments[:]
#
#
# def write2file(dictObj, fullpath, add2header='', commentFlag='#', header=True, checkOverwrite=True):
#     r"""Save a dictionary in a txt file.
#
#     Comments must be indicated at the begining of the line. Also, comments can
#     go anywhere in the file, not only at the beggining of the file.
#
#     Dictionary can be recovered by :py:func:`filemanip.loadDict`.
#
#     Note:
#         If the dict values are arrays, consider using :py:func:`filemanip.saveDataDict`.
#
#     Note:
#         Use `*` in front of a dict key to not save it to file.
#
#     Args:
#         dictObj (dict): dictionary to save
#         fullpath (str or pathlib.Path): full path to save file.
#         add2header (str, optional): string to add to the file. Use `\n` for new line.
#             commentFlag is added automatically.
#         commentFlag (str, optional): string that indicate line is a comment.
#         header (bool, optional): True/false to enable/disable header and comments.
#         checkOverwrite (bool, optional): True checks if file exist and ask permission to
#             overwrite it.
#
#     Return:
#         1 if successful and -1 otherwise.
#     """
#     fullpath = Path(fullpath)
#
#     # check overwrite
#     if checkOverwrite is False:
#         pass
#     elif check_overwrite(str(fullpath)):
#         pass
#     else:
#         return -1
#
#
#     file = open(str(Path(fullpath)), 'w')
#
#     # header
#     if header == True:
#         file.write(f'{commentFlag} Created: ' + str(datetime.datetime.now()) + '\n')
#
#         # comments
#         if add2header != '':
#             file.write(f'{commentFlag} ' + str(add2header.replace('\n', f'\n{commentFlag} ')) + '\n')
#
#         # # end header flag
#         # if endHeaderFlag is not None:
#         #     file.write(f'{endHeaderFlag} \n')
#
#     # save
#     try:
#         for item in dictObj:
#             if str(item).startswith('*') == False:
#                 if type(dictObj[item]) is np.ndarray:  # transform to list
#                     dictObj[item] = list(dictObj[item])
#                 line = '{0}: {1}\n'.format(item, dictObj[item])
#                 file.write(line)
#     except:
#         file.close()
#         return -1
#     file.close()
#
#     return 1
#
#
# def loadDict(fullpath, commentFlag='#', evaluate=True):
#     """Load data from file saved by manipUtils.filemanip.saveDict.
#
#     Comments must be indicated at the begining of the line. Also comments can
#     anywhere in the file, not only at the beggining of the file.
#
#     Note:
#         It uses eval function to recover dictionary values.
#
#     Args:
#         fullpath (str or pathlib.Path): path to file.
#         commentFlag (str, optional): lines starting with commentFlag are disregarded.
#         evaluate (bool, optional): If false, dict values are returned as pure strings.
#
#     Returns
#         Dictionary.
#     """
#
#     # Read File and create dict
#     data = dict()
#     with open(str(Path(fullpath))) as f:
#         for line in f:
#             if line[:len(commentFlag)].strip() != commentFlag:
#                 content = ''
#                 parts = line.split(': ')
#                 key = parts[0]
#                 content += ': '.join(parts[1:])
#                 data[key] = content[:-1]
#
#     # Recover data from dict
#     if evaluate ==  True:
#         for key in data:
#             try:
#                 data[key] = eval(data[key].replace('OrderedDict', 'collections.OrderedDict'))
#             except NameError:
#                 data[key] = data[key]
#     return data
#
#
# def saveDataDict(data, fullpath='./untitled.txt', add2header='', delimiter=',', commentFlag='#', keyFlag=None, keyList=None, header=True, checkOverwrite=True):
#     r"""Save a dict of arrays in a txt file. Header is based on the dict keys.
#
#     Dictionary can be recovered by :py:func:`filemanip.loadDataDict`.
#
#     Note:
#         Use `*` in front of a dict key to not save it to file.
#
#     Args:
#         data (dict): dictionary with data.
#         fullpath (str or pathlib.Path, optional): full path to save file
#             [default= './untitled.txt']
#         add2header (str, optional): string to add to the file. Use `\n` for new line.
#             commentFlag is added automatically.
#         delimiter (str, optional): The string used to separate values.
#         commentFlag (str, optional): string that indicate line is a comment.
#         keyFlag (str, optional): string that indicate that line is a list with
#             dict keys.
#         keyList (list, optional): string to be used as header. Overwrites auto header
#             generation based on dict keys.
#         header (bool, optional): True/false to enable/disable header and comments.
#         ignoreOverwrite (bool, optional): if `True`, it overwrites files
#             without asking for permission.
#
#     Return
#         1 if successful and -1 otherwise.
#     """
#     fullpath = Path(fullpath)
#
#     # check overwrite
#     if checkOverwrite is False:
#         pass
#     elif check_overwrite(str(fullpath)):
#         pass
#     else:
#         return -1
#
#     # deals with star keys (*)
#     temp = {key: data[key] for key in data if str(key).startswith('*') is False}
#
#     # initialize file
#     file = open(str(fullpath), 'w')
#
#     # header
#     if header == True:
#         file.write(f'{commentFlag} Created: ' + str(datetime.datetime.now()) + '\n')
#
#         # comments
#         if add2header != '':
#             file.write(f'{commentFlag} ' + str(add2header.replace('\n', f'\n{commentFlag} ')) + '\n')
#
#         # keyline
#         if keyFlag is None:
#             keyFlag = commentFlag
#         if keyList is None:
#             keyLine = ''
#             for i in temp:
#                 if i == list(temp.keys())[-1]:
#                     keyLine += str(i) + '\n'
#                 else:
#                     keyLine += str(i) + f'{delimiter}'
#         file.write(f'{keyFlag} {keyLine}')
#
#     # save data
#     for j in range(0, max([len(temp[x]) for x in temp])):
#         line = ''
#         for i in temp:
#             if i == list(temp.keys())[-1]:  # last item
#                 try:
#                     line += str(temp[i][j]) + '\n'
#                 except IndexError:
#                     line += '\n'
#             else:
#                 try:
#                     line += str(temp[i][j]) + f'{delimiter}'
#                 except IndexError:
#                     line += f'{delimiter}'
#         file.write(line)
#     file.close()
#
#
# def loadDataDict(fullpath, delimiter=',', useCols=None, commentFlag='#', keyDelimiter=None, keyFlag=None, keyList=None):
#     """Load data from file saved by manipUtils.filemanip.saveDataDict.
#
#     Actualy, it can load data from any txt file if file is minimally
#     properly formated.
#
#     Comments must be indicated at the begining of the line and comments are
#     permited only at the begining of the file.
#
#     Args:
#         fullpath (str or pathlib.Path): path to file
#         delimiter (str, optional): The string used to separate values.
#             By default, comma (,) is used. If whitespaces are used, any
#             consecutive whitespaces act as delimiter and columns must have the
#             same lenght. Use \t for tab.
#         useCols (list, optional): Which columns to read, with 0 being the first. You Can
#             use numbers (int) or strings, where string must match with header strings
#             in the file. You may mix numbers and strings, in this case
#             numbers are accounted first, than the strings.
#         commentFlag (str, optional): lines starting with commentFlag are disregarded.
#         keyFlag (str, optional): It searchs the beginning of the file (before data
#             starts) for a line with this flag and creates dict keys based on
#             this line. If `None`, it will try to create header from the last
#             header line before data starts.
#         keyDelimiter (str, optional): If not None, it will use keyDelimiter to
#         separate header keys. Useful when delimiter from data is different from
#         keys delimiter.
#         keyList (list, optional): use this if loading data from a file that does
#             not have a header or if you want to change the columns labels imported
#             from the file. It creates dict keys based on `keyList`.
#             If `keyList` smaller than `useCols` than extra itens in `useCols`
#             are ignored.
#
#     Returns
#         Dictionary.
#     """
#     fullpath = Path(fullpath)
#
#     if delimiter is ' ':
#         delimiter = None
#
#     # adjust usecols
#     useCols2 = deepcopy(useCols)
#     if useCols2 is not None:
#         useCols = [number for number in useCols if type(number) == int]
#         useKeys = [key for key in useCols2 if type(key) == str]
#     else:
#         useKeys = None
#
#     # get header
#     if keyFlag is None:
#         keyFlag = commentFlag
#     header = _getComments(fullpath, commentFlag=commentFlag, stopFlag=keyFlag)
#
#     # get header from file (keylist2 -> total key list from file)
#     if (useKeys is None or useKeys == []) and keyList is not None:
#         pass
#     else:
#         if header == -1:
#             print('Error. Cannot find header, Use keyList to manually add header.')
#             return -1
#         if keyDelimiter is None:
#             keyDelimiter=delimiter
#         keyList2 = header[-1].replace(keyFlag, '').strip()
#         keyList2 = keyList2.replace('\n', '').split(keyDelimiter)
#         # remove empty itens and trailing spaces
#         keyList2 = [item.strip() for item in keyList2 if item != '']
#         # keyList2 = keyList2[1:]#.replace(keyFlag, '').strip()
#
#     # add itens to useCols
#     if useKeys is not None:
#         for key in useKeys:
#             if key in keyList2:
#                 useCols.append(keyList2.index(key))
#
#     # add itens to keylist
#     if keyList is None and useCols != None:
#         keyList = [keyList2[i] for i in useCols]
#     elif keyList is None and useCols is None:
#         keyList = keyList2
#
#     # get data
#     data = np.genfromtxt(str(fullpath), delimiter=delimiter, usecols=useCols)
#
#     datadict = dict()
#     for i in range(len(keyList)):
#         name = keyList[i]
#         try:
#             data_temp = data[:, i]
#
#         except IndexError:
#             if len(keyList) == 1:
#                 data_temp = data[:]
#             else:
#                 data_temp = data[i]
#         if np.isin('nan', data_temp):
#             first_nan = np.where(np.isnan(data_temp))[0][0]
#             datadict[name] = data_temp[:first_nan]
#         else:
#             if len(keyList) == 1:
#                 datadict[name] = data_temp[:]
#             else:
#                 datadict[name] = data_temp
#
#     return datadict
#
#
# def check_overwrite(filePath):
#     """Check if file exists and prompt user for overwriting privileges.
#
#     Args:
#         filePath (str or pathlib.Path): file directory path.
#
#     Returns:
#         True if file does not exist or if it exists and overwrite is permited.
#             False otherwise.
#     """
#     if Path(filePath).is_file() or Path(filePath).is_dir():
#         print('\nFile: ' + str(filePath))
#         if query_yes_no('File/folder already exists!! Do you wish to ovewrite it?', 'no') == True:
#             return True
#         else:
#             return False
#     else:
#         return True
#
#
# def check_path_exists(*args):
#     """Check if paths exists.
#
#     Args:
#         *args (str, pathlib.Path): one path or a sequence of paths.
#
#     Returns:
#         list with string (abs path) if corresponding path exists
#         or -1 otherwise.
#     """
#     abs = []
#
#     for path in args:
#         path = Path(path)
#
#         if path.is_file() == False and path.is_dir() == False:
#             abs.append(-1)
#             # msg.append(f'ERROR: Cannot find {path}')
#         else:
#             abs.append(str(path.resolve()))
#             # msg.append(f'Found {path.resolve()}')
#     return abs






# def get_fileDict(fullpath='.', string='*', separator_list=['_'], reference_position_list=[0]):
#     """Returns a list with all the files containg `string` in its name.
#
#     Args:
#         fullpath (str or pathlib.Path, optional): list with full file directory
#             paths.
#         string (str, optional): string to look for in file names.
#         separator_list (list, optional): list of string that separates
#             information chuncks in file names.
#         reference_position_list (list, optional): Each chunk of information
#             (which is separated by "separator") is assigned a number based on
#             its position.
#             The first info is 0, then 1, and so on. `reference_position` is a
#             index representing which value to use as key.
#
#     Note:
#         The separator_list and reference_position_list are looped simutaneously,
#         and each separator is associated with a reference position.
#
#     Examples:
#
#
#     Return:
#         Dict
#     """
#     file_list = get_fileList(fullpath=fullpath, string=string)
#
#     file_dict = dict()
#     for path in file_list:
#         for separator,reference_position in zip(separator_list, reference_position_list):
#             try:
#                 reference = reference.split(separator)[reference_position]
#             except:
#                 reference = path.name.split(separator)[reference_position]
#         try:
#             if reference.isdigit():
#                 key = int(reference)
#             else:
#                 key = reference
#             file_dict[key] = path
#         except:
#             print('Something went wrong parsing element: ')
#             print(path)
#         del reference
#
#     return file_dict
