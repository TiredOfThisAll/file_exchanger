from dataclasses import dataclass
from datetime import datetime


@dataclass
class Metadata:
    uuid: str
    filename: str
    filesize: int
    content_type: str
    extension: str
    was_uploaded_on: datetime