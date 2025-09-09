DEBUG = False

import json
import random
import string
import orjson

from functools import lru_cache
from typing import Any, Dict, List, Optional

"""
======================================================================
 Project: Gedcom-X
 File:    GedcomX.py
 Author:  David J. Cartwright
 Purpose: Object for working with Gedcom-X Data

 Created: 2025-07-25
 Updated:
    - 2025-08-31: _as_dict_ to only create entries in dict for fields that hold data,
    id_index functionality, will be used for resolution of Resources
    - 2025-09-03: _from_json_ refactor
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .agent import Agent
from .attribution import Attribution
from .document import Document
from .event import Event
from .group import Group
from .identifier import make_uid
from .logging_hub import logging, hub, ChannelConfig
from .person import Person
from .place_description import PlaceDescription
from .relationship import Relationship, RelationshipType
from .resource import Resource
from .source_description import ResourceType, SourceDescription
from .textvalue import TextValue
from .uri import URI
#=====================================================================

log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
deserial_log = "gedcomx.serialization"



def TypeCollection(item_type):
    """
    Factory that creates a typed, indexable collection for a specific model class.

    The returned object behaves like:
      - a container (append/remove, __len__, __getitem__)
      - an iterator (for item in collection)
      - a simple query helper via __call__(**field_equals)
      - a small in-memory index on id, name (see note), and uri

    Parameters
    ----------
    item_type : type
        The class/type that items in this collection must be instances of.

    Returns
    -------
    Collection
        A new, empty collection instance specialized for `item_type`.

    Notes
    -----
    - Name indexing is currently disabled (see TODO in `_update_indexes`).
    - The collection auto-assigns/normalizes an item's `uri.path` based on `item_type`.
    """
    class Collection:
        def __init__(self):
            self._items = []
            self._id_index = {}
            self._name_index = {}
            self._uri_index = {}
            self.uri = URI(path=f'/{item_type.__name__}s/')

        def __iter__(self):
            self._index = 0
            return self

        def __next__(self):
            if self._index < len(self._items):
                result = self._items[self._index]
                self._index += 1
                return result
            else:
                raise StopIteration

        @property
        def item_type(self):
            return item_type
        
        def _update_indexes(self, item):
            # Update the id index
            if hasattr(item, 'id'):
                self._id_index[item.id] = item
            
            try:
                if hasattr(item, 'uri'):
                    self._uri_index[item.uri.value] = item
            except AttributeError as e:
                print(f"type{item}")
                assert False

            # Update the name index
             #TODO Fix name handling on persons
            if hasattr(item, 'names'):
                names = getattr(item, 'names')
                for name in names:
                    #print(name._as_dict_)
                    if isinstance(name, TextValue):
                        name_value = name.value 
                        if name_value in self._name_index:
                            self._name_index[name_value].append(item)
                        else:
                            self._name_index[name_value] = [item]
                    else:
                        pass
            
        @property
        def id_index(self):
            return self._id_index
        
        def _remove_from_indexes(self, item):
            # Remove from the id index
            if hasattr(item, 'id'):
                if item.id in self._id_index:
                    del self._id_index[item.id]

            # Remove from the name index
            if hasattr(item, 'names'):
                names = getattr(item, 'names')
                for name in names:
                    name_value = name.value if isinstance(name, TextValue) else name
                    if name_value in self._name_index:
                        if item in self._name_index[name_value]:
                            self._name_index[name_value].remove(item)
                            if not self._name_index[name_value]:
                                del self._name_index[name_value]

        def byName(self, sname: str | None):
            # Use the name index for fast lookup
            if sname:
                sname = sname.strip()
                return self._name_index.get(sname, [])
            return []

        def byId(self, id):
            # Use the id index for fast lookup
            return self._id_index.get(id, None)
        
        def byUri(self, uri):
            # Use the id index for fast lookup
            return self._uri_index.get(uri.value, None)

        def append(self, item):
            if not isinstance(item, item_type):
                raise TypeError(f"Expected item of type {item_type.__name__}, got {type(item).__name__}")
            #if item.id in self.id_index: assert False
            if item.uri:
                item.uri.path  = f'{str(item_type.__name__)}s' if (item.uri.path is None or item.uri.path == "") else item.uri.path
            else:
                item.uri = URI(path=f'/{item_type.__name__}s/',fragment=item.id)
                
            self._items.append(item)
            self._update_indexes(item)

        def extend(self, items: list):
            """Add multiple items to the collection at once."""
            if not isinstance(items, (list, tuple)):
                raise TypeError("extend() expects a list or tuple of items")
            for item in items:
                self.append(item)

        def remove(self, item):
            if item not in self._items:
                raise ValueError("Item not found in the collection.")
            self._items.remove(item)
            self._remove_from_indexes(item)

        def __repr__(self):
            return f"Collection({self._items!r})"
        
        def list(self):
            for item in self._items:
                print(item)
        
        def __call__(self, **kwargs):
            results = []
            for item in self._items:
                match = True
                for key, value in kwargs.items():
                    if not hasattr(item, key) or getattr(item, key) != value:
                        match = False
                        break
                if match:
                    results.append(item)
            return results
        
        def __len__(self):
            return len(self._items)
        
        def __getitem__(self, index):
            return self._items[index]
    
        @property
        def _items_as_dict(self) -> dict:
            return {f'{str(item_type.__name__)}s':  [item._as_dict_ for item in self._items]}

        @property
        def _as_dict_(self):
            return {f'{str(item_type.__name__).lower()}s': [item._as_dict_ for item in self._items]}     

        @property
        def json(self) -> str:
            
            return json.dumps(self._as_dict_, indent=4)    

    return Collection()

class GedcomX:
    """
    Main GedcomX Object representing a Genealogy. Stores collections of Top Level Gedcom-X Types.
    complies with GEDCOM X Conceptual Model V1 (http://gedcomx.org/conceptual-model/v1)

    Parameters
    ----------
    id : str
        Unique identifier for this Genealogy.
    attribution : Attribution Object
        Attribution information for the Genealogy
    filepath : str
        Not Implimented.
    description : str
        Description of the Genealogy: ex. 'My Family Tree'

    Raises
    ------
    ValueError
        If `id` is not a valid UUID.
    """
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: Optional[str] = None,
                 attribution: Optional[Attribution] = None,
                 filepath: Optional[str] = None,
                 description: Optional[str] = None,
                 persons: Optional[List[Person]] = None,
                 relationships: Optional[List[Relationship]] = None,
                 sourceDescriptions: Optional[List[SourceDescription]] = None,
                 agents:  Optional[List[Agent]] = None,
                 places: Optional[List[PlaceDescription]] = None) -> None:
        
        self.id = id
        self.attribution = attribution
        self._filepath = None
        
        self.description = description
        self.sourceDescriptions = TypeCollection(SourceDescription)
        if sourceDescriptions: self.sourceDescriptions.extend(sourceDescriptions)
        self.persons = TypeCollection(Person)
        if persons: self.persons.extend(persons)
        self.relationships = TypeCollection(Relationship)
        if relationships: self.relationships.extend(relationships)      
        self.agents = TypeCollection(Agent)
        if agents: self.agents.extend(agents) 
        self.events = TypeCollection(Event)
        self.documents = TypeCollection(Document)
        self.places = TypeCollection(PlaceDescription)
        if places: self.places.extend(places)
        self.groups = TypeCollection(Group)

        self.relationship_table = {}

        #self.default_id_generator = make_uid

    @property
    def contents(self):
        return {
            "source_descriptions": len(self.sourceDescriptions),
            "persons": len(self.persons),
            "relationships": len(self.relationships),
            "agents": len(self.agents),
            "events": len(self.events),
            "documents": len(self.documents),
            "places": len(self.places),
            "groups": len(self.groups),
        }
            
    def add(self,gedcomx_type_object):
        if gedcomx_type_object:
            if isinstance(gedcomx_type_object,Person):
                self.add_person(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,SourceDescription):
                self.add_source_description(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Agent):
                self.add_agent(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,PlaceDescription):
                self.add_place_description(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Event):
                self.add_event(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Relationship):
                self.add_relationship(gedcomx_type_object)
            else:
                raise ValueError(f"I do not know how to add an Object of type {type(gedcomx_type_object)}")
        else:
            Warning("Tried to add a None type to the Geneology")

    def add_source_description(self,sourceDescription: SourceDescription):
        if sourceDescription and isinstance(sourceDescription,SourceDescription):
            if sourceDescription.id is None:
                assert False
            self.sourceDescriptions.append(item=sourceDescription)
            self.lastSourceDescriptionAdded = sourceDescription
        else:
            raise ValueError(f"When adding a SourceDescription, value must be of type SourceDescription, type {type(sourceDescription)} was provided")

    def add_person(self,person: Person):
        """Add a Person object to the Genealogy

        Args:
            person: Person Object

        Returns:
            None

        Raises:
            ValueError: If `person` is not of type Person.
        """
        if person and isinstance(person,Person):
            if person.id is None:
                person.id =self.make_id()
            self.persons.append(item=person)
        else:
            raise ValueError(f'person must be a Person Object not type: {type(person)}')
        
    def add_relationship(self,relationship: Relationship):
        if relationship and isinstance(relationship,Relationship):
            if isinstance(relationship.person1,Resource) and isinstance(relationship.person2,Resource):
                self.relationships.append(relationship)
                return
            elif isinstance(relationship.person1,Person) and isinstance(relationship.person2,Person):

                if relationship.person1:
                    if relationship.person1.id is None:
                        relationship.person1.id = self.make_id()
                    if not self.persons.byId(relationship.person1.id):
                        self.persons.append(relationship.person1)
                    if relationship.person1.id not in self.relationship_table:
                        self.relationship_table[relationship.person1.id] = []
                    self.relationship_table[relationship.person1.id].append(relationship)
                    relationship.person1._add_relationship(relationship)
                else:
                    pass
                
                if relationship.person2:
                    if relationship.person2.id is None:
                        relationship.person2.id = self.make_id() #TODO
                    if not self.persons.byId(relationship.person2.id):
                        self.persons.append(relationship.person2)
                    if relationship.person2.id not in self.relationship_table:
                        self.relationship_table[relationship.person2.id] = []
                    self.relationship_table[relationship.person2.id].append(relationship)
                    relationship.person2._add_relationship(relationship)
                else:
                    pass

                self.relationships.append(relationship)
        else:
            raise ValueError()
    
    def add_place_description(self,placeDescription: PlaceDescription):
        if placeDescription and isinstance(placeDescription,PlaceDescription):
            if placeDescription.id is None:
                Warning("PlaceDescription has no id")
            self.places.append(placeDescription)

    def add_agent(self,agent: Agent):
        if isinstance(agent,Agent) and agent is not None:
            if self.agents.byId(agent.id) is not None:   
                print(f"Did not add agent with Duplicate ID")  
                return False  
            self.agents.append(agent)
        else:
            raise ValueError()
    
    def add_event(self,event_to_add: Event):
        if event_to_add and isinstance(event_to_add,Event):
            if event_to_add.id is None: event_to_add.id = make_uid()
            for current_event in self.events:
                if event_to_add == current_event:
                    print("DUPLICATE EVENT")
                    print(event_to_add._as_dict_)
                    print(current_event._as_dict_)
                    
                    return
            self.events.append(event_to_add)
        else:
            raise ValueError

    @lru_cache(maxsize=65536)
    def get_person_by_id(self,id: str):
        filtered = [person for person in self.persons if getattr(person, 'id') == id]
        if filtered: return filtered[0]
        return None
     
    @lru_cache(maxsize=65536)
    def source_by_id(self,id: str):
        filtered = [source for source in self.sourceDescriptions if getattr(source, 'id') == id]
        if filtered: return filtered[0]
        return None        

    @property
    def id_index(self):
        combined = {**self.sourceDescriptions.id_index,
                    **self.persons.id_index,
                    **self.relationships.id_index,
                    **self.agents.id_index,
                    **self.events.id_index,
                    **self.documents.id_index,
                    **self.places.id_index,
                    **self.groups.id_index
        }
        for i in combined.keys():
            combined[i] = str(type(combined[i]).__name__)
        return combined

    @property
    def _as_dict(self) -> dict[str, Any]:
        from .serialization import Serialization
        return Serialization.serialize(self)
        

    @property
    def json(self) -> bytes:
        """
        JSON Representation of the GedcomX Genealogy.

        Returns:
            str: JSON Representation of the GedcomX Genealogy in the GEDCOM X JSON Serialization Format
        """
        return orjson.dumps(self._as_dict,option= orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE)
        

    @staticmethod
    def from_json(data: dict):
        from .serialization import Serialization
        gx = GedcomX()

        persons = data.get('persons', [])
        for person in persons:
            if (person := Person._from_json_(person)) is not None:
                gx.add_person(person)
        
        source_descriptions = data.get('sourceDescriptions', [])
        for source in source_descriptions:
            if (source_description := SourceDescription._from_json_(source)) is not None:
                gx.add_source_description(source_description)         
        
        relationships = data.get('relationships', [])
        for rel in relationships:
            if (relationship := Relationship._from_json_(rel)) is not None:
                gx.add_relationship(relationship)

        agents = data.get('agents', [])
        for agent_data in agents:
            if (agent := Agent._from_json_(agent_data)) is not None:
                gx.add_agent(agent)
            else:
                raise ValueError()
        
        events = data.get('events', [])
        for event_data in events:
            if (event := Event._from_json_(event_data)) is not None:
                gx.add_event(event)
                
        places = data.get('places', [])
        for place_data in places:
            if (place := PlaceDescription._from_json_(place_data)) is not None:
                gx.add_place_description(place)
        
        documents = data.get('documents', [])
        for doc_data in documents:
            if (event := Document._from_json_(event_data)) is not None:
                pass
        
        return gx
        
    @staticmethod
    def make_id(length: int = 12) -> str:
        """Generate a random alphanumeric ID of given length."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(random.choices(alphabet, k=length))