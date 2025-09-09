from typing import Any, Optional
"""
======================================================================
 Project: Gedcom-X
 File:    note.py
 Author:  David J. Cartwright
 Purpose: Python Object representation of GedcomX Name, NameType, NameForm, NamePart Types

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
from .logging_hub import hub, logging
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
#=====================================================================

class Note:
    identifier = 'http://gedcomx.org/v1/Note'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,lang: Optional[str] = 'en', subject: Optional[str] = None, text: Optional[str] = None, attribution: Optional[Attribution] = None) -> None:
        self.lang = lang
        self.subject = subject
        self.text = text
        self.attribution = attribution  

    def append(self, text_to_add: str):
        if text_to_add and isinstance(text_to_add, str):
            if self.text:
                self.text = self.text + text_to_add
            else:
                self.text = text_to_add
        else:
            return #TODO
            raise ValueError("The text to add must be a non-empty string.")
    
    @property
    def _as_dict_(self):
        from .serialization import Serialization
        type_as_dict = {}
        if self.lang:
            type_as_dict["lang"] = self.lang
        if self.subject:
            type_as_dict["subject"] = self.subject
        if self.text:
            type_as_dict["text"] = self.text
        if self.attribution:
            # If attribution exposes `_as_dict_` as a property, use it; otherwise include as-is
            type_as_dict["attribution"] = getattr(self.attribution, "_as_dict_", self.attribution)
        return type_as_dict if type_as_dict != {} else None
        return Serialization.serialize_dict(type_as_dict)    
    
    def __eq__(self, other):
        if not isinstance(other, Note):
            return NotImplemented

        def safe_str(val):
            return val.strip() if isinstance(val, str) else ''

        return (
            #safe_str(self.lang) == safe_str(other.lang) and
            #safe_str(self.subject) == safe_str(other.subject) and
            safe_str(self.text) == safe_str(other.text) #and
           # self.attribution == other.attribution  # Assumes Attribution defines __eq__
        )
    
    @classmethod
    def _from_json_(cls, data: Any, context=None) -> "Note":
        # Allow shorthand: "some note text"
        #if isinstance(data, str):
        #    return cls(text=data)

        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict or str, got {type(data)}")

        obj: dict[str, Any] = {}

        # Scalars
        if (lang := data.get("lang")) is not None:
            obj["lang"] = lang
        if (subject := data.get("subject")) is not None:
            obj["subject"] = subject
        if (text := data.get("text")) is not None:
            obj["text"] = text

        # Object
        if (attr := data.get("attribution")) is not None:
            obj["attribution"] = Attribution._from_json_(attr, context)

        return cls(**obj)