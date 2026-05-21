from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

# ========== ИЕРАРХИЯ ==========
class SectionCreate(BaseModel):
    name: str
    section_type: str
    parent_id: Optional[int] = None

class SectionResponse(SectionCreate):
    id: int
    created_at: datetime

# ========== БАЗОВОЕ ИЗДАНИЕ ==========
class PublicationBase(BaseModel):
    title: str
    author: str
    year: int
    publisher: Optional[str] = None
    section_id: int

# ========== КНИГА ==========
class BookCreate(PublicationBase):
    isbn: str
    pages: int
    genre: Optional[str] = None

class BookResponse(BookCreate):
    id: int
    version: int
    is_current: bool
    created_at: datetime

# ========== ЖУРНАЛ ==========
class MagazineCreate(PublicationBase):
    issn: str
    issue_number: int
    frequency: Optional[str] = None

class MagazineResponse(MagazineCreate):
    id: int
    version: int
    is_current: bool
    created_at: datetime

# ========== ГАЗЕТА ==========
class NewspaperCreate(PublicationBase):
    issn: str
    date_published: date
    city: Optional[str] = None

class NewspaperResponse(NewspaperCreate):
    id: int
    version: int
    is_current: bool
    created_at: datetime

# ========== ИСТОРИЯ ВЕРСИЙ ==========
class PublicationHistoryResponse(BaseModel):
    id: int
    version: int
    title: str
    author: str
    pub_type: str
    is_current: bool
    created_at: datetime
    isbn: Optional[str] = None
    pages: Optional[int] = None
    genre: Optional[str] = None
    issn: Optional[str] = None
    issue_number: Optional[int] = None
    frequency: Optional[str] = None
    date_published: Optional[date] = None
    city: Optional[str] = None