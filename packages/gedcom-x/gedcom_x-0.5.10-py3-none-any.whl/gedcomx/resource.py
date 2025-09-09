from typing import Optional

"""
======================================================================
 Project: Gedcom-X
 File:    Resource.py
 Author:  David J. Cartwright
 Purpose: References TopLevel Types for Serialization

 Created: 2025-08-25
 Updated:
   - 2025-08-31: working on target=Resource and deserialization issues
   - 2025-09-03: _from_json_ refactor, arguments changed
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""

from .uri import URI
from .logging_hub import hub, logging
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
#=====================================================================
    
class Resource:
    """
    Class used to track and resolve URIs and references between datastores.

    Parameters
    ----------
    
    Raises
    ------
    ValueError
        If `id` is not a valid UUID.
    """
    # TODO, Deal with a resouce being passed, as it may be unresolved.
    def __init__(self,resource: URI | None = None,resourceId: str | None = None, target: object = None) -> None:
        
        #if (resource is None) and (target is None): #TODO
        #    raise ValueError('Resource object must point to something.')

        self.resource = resource
        self.resourceId = resourceId
        self.Id = None

        self.type = None
        self.resolved = False
        self.target: object = target
        self.remote: bool | None = None    # is the resource pointed to persitent on a remote datastore?

        if target:
            if isinstance(target,Resource):
                self.resource = target.resource
                self.resourceId = target.resourceId
                self.target = target.target
            else:
                log.debug(f"Target of type: {type(target)}, {target}")
                if hasattr(target,'uri'):
                    self.resource = target.uri
                else:
                    self.resourceId = URI(fragment=target.id)
                self.resourceId = target.id
   
    @property
    def uri(self):
        return self.resource
    
    @property
    def _as_dict_(self):
        from .serialization import Serialization
        return Serialization.serialize(self)
        typ_as_dict = {}
        if self.resource is not None:
            typ_as_dict["resource"] = self.resource
        if self.resourceId is not None:
            typ_as_dict["resourceId"] = self.resourceId,
        
        return typ_as_dict or None

    
    
    @classmethod
    def _from_json_(cls, data: dict, context=None) -> "Resource":
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict, got {type(data)} {data}")
        resource = {}

        # Scalars
        if (res := data.get("resource")) is not None:
            resource["resource"] = res

        return cls(**resource)

    def __repr__(self) -> str:
        return f"Resource(resource={self.resource}, resourceId={self.resourceId}, target={self.target})"
    
    def __str__(self) -> str:
        return f"resource={self.resource}{f', resourceId={self.resourceId}' if self.resourceId else ''}"
    


