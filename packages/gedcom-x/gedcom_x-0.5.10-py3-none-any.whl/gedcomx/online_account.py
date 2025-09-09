from typing import Optional

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

class OnlineAccount:
    identifier = 'http://gedcomx.org/v1/OnlineAccount'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, serviceHomepage: Resource, accountName: str) -> None:
        pass