"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to read swap instances by type  directives file(s) and return them as a tuple to the caller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These helper function expect a text file in csv format with 5 columns:

- SOURCE_FAMILY_NAME = 0
- SOURCE_FAMILY_CATEGORY_NAME = 1
- SOURCE_FAMILY_TYPE_NAME = 2
- TARGET_FAMILY_NAME = 3
- TARGET_FAMILY_TYPE = 4

Note:

- First row is treated as a header row and its content is ignored.

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

from duHast.Utilities import files_csv as fileCSV, files_get as fileGet
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap
from duHast.Utilities.files_io import file_exist




def _read_swap_directives(files):
    """
    Reads list of swap directives from file into named directive class instances.

    :param filePath: Fully qualified file path to rename directives file.
    :type filePath: str
    :return: List of swap directives.
    :rtype: [FamilyDirectiveSwap]
    """

    rename_directives = []
    for file in files:
        rows_result = fileCSV.read_csv_file(file)
        # check whether file was read successfully
        if rows_result.status is False:
            return rename_directives
        
        rows = rows_result.result
        
        # read rows in tuples ignoring the header row
        for i in range(1, len(rows)):
            if len(rows[i]) >= 4:

                data = FamilyDirectiveSwap(
                    name=rows[i][
                        FamilyDirectiveSwap.SWAP_DIRECTIVE_LIST_INDEX_SOURCE_FAMILY_NAME
                    ],
                    category=rows[i][
                        FamilyDirectiveSwap.SWAP_DIRECTIVE_LIST_INDEX_SOURCE_FAMILY_CATEGORY_NAME
                    ],
                    source_type_name=rows[i][
                        FamilyDirectiveSwap.SWAP_DIRECTIVE_LIST_INDEX_SOURCE_FAMILY_TYPE_NAME
                    ],
                    target_family_name=rows[i][
                        FamilyDirectiveSwap.SWAP_DIRECTIVE_LIST_TARGET_FAMILY_NAME
                    ],
                    target_family_type_name=rows[i][
                        FamilyDirectiveSwap.SWAP_DIRECTIVE_LIST_TARGET_FAMILY_TYPE
                    ],
                )

            rename_directives.append(data)
    return rename_directives

def get_swap_directives(directory_path):
    """
    Retrieves file swap directives from a given folder location.

    :param directory_path: Fully qualified folder path to folder containing directives.
    :type directory_path: str

    :return:
        Result class instance.

        - result.status. True if rename directives where found and loaded successfully, otherwise False.
        - result.message will contain number of directives found in format:'Found rename directives: ' + number
        - result.result list of directives

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # check whether csv files matching file name filter exist in directory path
    swap_directive_files = fileGet.get_files_from_directory_walker_with_filters(
        directory_path,
        FamilyDirectiveSwap.SWAP_DIRECTIVE_FILE_NAME_PREFIX,
        "",
        FamilyDirectiveSwap.SWAP_DIRECTIVE_FILE_EXTENSION,
    )

    # check whether any files where found?
    if len(swap_directive_files) > 0:
        # attempt to re swap directives from files
        swap_directives = _read_swap_directives(swap_directive_files)
        # check whether any swap directives where found in files
        if len(swap_directives) > 0:
            return_value.update_sep(
                True, "Found swap directives: {}".format(len(swap_directives))
            )
            # store swap directives in result object
            return_value.result = swap_directives
        else:
            return_value.update_sep(
                False,FamilyDirectiveSwap.EXCEPTION_EMPTY_SWAP_DIRECTIVE_FILES
            )
    else:
        return_value.update_sep(
            False, FamilyDirectiveSwap.EXCEPTION_NO_SWAP_DIRECTIVE_FILES
        )

    return return_value


def write_swap_directives_to_file(swap_directives, file_path):
    """
    Writes swap directives to a specified file in CSV format.

    :param swap_directives: List of swap directives to write to file.
    :type swap_directives: list of FamilyDirectiveSwap
    :param file_path: Fully qualified file path where the directives will be written.
    :type file_path: str
    :return: Result object indicating success or failure of the write operation.
    :rtype: Result
    """
    
    return_value = res.Result()


    # loop over directives and convert them to a list of lists
    swap_directives_list = []
    try:
        for directive in swap_directives:
            swap_directives_list.append([
                directive.name,
                directive.category,
                directive.source_type_name,
                directive.target_family_name,
                directive.target_family_type_name
            ])

        # set default write mode and header
        write_mode = "w"
        header = FamilyDirectiveSwap.SWAP_DIRECTIVE_HEADER_ROW

        # check whether file exists and set write mode and header accordingly
        if file_exist(file_path):
            # file does not exist, so write mode is 'w'
            write_mode = "a"
            header =[]
        
        # write the directives to the file
        return_value = fileCSV.write_report_data_as_csv(
            file_name=file_path,
            header = header,
            write_type=write_mode,
            data=swap_directives_list,
            quoting=fileCSV.csv.QUOTE_MINIMAL,
        )

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write swap directives with exception: {}".format(e),
        )
    
    return return_value
