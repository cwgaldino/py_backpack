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
from .genmanip import query_yes_no


def check_overwrite(filePath):
    """Check if file exists and prompt user for overwriting privileges.

    Args:
        filePath (str or pathlib.Path): file directory path.

    Returns:
        True if file does not exist or if it exists and overwrite is permited.
            False otherwise.
    """
    if Path(filePath).is_file() or Path(filePath).is_dir():
        print('\nFile: ' + str(filePath))
        if query_yes_no('File/folder already exists!! Do you wish to ovewrite it?', 'no') == True:
            return True
        else:
            return False
    else:
        return True


def check_path_exists(*args):
    """Check if paths exists.

    Args:
        *args (str, pathlib.Path): one path or a sequence of paths.

    Returns:
        list with either abs path if corresponding path exists or -1 otherwise.
    """
    abs = []
    # flag = 1
    # msg = []
    for path in args:
        path = Path(path)

        if path.is_file() == False and path.is_dir() == False:
            abs.append(-1)
            # msg.append(f'ERROR: Cannot find {path}')
        else:
            abs.append(str(path.resolve()))
            # msg.append(f'Found {path.resolve()}')
    # if -1 in abs:
    #     flag = -1
    return abs#flag, #, msg


def saveString(string, folder='.', filename='Untitled.txt'):
    """Save string to txt file.

    Args:
        folder (str or pathlib.Path, optional): path to save file. If no path
            is given, current working directory is used.
        filename (str, optional): file name.

    Returns:
        1 if successful or -1 otherwise.
    """
    # check folder exist
    if folder == '.':
        folder = Path.cwd()
    else:
        folder = Path(folder)
        if folder.is_dir() == False:
            print(f'ERROR: {folder} does not exist.')
            print('File not created.')
            return -1

    f = open(str(folder/filename), 'w')
    f.write(string)
    f.close()
    return 1


