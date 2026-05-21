from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Date, Boolean, TIMESTAMP, ForeignKey, select, and_
from datetime import datetime, date
from typing import Optional, Dict, Any, List

DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost/library_db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# ========== МОДЕЛИ ==========
class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    section_type = Column(String(50))
    parent_id = Column(Integer, ForeignKey('sections.id'))
    created_at = Column(TIMESTAMP, default=datetime.now)

class Publication(Base):
    __tablename__ = 'publications'
    id = Column(Integer, primary_key=True)
    version = Column(Integer, primary_key=True, default=1)
    title = Column(String(300))
    author = Column(String(200))
    year = Column(Integer)
    publisher = Column(String(200))
    section_id = Column(Integer, ForeignKey('sections.id'))
    pub_type = Column(String(50))
    is_current = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.now)

class Book(Base):
    __tablename__ = 'books'
    publication_id = Column(Integer, ForeignKey('publications.id'), primary_key=True)
    version = Column(Integer, ForeignKey('publications.version'), primary_key=True)
    isbn = Column(String(20))
    pages = Column(Integer)
    genre = Column(String(100))

class Magazine(Base):
    __tablename__ = 'magazines'
    publication_id = Column(Integer, ForeignKey('publications.id'), primary_key=True)
    version = Column(Integer, ForeignKey('publications.version'), primary_key=True)
    issn = Column(String(20))
    issue_number = Column(Integer)
    frequency = Column(String(50))

class Newspaper(Base):
    __tablename__ = 'newspapers'
    publication_id = Column(Integer, ForeignKey('publications.id'), primary_key=True)
    version = Column(Integer, ForeignKey('publications.version'), primary_key=True)
    issn = Column(String(20))
    date_published = Column(Date)
    city = Column(String(100))

# ========== CRUD ОПЕРАЦИИ ==========

# --- КНИГИ ---
async def create_book(db: AsyncSession, data: Dict) -> Dict:
    pub = Publication(
        title=data['title'], author=data['author'], year=data['year'],
        publisher=data.get('publisher'), section_id=data['section_id'], pub_type='book', is_current=True
    )
    db.add(pub)
    await db.flush()
    
    book = Book(
        publication_id=pub.id, version=pub.version, isbn=data['isbn'],
        pages=data['pages'], genre=data.get('genre')
    )
    db.add(book)
    await db.commit()
    return {"id": pub.id, "version": pub.version}

async def get_book_by_id(db: AsyncSession, pub_id: int) -> Optional[Dict]:
    result = await db.execute(
        select(Publication, Book)
        .join(Book, and_(Publication.id == Book.publication_id, Publication.version == Book.version))
        .where(Publication.id == pub_id, Publication.is_current == True)
    )
    row = result.first()
    if not row: return None
    pub, book = row
    return {**{c.name: getattr(pub, c.name) for c in pub.__table__.columns},
            **{c.name: getattr(book, c.name) for c in book.__table__.columns}}

# --- ЖУРНАЛЫ ---
async def create_magazine(db: AsyncSession, data: Dict) -> Dict:
    pub = Publication(
        title=data['title'], author=data['author'], year=data['year'],
        publisher=data.get('publisher'), section_id=data['section_id'], pub_type='magazine', is_current=True
    )
    db.add(pub)
    await db.flush()
    
    magazine = Magazine(
        publication_id=pub.id, version=pub.version, issn=data['issn'],
        issue_number=data['issue_number'], frequency=data.get('frequency')
    )
    db.add(magazine)
    await db.commit()
    return {"id": pub.id, "version": pub.version}

# --- ГАЗЕТЫ ---
async def create_newspaper(db: AsyncSession, data: Dict) -> Dict:
    pub = Publication(
        title=data['title'], author=data['author'], year=data['year'],
        publisher=data.get('publisher'), section_id=data['section_id'], pub_type='newspaper', is_current=True
    )
    db.add(pub)
    await db.flush()
    
    newspaper = Newspaper(
        publication_id=pub.id, version=pub.version, issn=data['issn'],
        date_published=data['date_published'], city=data.get('city')
    )
    db.add(newspaper)
    await db.commit()
    return {"id": pub.id, "version": pub.version}

