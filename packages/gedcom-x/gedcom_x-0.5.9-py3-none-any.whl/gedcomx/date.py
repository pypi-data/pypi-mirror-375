from typing import Any, Optional, Dict
from datetime import datetime, timezone
from dateutil import parser
"""
======================================================================
 Project: Gedcom-X
 File:    date.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-08-25
 Updated:
   - 2025-09-03: _from_json refactored
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
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


class DateFormat:
    def __init__(self) -> None:
        pass

class DateNormalization():
    pass        

class Date:
    identifier = 'http://gedcomx.org/v1/Date'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, original: Optional[str],normalized: Optional[DateNormalization] = None ,formal: Optional[str | DateFormat] = None) -> None:
        self.original = original
        self.formal = formal

        self.normalized: DateNormalization | None = normalized if normalized else None
    
    @property
    def _as_dict_(self):
        from .serialization import Serialization
        type_as_dict = {}
        if self.original:
            type_as_dict['original'] = self.original
        if self.formal:
            type_as_dict['formal'] = self.formal
        return type_as_dict if type_as_dict != {} else None
        return Serialization.serialize_dict(type_as_dict)

    @classmethod
    def _from_json_(cls,data: Any, context=None):
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict or str, got {type(data)} data:{data}")

        date_data: Dict[str, Any] = {}

        # Scalars
        if (orig := data.get("original")) is not None:
            date_data["original"] = orig
        if (formal := data.get("formal")) is not None:
            date_data["formal"] = formal
        
        return cls(**date_data)
        


def date_to_timestamp(date_str: str, assume_utc_if_naive: bool = True, print_definition: bool = True):
    """
    Convert a date string of various formats into a Unix timestamp.

    A "timestamp" refers to an instance of time, including values for year, 
    month, date, hour, minute, second, and timezone.
    """
    # Handle year ranges like "1894-1912" → pick first year
    if "-" in date_str and date_str.count("-") == 1 and all(part.isdigit() for part in date_str.split("-")):
        date_str = date_str.split("-")[0].strip()

    # Parse date
    dt = parser.parse(date_str)

    # Ensure timezone awareness
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc if assume_utc_if_naive else datetime.now().astimezone().tzinfo)

    # Normalize to UTC and compute timestamp
    dt_utc = dt.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    ts = (dt_utc - epoch).total_seconds()

    # Create ISO 8601 string with full date/time/timezone
    full_timestamp_str = dt_utc.replace(microsecond=0).isoformat()

    
    return ts, full_timestamp_str