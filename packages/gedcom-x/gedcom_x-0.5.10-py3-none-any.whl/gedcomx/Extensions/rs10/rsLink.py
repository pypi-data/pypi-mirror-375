from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union
"""
======================================================================
 Project: Gedcom-X
 File:    rsLink.py
 Author:  David J. Cartwright
 Purpose: Link type of GedcomX RS (Extension)

 Created: 2025-08-25
 Updated:
   - 
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from ...exceptions import GedcomClassAttributeError
from ...logging_hub import hub, logging
from ...uri import URI
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
deserial_log = "gedcomx.deserialization"
#=====================================================================


class rsLink():
    """A link description object. RS Extension to GedcomX by FamilySearch.

    Args:
        rel (str): Link relation identifier. Required.
        href (str, optional): Link target URI. If omitted, provide `template`.
        template (str, optional): URI Template (see RFC 6570). If omitted, provide `href`.
        type (str, optional): Media type(s) of the linked resource (RFC 2616 §3.7).
        accept (str, optional): Acceptable media type(s) for updating the linked resource (RFC 2616 §3.7).
        allow (str, optional): Allowable HTTP methods to transition to the linked resource (RFC 2616 §14.7).
        hreflang (str, optional): Language of the linked resource (e.g., BCP-47 tag).
        title (str, optional): Human-readable label for the link.

    Raises:
        ValueError: If neither `href` nor `template` is provided.
    """

    """Attribution Information for a Genealogy, Conclusion, Subject and child classes

    Args:
        contributor (Agent, optional):            Contributor to object being attributed.
        modified (timestamp, optional):           timestamp for when this record was modified.
        changeMessage (str, optional):            Birth date (YYYY-MM-DD).
        creator (Agent, optional):      Creator of object being attributed.
        created (timestamp, optional):            timestamp for when this record was created

    Raises:
        
    """
    identifier = "http://gedcomx.org/v1/Link"

    def __init__(self,
                 href:  Optional[URI] = None,
                 template: Optional[str] = None,
                 type: Optional[str] = None,
                 accept: Optional[str] = None,
                 allow: Optional[str] = None,
                 hreflang: Optional[str] = None,
                 title: Optional[str] = None) -> None:
        
      
        self.href = href if isinstance(href,URI) else URI.from_url(href) if isinstance(href,str) else None
        self.template = template
        self.type = type
        self.accept = accept
        self.allow = allow
        self.hreflang = hreflang
        self.title = title
    
        if self.href is None: # and self.template is None:
            raise GedcomClassAttributeError("href or template are required")
        
    def __str__(self) -> str:
        def to_text(v):
            if v is None:
                return None
            # unwrap URI-like objects
            if isinstance(v, URI):
                return getattr(v, "value", None) or str(v)
            # normalize strings (skip empty/whitespace-only)
            if isinstance(v, str):
                s = v.strip()
                return s or None
            return str(v)

        parts = []

        # show href as the primary bit if present
        href_s = to_text(self.href)
        if href_s:
            parts.append(href_s)

        # show other fields as key=value
        for name in ("template", "type", "accept", "allow", "hreflang", "title"):
            val = to_text(getattr(self, name, None))
            if val:
                parts.append(f"{name}={val}")

        return " | ".join(parts) if parts else self.__class__.__name__    
            
    
    
    @classmethod
    def _from_json_(cls, data: Any, context: Any = None) -> "rsLink":
        """
        Build an rsLink from JSON.

        Accepted shapes:
          - {"rel": "self", "href": "https://..."}
          - {"rel": {...}, "href": {...}}  # URI objects as dicts
          - {"href": "https://...", "type": "...", ...}  # rel optional
          - {"uri": "https://..."} or {"url": "..."}     # href aliases
          - "https://example.com"                         # shorthand -> href only

        Note:
          - `rel` is coerced to a URI if possible.
          - `href` is coerced to a URI (string/dict supported).
          - If both `href` and `template` are missing, __init__ will raise.
        """
        # Shorthand: bare string is an href
        
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict or str, got {type(data)}")

        print("LINK DATA:",data)
        # Extract with common aliases
        rel = data.get("rel")
        href = data.get("href")
                    


        return cls(
            rel=rel,
            href=href,
            template=data.get("template"),
            type=data.get("type"),
            accept=data.get("accept"),
            allow=data.get("allow"),
            hreflang=data.get("hreflang"),
            title=data.get("title"),
        )


class _rsLinks():
    
    def __init__(self,
                 person: rsLink | None = None,
                 portrait: rsLink | None= None
                 ) -> None:
        
        self.person = person
        self.portrait = portrait