from typing import Optional

"""
======================================================================
 Project: Gedcom-X
 File:    Qualifier.py
 Author:  David J. Cartwright
 Purpose: Python Object representation of GedcomX Qualifier Type

 Created: 2025-08-25
 Updated:
   - 2025-08-31: _as_dict_ to only create entries in dict for fields that 
   hold data, updated _from_json
   - 2025-09-03: _from_json_ refactor
   
======================================================================
"""
from .logging_hub import hub, logging
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
#=====================================================================

class Qualifier:
    """defines the data structure used to supply additional details, annotations,
    tags, or other qualifying data to a specific data element.

    
    Attributes:
        name str: The name of the Qualifier. *It is RECOMMENDED that the qualifier 
            name resolve to an element of a constrained vocabulary.*
            
        value (Optional[str]): The value of the Qualifier. *If provided, the name 
            MAY give the semantic meaning of the value.*

    """
    identifier = 'http://gedcomx.org/v1/Qualifier'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self, name: str, value: Optional[str]) -> None:
        self.name = name
        self.value = value
    
    @property
    def __as_dict__(self):
        from .serialization import Serialization

        type_as_dict = {}
        if self.name:
            type_as_dict["name"] = self.name
        if self.value:
            type_as_dict["value"] = self.value
        
        return type_as_dict if type_as_dict != {} else None
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls, data: dict, context=None) -> "Qualifier":
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict, got {type(data)}")

        name = data.get("name")
        value = data.get("value")

        return cls(name=name, value=value)

