"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- date stamps (with varies formatting options)

"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#


#: default file stamp date format using underscores as delimiter: 21_03_01
import datetime

from duHast.Utilities.files_io import get_file_name_without_ext


FILE_DATE_STAMP_YY_MM_DD = "%y_%m_%d"


#: file stamp date format using spaces as delimiter: 21 03 01
FILE_DATE_STAMP_YYMMDD_SPACE = "%y %m %d"


#: file stamp date format using spaces as delimiter: 2021 03 01
FILE_DATE_STAMP_YYYYMMDD_SPACE = "%Y %m %d"


#: file stamp date format using underscores as delimiter: 2021_03_01
FILE_DATE_STAMP_YYYY_MM_DD = "%Y_%m_%d"


#: file stamp date time format using underscores as delimiter: 2021_03_01_18_59_59
FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC = "%Y_%m_%d_%H_%M_%S"

#: file stamp date time format using underscores as delimiter: 2021_03_01_18_59_59_123
FILE_DATE_STAMP_YYYY_MM_DD_HH_MM_SEC_MSEC = "%Y_%m_%d_%H_%M_%S_%f"


#: time stamp using colons: 18:59:59
TIME_STAMP_HHMMSEC_COLON = "%H:%M:%S"

#: time stamp using colons: 18_59_59
TIME_STAMP_HHMMSEC_UNDERSCORE = "%H_%M_%S"


def get_file_date_stamp(format=FILE_DATE_STAMP_YY_MM_DD):
    """
    Returns a date stamp formatted suitable for a file name.
    :param format: The date stamp format, defaults to FILE_DATE_STAMP_YY_MM_DD
    :type format: str, optional
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    """

    d = datetime.datetime.now()
    return d.strftime(format)


#: folder date format: no delimiter 210301
FOLDER_DATE_STAMP_YYMMDD = "%y%m%d"


#: folder date format: no delimiter 20210301
FOLDER_DATE_STAMP_YYYYMMDD = "%Y%m%d"


#: folder date format: no delimiter 2021
FOLDER_DATE_STAMP_YYYY = "%Y"

def date_time_stamp_builder(format):
    """
    Returns a formatted date stamp.

    Note: milliseconds, if required, are capped to 3 digits.

    :param format: The date stamp format
    :type format: str
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    """

    if isinstance(format, str):
        # check if the format is a valid date format
        try:
            d = datetime.datetime.now()
            formatted_time = d.strftime(format)
            
            # Check if the format includes microseconds and trim to milliseconds if needed
            if "%f" in format:
                formatted_time = formatted_time[:-3]

            return formatted_time
        except ValueError:
            raise ValueError("Invalid date format string provided.")
    else:
        raise TypeError("Format must be a string, got {}".format(type(format))) 
    

def get_folder_date_stamp(format=FOLDER_DATE_STAMP_YYYYMMDD):
    """
    Returns a date stamp formatted suitable for a folder name.

    Note: milliseconds, if required, are capped to 3 digits.

    :param format: The date stamp format, defaults to FOLDER_DATE_STAMP_YYYYMMDD
    :type format: str, optional
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    """

    return  date_time_stamp_builder(format)



def get_date_stamp(format):
    """
    Returns a date stamp formatted using past in format string.

    Note: milliseconds, if required, are capped to 3 digits.

    :param format: The date stamp format
    :type format: str
    :return: datetime.now() string formatted using supplied format string
    :rtype: str
    """

    return date_time_stamp_builder(format)


def get_date_stamped_file_name(file_path, file_extension=".txt", file_suffix=""):
    """
    Returns a time stamped output file name based on the past in file name and file extension.
    :param file_path: Fully qualified file path to file
    :type file_path: str
    :param file_extension: File extension needs to include '.', defaults to '.txt'
    :type file_extension: str, optional
    :param file_suffix: File suffix will be appended after the name but before the file extension, defaults to ''
    :type file_suffix: str, optional
    :return: File name.
    :rtype: str
    """

    # get date prefix for file name
    file_prefix = get_file_date_stamp()
    name = get_file_name_without_ext(file_path)
    return file_prefix + "_" + name + file_suffix + file_extension