# --- ОБНОВЛЕНИЕ ---
async def update_publication(db: AsyncSession, pub_id: int, update_data: Dict) -> Dict:
    result = await db.execute(
        select(Publication).where(Publication.id == pub_id, Publication.is_current == True)
    )
    pub = result.scalar_one()
    for key, value in update_data.items():
        if hasattr(pub, key):
            setattr(pub, key, value)
    db.add(pub)
    await db.commit()
    await db.refresh(pub)
    return {"id": pub.id, "version": pub.version, "is_current": pub.is_current}

# --- ИСТОРИЯ ВЕРСИЙ ---
async def get_publication_history(db: AsyncSession, pub_id: int) -> List[Dict]:
    result = await db.execute(
        select(Publication).where(Publication.id == pub_id).order_by(Publication.version)
    )
    pubs = result.scalars().all()
    history = []
    for pub in pubs:
        item = {"id": pub.id, "version": pub.version, "title": pub.title, "author": pub.author,
                "pub_type": pub.pub_type, "is_current": pub.is_current, "created_at": pub.created_at}
        if pub.pub_type == 'book':
            r = await db.execute(select(Book).where(Book.publication_id == pub.id, Book.version == pub.version))
            book = r.scalar_one_or_none()
            if book:
                item['isbn'] = book.isbn
                item['pages'] = book.pages
                item['genre'] = book.genre
        elif pub.pub_type == 'magazine':
            r = await db.execute(select(Magazine).where(Magazine.publication_id == pub.id, Magazine.version == pub.version))
            mag = r.scalar_one_or_none()
            if mag:
                item['issn'] = mag.issn
                item['issue_number'] = mag.issue_number
                item['frequency'] = mag.frequency
        elif pub.pub_type == 'newspaper':
            r = await db.execute(select(Newspaper).where(Newspaper.publication_id == pub.id, Newspaper.version == pub.version))
            news = r.scalar_one_or_none()
            if news:
                item['issn'] = news.issn
                item['date_published'] = news.date_published
                item['city'] = news.city
        history.append(item)
    return history

# --- ИЕРАРХИЯ ---
async def create_section(db: AsyncSession, name: str, section_type: str, parent_id: Optional[int] = None) -> Dict:
    section = Section(name=name, section_type=section_type, parent_id=parent_id)
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return {"id": section.id, "name": section.name, "section_type": section.section_type, "parent_id": section.parent_id}

async def get_section_tree(db: AsyncSession, root_id: Optional[int] = None) -> List[Dict]:
    if root_id:
        query = """WITH RECURSIVE tree AS (SELECT id, name, section_type, parent_id, 1 as level FROM sections WHERE id = %s
                   UNION ALL SELECT s.id, s.name, s.section_type, s.parent_id, t.level + 1 FROM sections s
                   JOIN tree t ON s.parent_id = t.id) SELECT id, name, section_type, parent_id, level FROM tree ORDER BY level, id"""
        result = await db.execute(query, (root_id,))
    else:
        query = """WITH RECURSIVE tree AS (SELECT id, name, section_type, parent_id, 1 as level FROM sections WHERE parent_id IS NULL
                   UNION ALL SELECT s.id, s.name, s.section_type, s.parent_id, t.level + 1 FROM sections s
                   JOIN tree t ON s.parent_id = t.id) SELECT id, name, section_type, parent_id, level FROM tree ORDER BY level, id"""
        result = await db.execute(query)
    rows = result.fetchall()
    return [{"id": r[0], "name": r[1], "section_type": r[2], "parent_id": r[3], "level": r[4]} for r in rows]

# --- УДАЛЕНИЕ ---
async def delete_publication_logical(db: AsyncSession, pub_id: int) -> Dict:
    result = await db.execute(select(Publication).where(Publication.id == pub_id, Publication.is_current == True))
    pub = result.scalar_one_or_none()
    if not pub:
        return {"error": "Publication not found"}
    pub.is_current = False
    db.add(pub)
    await db.commit()
    return {"id": pub_id, "deleted": True}

# --- СПИСКИ ---
async def get_all_books(db: AsyncSession) -> List[Dict]:
    result = await db.execute(
        select(Publication, Book)
        .join(Book, and_(Publication.id == Book.publication_id, Publication.version == Book.version))
        .where(Publication.is_current == True, Publication.pub_type == 'book')
    )
    return [{"id": p.id, "title": p.title, "author": p.author, "isbn": b.isbn, "pages": b.pages} for p, b in result.all()]