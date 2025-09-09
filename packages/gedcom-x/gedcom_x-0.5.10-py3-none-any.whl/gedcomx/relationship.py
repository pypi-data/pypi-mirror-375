from enum import Enum
from typing import Any, Dict, Optional, List
"""
======================================================================
 Project: Gedcom-X
 File:    relationship.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-08-25
 Updated:
   - 2025-09-31: filename PEP8 standard
   - 2025-09-03: _from_json_ refactor
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .attribution import Attribution
from .conclusion import ConfidenceLevel
from .evidence_reference import EvidenceReference
from .Extensions.rs10.rsLink import _rsLinks #new
from .fact import Fact
from .identifier import Identifier, make_uid
from .note import Note
from .person import Person
from .resource import Resource
from .source_reference import SourceReference
from .subject import Subject
from .logging_hub import hub, logging
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
#=====================================================================


class RelationshipType(Enum):
    Couple = "http://gedcomx.org/Couple"
    ParentChild = "http://gedcomx.org/ParentChild"
    
    @property
    def description(self):
        descriptions = {
            RelationshipType.Couple: "A relationship of a pair of persons.",
            RelationshipType.ParentChild: "A relationship from a parent to a child."
        }
        return descriptions.get(self, "No description available.")
    
class Relationship(Subject):
    """Represents a relationship between two Person(s)

    Args:
        type (RelationshipType): Type of relationship 
        person1 (Person) = First Person in Relationship
        person2 (Person): Second Person in Relationship

    Raises:
        
    """
    identifier = 'http://gedcomx.org/v1/Relationship'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
             person1: Optional[Person | Resource] = None,
             person2: Optional[Person | Resource] = None,
             facts: Optional[List[Fact]] = None,  
             id: Optional[str] = None,
             lang: Optional[str] = None,
             sources: Optional[List[SourceReference]] = None,
             analysis: Optional[Resource] = None,
             notes: Optional[List[Note]] = None,
             confidence: Optional[ConfidenceLevel] = None,
             attribution: Optional[Attribution] = None,
             extracted: Optional[bool] = None,
             evidence: Optional[List[EvidenceReference]] = None,
             media: Optional[List[SourceReference]] = None,
             identifiers: Optional[List[Identifier]] = None,
             type: Optional[RelationshipType] = None,
             links: Optional[_rsLinks] = None,
             ) -> None:
    
        # Call superclass initializer if required
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers,links=links)
        
        self.id = id if id else make_uid()
        self.type = type
        self.person1 = person1
        self.person2 = person2
        self.facts = facts if facts else []
    
    def add_fact(self,fact: Fact):
        if (fact is not None) and isinstance(fact,Fact):
            for existing_fact in self.facts:
                if fact == existing_fact:
                    return
            self.facts.append(fact)
        else:
            raise TypeError(f"Expected type 'Fact' recieved type {type(fact)}")

    @property
    def _as_dict_(self):
        from .serialization import Serialization
        return Serialization.serialize(self)
        
        type_as_dict = (super()._as_dict_ or {}).copy()

        extras = {
            "type": getattr(self.type, "value", None),
            "person1": Resource(target=self.person1)._as_dict_ if self.person1 else None,
            "person2": Resource(target=self.person2)._as_dict_ if self.person2 else None,
            "facts": [f._as_dict_ for f in self.facts if f] if getattr(self, "facts", None) else None,
        }

        # only keep non-empty values
        type_as_dict.update({k: v for k, v in extras.items() if v not in (None, [], {}, ())})

        return type_as_dict or None

    @classmethod
    def _from_json_(cls, data: Dict[str, Any], context: Any = None) -> "Relationship":
        """
        Create a Person instance from a JSON-dict (already parsed).
        """
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict, got {type(data)}")
        
        relationship_data: Dict[str, Any] = {}
        relationship_data = Subject._dict_from_json_(data,context)

        if (id_ := data.get("id")) is not None:
            relationship_data["id"] = id_
        
        if (type_ := data.get("type")) is not None:
            relationship_data["type"] = RelationshipType(type_)
        
        # person1 / person2
        if (p1 := data.get("person1")) is not None:
            relationship_data["person1"] = Resource._from_json_(p1,context)

        if (p2 := data.get("person2")) is not None:
            relationship_data["person2"] = Resource._from_json_(p2,context)

        # facts
        if (facts := data.get("facts")) is not None:
            relationship_data["facts"] = [Fact._from_json_(f, context) for f in facts]
        
        return cls(**relationship_data)
    