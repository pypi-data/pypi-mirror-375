"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to rename family files on a local or network drive.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This helper function expect a folder containing rename directive files. For format of those files refer to module RevitFamilyRenameFilesUtils

Note:

- The revit category is not used when renaming files but when renaming nested families.
- Any associated type catalogue files will also be renamed to match the new family name.
- Rename directives may not have the filePath property set if the directive is only meant to be used on loaded families.

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

# import clr
# import System
import os

from duHast.Revit.Family import family_rename_files_utils as rFamRenameUtils
from duHast.Utilities.Objects import result as res
from duHast.Utilities import files_io as fileIO

def _rename_associated_files(rename_directive):
    """
    Renames associated catalogue files and part atom xml files based on rename directives.

    :param rename_directive: Rename directive object.
    :type rename_directive: rename_directive

    :return:
        Result class instance.

        - result.status. True if files where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'old name -> new name'.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """
    return_value = res.Result()

    associated_file_extension = {
        ".txt": "catalogue",
        ".xml": "part atom",
    }

    try:
        for file_extension_associated_file, associated_file_description in associated_file_extension.items():
            old_full_name = rename_directive.file_path[:-4] + file_extension_associated_file
            new_full_name = os.path.join(
                os.path.dirname(rename_directive.file_path),
                rename_directive.new_name + file_extension_associated_file,
            )
            old_txt_name = rename_directive.name + file_extension_associated_file
            new_txt_name = rename_directive.new_name + file_extension_associated_file
            try:
                if fileIO.file_exist(old_full_name):
                    os.rename(old_full_name, new_full_name)
                    return_value.append_message("{} -> {}".format(old_txt_name, new_txt_name))
                else:
                    return_value.update_sep(
                        True, "No {} file found: {}".format(associated_file_description,old_txt_name)
                    )  # nothing gone wrong here...just no catalogue file present
            except Exception as e:
                return_value.update_sep(
                    False,
                    "Failed to rename {} file: {} with exception: {}".format(
                        associated_file_description, old_full_name, e
                    ),
                )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to rename associated files with exception: ".format(e)
        )

    return return_value


def _rename_files(rename_directives, progress_callback=None):
    """
    Renames family files and any associated catalogue files and part atom xml files based on rename directives.

    :param rename_directives: List of tuples representing rename directives.
    :type rename_directives: [rename_directive]

    :return:
        Result class instance.

        - result.status. True if files where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'old name -> new name'.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    return_value.update_sep(True, "Renaming families:")

    # progress call back
    callback_counter = 1

    for rename_directive in rename_directives:

        if progress_callback != None:
            progress_callback.update(callback_counter, len(rename_directives))

        try:
            return_value.append_message("rename directive: {}".format(rename_directive))
            # check if rename directive includes a file path ( might be empty if nested families only are to be renamed)
            if rename_directive.file_path != "":
                # attempt to rename family file
                try:
                    # build the new file name
                    new_full_name = os.path.join(
                        os.path.dirname(rename_directive.file_path),
                        rename_directive.new_name + ".rfa",
                    )
                    if fileIO.file_exist(rename_directive.file_path):
                        os.rename(rename_directive.file_path, new_full_name)
                        return_value.append_message(
                            "{} -> {}".format(
                                rename_directive.name, rename_directive.new_name
                            )
                        )
                    else:
                        return_value.update_sep(
                            False, "File not found: {}".format(rename_directive.name)
                        )
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "Failed to rename file: {} with exception: {}".format(
                            rename_directive.name, e
                        ),
                    )

                # take care of catalogue files as well
                result_assocaited_files = _rename_associated_files(rename_directive)
                return_value.update(result_assocaited_files)
            else:
                return_value.update_sep(
                    True, "No file path found: {}".format(rename_directive.name)
                )  # nothing gone wrong here...just not required to rename a file
        except Exception as e:
            return_value.update_sep(
                False, "Failed to rename files with exception: ".format(e)
            )
        
        # check for user cancel
        if progress_callback != None:
            if progress_callback.is_cancelled():
                return_value.append_message("User cancelled!")
                break
        # progress call back
        callback_counter += 1
        
    return return_value


def rename_family_files(directory_path, progress_callback=None):
    """
    Entry point for this module. Will read rename directives files in given directory and attempt to rename
    family files and any associated catalogue files accordingly.

    Note: for rename directive file structure refer to module family_rename_files_utils
    
    :param directory_path: Fully qualified directory path to where rename directive files are located.
    :type directory_path: str
    :return: 
        Result class instance.

        - result.status. True if files where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'old name -> new name'.
        - result.result empty list
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain an exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    # get directives from folder
    rename_directives_result = rFamRenameUtils.get_rename_directives(directory_path)
    # check if anything came back
    if rename_directives_result.status:
        rename_directives = rename_directives_result.result
        # rename files as per directives
        return_value = _rename_files(rename_directives, progress_callback)
    else:
        return_value = rename_directives_result

    return return_value
