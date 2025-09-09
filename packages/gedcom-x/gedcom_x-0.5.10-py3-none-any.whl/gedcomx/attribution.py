
from datetime import datetime
from typing import Optional, Dict, Any

"""
======================================================================
 Project: Gedcom-X
 File:    Attribution.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-08-25
 Updated:
   - 2025-08-31: fixed _as_dict_ to deal with Resources and ignore empty fields
   - 2025-09-03: _from_json_ refactor

   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .agent import Agent
from .resource import Resource
from .logging_hub import hub, logging
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
#=====================================================================


class Attribution:
    """Attribution Information for a Genealogy, Conclusion, Subject and child classes

    Args:
        contributor (Agent, optional):            Contributor to object being attributed.
        modified (timestamp, optional):           timestamp for when this record was modified.
        changeMessage (str, optional):            Birth date (YYYY-MM-DD).
        creator (Agent, optional):      Creator of object being attributed.
        created (timestamp, optional):            timestamp for when this record was created

    Raises:
        
    """
    identifier = 'http://gedcomx.org/v1/Attribution'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,contributor: Optional[Agent | Resource] = None,
                 modified: Optional[datetime] = None,
                 changeMessage: Optional[str] = None,
                 creator: Optional[Agent | Resource] = None,
                 created: Optional[datetime] = None) -> None:
               
        self.contributor = contributor
        self.modified = modified
        self.changeMessage = changeMessage
        self.creator = creator
        self.created = created
        
    @property
    def _as_dict_(self) -> Dict[str, Any] | None:
        """
        Serialize Attribution to a JSON-ready dict, skipping None values.
        """
        with hub.use(serial_log):
            log.debug(f"Serializing 'Attribution'")
            type_as_dict: Dict[str, Any] = {}
            if self.contributor:
                type_as_dict['contributor'] = Resource(target=self.contributor)._as_dict_  
            if self.modified:     
                type_as_dict['modified'] = self.modified if self.modified else None
            if self.changeMessage:
                type_as_dict['changeMessage'] = self.changeMessage if self.changeMessage else None 
            if self.creator:
                type_as_dict['creator'] = Resource(target=self.creator)._as_dict_   
            if self.created:      
                type_as_dict['created'] = self.created if self.created else None
                    
            log.debug(f"'Attribution' serialized with fields: {type_as_dict.keys()}") 
            if type_as_dict == {}: log.warning("serializing and empty 'Attribution'")
        return type_as_dict if type_as_dict != {} else None

    @classmethod
    def _from_json_(cls, data: Dict[str, Any],context) -> 'Attribution':
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict or str, got {type(data)}")

        attribution_data: Dict[str, Any] = {}

        # contributor: Agent | Resource | URI string
        if (contrib := data.get("contributor")) is not None:
            attribution_data["contributor"] = Resource._from_json_(contrib, context)

        # creator: Agent | Resource | URI string
        if (creator := data.get("creator")) is not None:
            attribution_data["creator"] = Resource._from_json_(creator, context)

        # changeMessage: str
        if (cm := data.get("changeMessage")) is not None:
            attribution_data["changeMessage"] = cm

        # created/modified: datetime
        if (created := data.get("created")) is not None:
            attribution_data["created"] = created
        if (modified := data.get("modified")) is not None:
            attribution_data["modified"] = modified

        return cls(**attribution_data)
