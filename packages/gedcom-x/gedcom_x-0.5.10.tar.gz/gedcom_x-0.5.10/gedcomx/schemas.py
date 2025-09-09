from typing import List



class Schema:
    def __init__(self) -> None:
        pass

    def _init_schema(self):
        from .address import Address
        from .agent import Agent
        from .attribution import Attribution
        from .conclusion import ConfidenceLevel
        from .date import Date
        from .document import Document, DocumentType, TextType
        from .evidence_reference import EvidenceReference
        from .event import Event, EventType, EventRole, EventRoleType
        from .Extensions.rs10.rsLink import _rsLinks, rsLink
        from .fact import Fact, FactType, FactQualifier
        from .gender import Gender, GenderType
        from .identifier import IdentifierList, Identifier
        from .logging_hub import hub, ChannelConfig
        from .name import Name, NameType, NameForm, NamePart, NamePartType, NamePartQualifier
        from .note import Note
        from .online_account import OnlineAccount
        from .person import Person
        from .place_description import PlaceDescription
        from .place_reference import PlaceReference
        from .qualifier import Qualifier
        from .relationship import Relationship, RelationshipType
        from .resource import Resource
        from .source_description import SourceDescription, ResourceType, SourceCitation, Coverage
        from .source_reference import SourceReference
        from .textvalue import TextValue
        from .uri import URI

        self.field_type_table ={
            "Agent": {
                "id": str,
                "identifiers": IdentifierList,
                "names": List[TextValue],
                "homepage": URI,
                "openid": URI,
                "accounts": List[OnlineAccount],
                "emails": List[URI],
                "phones": List[URI],
                "addresses": List[Address],
                "person": object | Resource,  # intended Person | Resource
                "attribution": object,        # GEDCOM5/7 compatibility
                "uri": URI | Resource,
            },
            "Attribution": {
                "contributor": Resource,
                "modified": str,
                "changeMessage": str,
                "creator": Resource,
                "created": str,
            },
            "Conclusion": {
                "id": str,
                "lang": str,
                "sources": List["SourceReference"],
                "analysis": Document | Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "uri": "Resource",
                "max_note_count": int,
                "links": _rsLinks,
            },
            "Date": {
                "original": str,
                "formal": str,
                "normalized": str,
            },
            "Document": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": DocumentType,
                "extracted": bool,
                "textType": TextType,
                "text": str,
            },
            "Event": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": List[Identifier],
                "type": EventType,
                "date": Date,
                "place": PlaceReference,
                "roles": List[EventRole],
            },
            "EventRole": {
                "id:": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "person": Resource,
                "type": EventRoleType,
                "details": str,
            },
            "Fact": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource | Document,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": FactType,
                "date": Date,
                "place": PlaceReference,
                "value": str,
                "qualifiers": List[FactQualifier],
                "links": _rsLinks,
            },
            "GedcomX": {
                "persons": List[Person],
                "relationships": List[Relationship],
                "sourceDescriptions": List[SourceDescription],
                "agents": List[Agent],
                "places": List[PlaceDescription]
            },
            "Gender": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": GenderType,
            },
            "KnownSourceReference": {
                "name": str,
                "value": str,
            },
            "Name": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": NameType,
                "nameForms": List[NameForm],  # use string to avoid circulars if needed
                "date": Date,
            },
            "NameForm": {
                "lang": str,
                "fullText": str,
                "parts": List[NamePart],  # use "NamePart" as a forward-ref to avoid circulars
            },
            "NamePart": {
                "type": NamePartType,
                "value": str,
                "qualifiers": List["NamePartQualifier"],  # quote if you want to avoid circulars
            },
            "Note":{"lang":str,
                    "subject":str,
                    "text":str,
                    "attribution": Attribution},
            "Person": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": IdentifierList,
                "private": bool,
                "gender": Gender,
                "names": List[Name],
                "facts": List[Fact],
                "living": bool,
                "links": _rsLinks,
            },
            "PlaceDescription": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": List[IdentifierList],
                "names": List[TextValue],
                "type": str,
                "place": URI,
                "jurisdiction": Resource,
                "latitude": float,
                "longitude": float,
                "temporalDescription": Date,
                "spatialDescription": Resource,
            },
            "PlaceReference": {
                "original": str,
                "description": URI,
            },
            "Qualifier": {
                "name": str,
                "value": str,
            },
            "_rsLinks": {
                "person":rsLink,
                "portrait":rsLink},
            "rsLink": {
                "href": URI,
                "template": str,
                "type": str,
                "accept": str,
                "allow": str,
                "hreflang": str,
                "title": str,
            },
            "Relationship": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": IdentifierList,
                "type": RelationshipType,
                "person1": Resource,
                "person2": Resource,
                "facts": List[Fact],
            },
            "Resource": {
                "resource": str,
                "resourceId": str,
            },  
            "SourceDescription": {
                "id": str,
                "resourceType": ResourceType,
                "citations": List[SourceCitation],
                "mediaType": str,
                "about": URI,
                "mediator": Resource,
                "publisher": Resource,          # forward-ref to avoid circular import
                "authors": List[Resource],
                "sources": List[SourceReference],         # SourceReference
                "analysis": Resource,          # analysis is typically a Document (kept union to avoid cycle)
                "componentOf": SourceReference,           # SourceReference
                "titles": List[TextValue],
                "notes": List[Note],
                "attribution": Attribution,
                "rights": List[Resource],
                "coverage": List[Coverage],               # Coverage
                "descriptions": List[TextValue],
                "identifiers": IdentifierList,
                "created": Date,
                "modified": Date,
                "published": Date,
                "repository": Agent,                    # forward-ref
                "max_note_count": int,
            },
            "SourceReference": {
                "description": Resource,
                "descriptionId": str,
                "attribution": Attribution,
                "qualifiers": List[Qualifier],
            },
            "Subject": {
                "id": str,
                "lang": str,
                "sources": List["SourceReference"],
                "analysis": Resource,
                "notes": List["Note"],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": IdentifierList,
                "uri": Resource,
                "links": _rsLinks,
            },
            "TextValue":{"lang":str,"value":str},  
            "URI": {
                "value": str,
            },

        }
    
    def register_extra(self, cls, name, typ ):
        print("Adding...",cls,name,typ)
        if cls.__name__ not in self.field_type_table.keys():
            print("A")
            self.field_type_table[cls.__name__] = {name:typ}
        else:
            if name in self.field_type_table[cls.__name__].keys():
                print("B")
                raise ValueError
            else:
                self.field_type_table[cls.__name__][name] = typ
                print("C")

SCHEMA = Schema()
SCHEMA._init_schema()