"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around data storage in Revit.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data storage can be used to project wide settings not associated with a specific element. 

Obsolete in Revit 2025 ... 
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

import duHast.Utilities.Objects.result as res

from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.ExtensibleSchemas.extensible_schemas import get_schema


from Autodesk.Revit.DB import FilteredElementCollector, Transaction
from Autodesk.Revit.DB.ExtensibleStorage import DataStorage



def find_data_storage(doc, schema_guid):
    """
    Find a DataStorage element in the Revit document that contains the specified schema.
    
    :param doc: The Revit document to search in.
    :type doc: Autodesk.Revit.DB.Document
    :param schema_guid: The GUID of the schema to look for.
    :type schema_guid: str
    
    :return: The DataStorage element if found, None otherwise.
    :rtype: Autodesk.Revit.DB.DataStorage or None
    """
    
    # Look up the schema using its GUID
    schema = get_schema(schema_guid)
    if not schema:
        return None

    # Use a FilteredElementCollector to find all DataStorage elements
    collector = FilteredElementCollector(doc).OfClass(DataStorage)
    for data_storage in collector:
        # Check if the DataStorage element has an entity with the schema
        entity = data_storage.GetEntity(schema)
        if entity and entity.IsValid():
            return data_storage

    return None


def update_entity_on_data_storage(doc, data_storage, entity):
    """
    Update the entity of a DataStorage element with new data.
    
    :param doc: The Revit document to update the DataStorage element in.
    :type doc: Autodesk.Revit.DB.Document
    
    :param data_storage: The DataStorage element to update.
    :type data_storage: Autodesk.Revit.DB.DataStorage
    
    :param entity: The new entity to set on the DataStorage element.
    :type entity: Autodesk.Revit.DB.ExtensibleStorage.Entity

    :return: A Result object containing the updated DataStorage element in its result list or an error message.
    :rtype: duHast.Utilities.Objects.result.Result
    """
    
    return_value = res.Result()
    
    # build an action to update the DataStorage element
    def action():
        action_return_value = res.Result()
        try:
            # Update the DataStorage element with the new Entity
            data_storage.SetEntity(entity)
            action_return_value.append_message(
                "DataStorage element updated successfully."
            )
            action_return_value.result.append(data_storage)
        except Exception as e:
                action_return_value.update_sep(
                    False,
                    "Failed to update data storage: {}".format(e),
                )
        return action_return_value
    
    # attempt to update the DataStorage element in a transaction
    transaction = Transaction(doc, "Updating data storage")
    data_storage_update_result = in_transaction(transaction, action)
    return_value.update(data_storage_update_result)

    return return_value