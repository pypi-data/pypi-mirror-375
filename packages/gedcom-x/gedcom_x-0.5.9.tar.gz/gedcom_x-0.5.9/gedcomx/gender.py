from enum import Enum
from typing import List, Optional
"""
======================================================================
 Project: Gedcom-X
 File:    gender.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-08-25
 Updated:
   - 2025-09-03: _from_json_ refactor 
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .attribution import Attribution
from .conclusion import ConfidenceLevel, Conclusion
from .Extensions.rs10.rsLink import _rsLinks
from .note import Note
from .resource import Resource
from .source_reference import SourceReference
from .logging_hub import hub, logging
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
#=====================================================================


class GenderType(Enum):
    Male = "http://gedcomx.org/Male"
    Female = "http://gedcomx.org/Female"
    Unknown = "http://gedcomx.org/Unknown"
    Intersex = "http://gedcomx.org/Intersex"
    
    @property
    def description(self):
        descriptions = {
            GenderType.Male: "Male gender.",
            GenderType.Female: "Female gender.",
            GenderType.Unknown: "Unknown gender.",
            GenderType.Intersex: "Intersex (assignment at birth)."
        }
        return descriptions.get(self, "No description available.")
    
class Gender(Conclusion):
    identifier = 'http://gedcomx.org/v1/Gender'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 id: Optional[str] = None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None, 
                 type: Optional[GenderType] = None,
                 links: Optional[_rsLinks] = None
                 ) -> None:
        super().__init__(id=id, lang=lang, sources=sources, analysis=analysis, notes=notes, confidence=confidence, attribution=attribution, links=links)
        self.type = type
    
    @property
    def _as_dict_(self):
            
        type_as_dict = super()._as_dict_  or {}
        if self.type:
            type_as_dict['type'] = self.type.value if self.type else None                   
        
        return type_as_dict if type_as_dict != {} else None
        

    @classmethod
    def _from_json_(cls,data,context):
        conclusion = Conclusion._dict_from_json_(data,context)
        if (type_ := data.get("type")) is not None:
            conclusion["type"] = GenderType(type_)
        
        return cls(**conclusion)
        
        