def _getComments(fullpath, commentFlag='#', stopFlag='#H'):
    """Extract comments from text files.

    Comments must be indicated at the begining of the line.

    Args:
        fullpath (str or pathlib.Path): fullpath to file
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
    fullpath = str(Path(fullpath))
    l = len(commentFlag)

    if stopFlag is None:
        with open(fullpath) as file:
            for line in file:
                if line[0:l] == commentFlag:
                    comments.append(line[:])
    elif stopFlag == commentFlag:
        with open(fullpath) as file:
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


def saveDict(dictObj, fullpath, add2header='', commentFlag='#', header=True, checkOverwrite=True):
    r"""Save a dictionary in a txt file.

    Comments must be indicated at the begining of the line. Also, comments can
    go anywhere in the file, not only at the beggining of the file.

    Dictionary can be recovered by :py:func:`filemanip.loadDict`.

    Note:
        If the dict values are arrays, consider using :py:func:`filemanip.saveDataDict`.

    Note:
        Use `*` in front of a dict key to not save it to file.

    Args:
        dictObj (dict): dictionary to save
        fullpath (str or pathlib.Path): full path to save file.
        add2header (str, optional): string to add to the file. Use `\n` for new line.
            commentFlag is added automatically.
        commentFlag (str, optional): string that indicate line is a comment.
        header (bool, optional): True/false to enable/disable header and comments.
        checkOverwrite (bool, optional): True checks if file exist and ask permission to
            overwrite it.

    Return:
        1 if successful and -1 otherwise.
    """
    fullpath = Path(fullpath)

    # check overwrite
    if checkOverwrite is False:
        pass
    elif check_overwrite(str(fullpath)):
        pass
    else:
        return -1


    file = open(str(Path(fullpath)), 'w')

    # header
    if header == True:
        file.write(f'{commentFlag} Created: ' + str(datetime.datetime.now()) + '\n')

        # comments
        if add2header != '':
            file.write(f'{commentFlag} ' + str(add2header.replace('\n', f'\n{commentFlag} ')) + '\n')

        # # end header flag
        # if endHeaderFlag is not None:
        #     file.write(f'{endHeaderFlag} \n')

    # save
    try:
        for item in dictObj:
            if str(item).startswith('*') == False:
                if type(dictObj[item]) is np.ndarray:  # transform to list
                    dictObj[item] = list(dictObj[item])
                line = '{0}: {1}\n'.format(item, dictObj[item])
                file.write(line)
    except:
        file.close()
        return -1
    file.close()

    return 1


def loadDict(fullpath, commentFlag='#', evaluate=True):
    """Load data from file saved by manipUtils.filemanip.saveDict.

    Comments must be indicated at the begining of the line. Also comments can
    anywhere in the file, not only at the beggining of the file.

    Note:
        It uses eval function to recover dictionary values.

    Args:
        fullpath (str or pathlib.Path): path to file.
        commentFlag (str, optional): lines starting with commentFlag are disregarded.
        evaluate (bool, optional): If false, dict values are returned as pure strings.

    Returns
        Dictionary.
    """

    # Read File and create dict
    data = dict()
    with open(str(Path(fullpath))) as f:
        for line in f:
            if line[:len(commentFlag)].strip() != commentFlag:
                content = ''
                parts = line.split(': ')
                key = parts[0]
                content += ': '.join(parts[1:])
                data[key] = content[:-1]

    # Recover data from dict
    if evaluate ==  True:
        for key in data:
            try:
                data[key] = eval(data[key].replace('OrderedDict', 'collections.OrderedDict'))
            except NameError:
                data[key] = data[key]
    return data


def saveDataDict(data, fullpath, add2header='', delimiter=',', commentFlag='#', keyFlag=None, keyList=None, header=True, checkOverwrite=True):
    r"""Save a dict of arrays in a txt file. Header is based on the dict keys.

    Dictionary can be recovered by :py:func:`filemanip.loadDataDict`.

    Note:
        Use `*` in front of a dict key to not save it to file.

    Args:
        data (dict): dictionary with data.
        fullpath (str or pathlib.Path): full path to save file.
        add2header (str, optional): string to add to the file. Use `\n` for new line.
            commentFlag is added automatically.
        delimiter (str, optional): The string used to separate values.
        commentFlag (str, optional): string that indicate line is a comment.
        keyFlag (str, optional): string that indicate that line is a list with
            dict keys.
        keyList (list, optional): string to be used as header. Overwrites auto header
            generation based on dict keys.
        header (bool, optional): True/false to enable/disable header and comments.
        ignoreOverwrite (bool, optional): if `True`, it overwrites files
            without asking for permission.

    Return
        1 if successful and -1 otherwise.
    """
    fullpath = Path(fullpath)

    # check overwrite
    if checkOverwrite is False:
        pass
    elif check_overwrite(str(fullpath)):
        pass
    else:
        return -1

    # deals with star keys (*)
    temp = {key: data[key] for key in data if str(key).startswith('*') is False}

    # initialize file
    file = open(str(fullpath), 'w')

    # header
    if header == True:
        file.write(f'{commentFlag} Created: ' + str(datetime.datetime.now()) + '\n')

        # comments
        if add2header != '':
            file.write(f'{commentFlag} ' + str(add2header.replace('\n', f'\n{commentFlag} ')) + '\n')

        # keyline
        if keyFlag is None:
            keyFlag = commentFlag
        if keyList is None:
            keyLine = ''
            for i in temp:
                if i == list(temp.keys())[-1]:
                    keyLine += str(i) + '\n'
                else:
                    keyLine += str(i) + f'{delimiter}'
        file.write(f'{keyFlag} {keyLine}')

    # save data
    for j in range(0, max([len(temp[x]) for x in temp])):
        line = ''
        for i in temp:
            if i == list(temp.keys())[-1]:  # last item
                try:
                    line += str(temp[i][j]) + '\n'
                except IndexError:
                    line += '\n'
            else:
                try:
                    line += str(temp[i][j]) + f'{delimiter}'
                except IndexError:
                    line += f'{delimiter}'
        file.write(line)
    file.close()


def loadDataDict(fullpath, delimiter=',', useCols=None, commentFlag='#', keyDelimiter=None, keyFlag=None, keyList=None):
    """Load data from file saved by manipUtils.filemanip.saveDataDict.

    Actualy, it can load data from any txt file if file is minimally
    properly formated.

    Comments must be indicated at the begining of the line and comments are
    permited only at the begining of the file.

    Args:
        fullpath (str or pathlib.Path): path to file.
        delimiter (str, optional): The string used to separate values.
            By default, comma (,) is used. If whitespaces are used, any
            consecutive whitespaces act as delimiter and columns must have the
            same lenght. Use \t for tab.
        useCols (list, optional): Which columns to read, with 0 being the first. You Can
            use numbers (int) or strings, where string must match with header strings
            in the file. You may mix numbers and strings, in this case
            numbers are accounted first, than the strings.
        commentFlag (str, optional): lines starting with commentFlag are disregarded.
        keyFlag (str, optional): It searchs the beginning of the file (before data
            starts) for a line with this flag and creates dict keys based on
            this line. If `None`, it will try to create header from the last
            header line before data starts.
        keyDelimiter (str, optional): If not None, it will use keyDelimiter to
        separate header keys. Useful when delimiter from data is different from
        keys delimiter.
        keyList (list, optional): use this if loading data from a file that does
            not have a header or if you want to change the columns labels imported
            from the file. It creates dict keys based on `keyList`.
            If `keyList` smaller than `useCols` than extra itens in `useCols`
            are ignored.

    Returns
        Dictionary.
    """
    if delimiter is None:
        delimiter = ' '

    # adjust usecols
    useCols2 = deepcopy(useCols)
    if useCols2 is not None:
        useCols = [number for number in useCols if type(number) == int]
        useKeys = [key for key in useCols2 if type(key) == str]
    else:
        useKeys = None

    # get header
    if keyFlag is None:
        keyFlag = commentFlag
    header = _getComments(fullpath, commentFlag=commentFlag, stopFlag=keyFlag)

    # get header from file (keylist2 -> total key list from file)
    if (useKeys is None or useKeys == []) and keyList is not None:
        pass
    else:
        if header == -1:
            print('Error. Cannot find header, Use keyList to manually add header.')
            return -1
        if keyDelimiter is None:
            keyDelimiter=delimiter
        keyList2 = header[-1].replace(keyFlag, '').strip()
        keyList2 = keyList2.replace('\n', '').split(keyDelimiter)
        # remove empty itens and trailing spaces
        keyList2 = [item.strip() for item in keyList2 if item != '']
        # keyList2 = keyList2[1:]#.replace(keyFlag, '').strip()

    # add itens to useCols
    if useKeys is not None:
        for key in useKeys:
            if key in keyList2:
                useCols.append(keyList2.index(key))

    # add itens to keylist
    if keyList is None and useCols != None:
        keyList = [keyList2[i] for i in useCols]
    elif keyList is None and useCols is None:
        keyList = keyList2

    # get data
    data = np.genfromtxt(str(Path(fullpath)), delimiter=delimiter, usecols=useCols)

    datadict = dict()
    for i in range(len(keyList)):
        name = keyList[i]
        try:
            data_temp = data[:, i]

        except IndexError:
            if len(keyList) == 1:
                data_temp = data[:]
            else:
                data_temp = data[i]
        if np.isin('nan', data_temp):
            first_nan = np.where(np.isnan(data_temp))[0][0]
            datadict[name] = data_temp[:first_nan]
        else:
            if len(keyList) == 1:
                datadict[name] = data_temp[:]
            else:
                datadict[name] = data_temp

    return datadict


def checkExtension(fullpath, extension):
    """Check if file has desired extension.

    Args:
        fullpath (str or pathlib.Path): path to file.
        extension (str): string extension. No need to put dot in front of it.

    Returns
        True if file has an extension and it macth with `extension`. False if
        it does not match and -1 if file does not have extension.
    """
    filename = Path(fullpath)
    extension = extension.split('.')[-1]

    a = filename.name.split('.')
    if len(a) > 1:
        ext = a[-1]
        return extension == ext
    else:
        ext = None
        return -1


def filenamePattern(fileList, values2keep, separator='_', ask=True):
    """Change the filename pattern of several files.

    For example: suppose a file naming system with like:

    <folder>/000_58949_test0.txt
    <folder>/001_98769_test1.txt
    ...

    Suppose that we want to rename the file like:

    <folder>/test0_58949.txt
    <folder>/test1_98769.txt
    ...

    Then we would run this function with `values2keep=[2, 1]`.

    Args:
        fileList (str or pathlib.Path): list with full file directory paths.
        separator (str, optional): string that separates information chuncks.
        values2keep (list): Each chunk of information (which is
            separated by "separator") is assigned a number based on its position.
            The first info is 0, then 1, and so on. `values2keep` is a list of which
            info chuncks you want to keep and in which order.
        ask (bool): If true, it shows all the new filenames and asks for
            permission to rename.
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


def parse_folder(fullpath, separator='_', reference_position=0):
    """Returns a dict with file or folder paths inside fullpath.

    The file names (or folder names) are splited at separator in a list of
    strings. The value at reference_position will be used as key.

    Args:
        fullpath (str or pathlib.Path): list with full file directory paths.
        separator (str, optional): string that separates information chuncks.
        reference_position (int, optional): Each chunk of information (which is
            separated by "separator") is assigned a number based on its position.
            The first info is 0, then 1, and so on. `reference_position` is a
            index representing which value to use as key.

    Examples:
        Suppose we have a folder with the following subfolders:
            >folder_main
                > 0_data0
                > 1_data_important
                > 2_whatever
                > 3_another_data_folder
                > ...

        We can easily get the path to the subfolder by using:
        
        >>> folder_main_p = parse_folder(fullpath_to_folder_main)
        >>> folder_main_p[0]
        fullpath_to_folder_main/0_data0
        >>> folder_main_p[3]
        fullpath_to_folder_main/3_another_data_folder
    """
    fullpath = Path(fullpath)

    parsed_folder = dict()
    for element in fullpath.glob('*'):

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

    return parsed_folder
