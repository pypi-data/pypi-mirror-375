from enum import Enum
from typing import Any, Dict, List, Optional
"""
======================================================================
 Project: Gedcom-X
 File:    document.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-08-25
 Updated:
   - 2025-09-03: _from_json_ refactored 
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .attribution import Attribution
from .conclusion import Conclusion, ConfidenceLevel
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


class DocumentType(Enum):
    Abstract = "http://gedcomx.org/Abstract"
    Transcription = "http://gedcomx.org/Transcription"
    Translation = "http://gedcomx.org/Translation"
    Analysis = "http://gedcomx.org/Analysis"
    
    @property
    def description(self):
        descriptions = {
            DocumentType.Abstract: "The document is an abstract of a record or document.",
            DocumentType.Transcription: "The document is a transcription of a record or document.",
            DocumentType.Translation: "The document is a translation of a record or document.",
            DocumentType.Analysis: "The document is an analysis done by a researcher; a genealogical proof statement is an example of one kind of analysis document."
        }
        return descriptions.get(self, "No description available.")

class TextType(Enum):
    plain = 'plain'
    xhtml = 'xhtml'

class Document(Conclusion):
    identifier = 'http://gedcomx.org/v1/Document'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: Optional[str] = None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None, # ConfidenceLevel
                 attribution: Optional[Attribution] = None,
                 type: Optional[DocumentType] = None,
                 extracted: Optional[bool] = None, # Default to False
                 textType: Optional[TextType] = None,
                 text: Optional[str] = None,
                 ) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution)
        self.type = type
        self.extracted = extracted
        self.textType = textType
        self.text = text
    
    @property
    def _as_dict(self):
        from .serialization import Serialization
        type_as_dict = super()._as_dict_
        if self.type:
            type_as_dict['type'] = self.type.value
        if self.extracted is not None:
            type_as_dict['extracted'] = self.extracted
        if self.textType:
            type_as_dict['textType'] = self.textType.value
        if self.text:
            type_as_dict['text'] = self.text
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls, data: Any, context: Any = None) -> "Document":
        """
        Build a Document from JSON.
        Shorthand: a bare string becomes {'text': <string>}.
        """
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict or str, got {type(data)}")

        obj: Dict[str, Any] = Conclusion._dict_from_json_(data,context)

        # type (enum)
        if (typ := data.get("type")) is not None:
            obj["type"] = DocumentType(typ)
            

        # extracted (bool; accept common string forms)
        if (ex := data.get("extracted")) is not None:
            obj["extracted"] = bool(ex)

        # textType (enum)
        if (tt := data.get("textType")) is not None:
            obj["textType"] = TextType(tt) 

        # text (string)
        if (tx := data.get("text")) is not None:
            obj["text"] = str(tx)

        return cls(**obj)