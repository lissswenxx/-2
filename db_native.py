import asyncpg
from typing import Optional, Dict, Any, List

class NativeDB:
    def __init__(self):
        self.dsn = "postgresql://postgres:12345@localhost/library_db"
    
    async def get_connection(self):
        return await asyncpg.connect(self.dsn)
    
    async def create_book(self, data: Dict) -> Dict:
        conn = await self.get_connection()
        try:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "INSERT INTO publications (title, author, year, publisher, section_id, pub_type, is_current) VALUES ($1,$2,$3,$4,$5,'book',true) RETURNING id, version",
                    data['title'], data['author'], data['year'], data.get('publisher'), data['section_id'])
                pid, ver = row['id'], row['version']
                await conn.execute(
                    "INSERT INTO books (publication_id, version, isbn, pages, genre) VALUES ($1,$2,$3,$4,$5)",
                    pid, ver, data['isbn'], data['pages'], data.get('genre'))
                return {"id": pid, "version": ver}
        finally:
            await conn.close()
    
    async def create_magazine(self, data: Dict) -> Dict:
        conn = await self.get_connection()
        try:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "INSERT INTO publications (title, author, year, publisher, section_id, pub_type, is_current) VALUES ($1,$2,$3,$4,$5,'magazine',true) RETURNING id, version",
                    data['title'], data['author'], data['year'], data.get('publisher'), data['section_id'])
                pid, ver = row['id'], row['version']
                await conn.execute(
                    "INSERT INTO magazines (publication_id, version, issn, issue_number, frequency) VALUES ($1,$2,$3,$4,$5)",
                    pid, ver, data['issn'], data['issue_number'], data.get('frequency'))
                return {"id": pid, "version": ver}
        finally:
            await conn.close()
    
    async def create_newspaper(self, data: Dict) -> Dict:
        conn = await self.get_connection()
        try:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "INSERT INTO publications (title, author, year, publisher, section_id, pub_type, is_current) VALUES ($1,$2,$3,$4,$5,'newspaper',true) RETURNING id, version",
                    data['title'], data['author'], data['year'], data.get('publisher'), data['section_id'])
                pid, ver = row['id'], row['version']
                await conn.execute(
                    "INSERT INTO newspapers (publication_id, version, issn, date_published, city) VALUES ($1,$2,$3,$4,$5)",
                    pid, ver, data['issn'], data['date_published'], data.get('city'))
                return {"id": pid, "version": ver}
        finally:
            await conn.close()
    
    async def update_publication(self, pub_id: int, update_data: Dict) -> Dict:
        conn = await self.get_connection()
        try:
            async with conn.transaction():
                set_clause = ", ".join([f"{k}=${i+2}" for i,k in enumerate(update_data.keys())])
                values = list(update_data.values())
                await conn.execute(f"UPDATE publications SET {set_clause} WHERE id=$1 AND is_current=true", pub_id, *values)
                new = await conn.fetchrow("SELECT id, version, is_current FROM publications WHERE id=$1 AND is_current=true", pub_id)
                return {"id": new['id'], "version": new['version'], "is_current": new['is_current']}
        finally:
            await conn.close()
    
    async def get_publication_history(self, pub_id: int) -> List[Dict]:
        conn = await self.get_connection()
        try:
            rows = await conn.fetch(
                "SELECT p.*, b.isbn, b.pages, b.genre, m.issn, m.issue_number, m.frequency, n.issn as n_issn, n.date_published, n.city FROM publications p LEFT JOIN books b ON p.id=b.publication_id AND p.version=b.version LEFT JOIN magazines m ON p.id=m.publication_id AND p.version=m.version LEFT JOIN newspapers n ON p.id=n.publication_id AND p.version=n.version WHERE p.id=$1 ORDER BY p.version", pub_id)
            return [dict(r) for r in rows]
        finally:
            await conn.close()
    
    async def create_section(self, name: str, section_type: str, parent_id: Optional[int] = None) -> Dict:
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow("INSERT INTO sections (name, section_type, parent_id) VALUES ($1,$2,$3) RETURNING id, name, section_type, parent_id, created_at", name, section_type, parent_id)
            return dict(row)
        finally:
            await conn.close()
    
    async def get_section_tree(self, root_id: Optional[int] = None) -> List[Dict]:
        conn = await self.get_connection()
        try:
            if root_id:
                rows = await conn.fetch("WITH RECURSIVE tree AS (SELECT id, name, section_type, parent_id, 1 as level FROM sections WHERE id=$1 UNION ALL SELECT s.id, s.name, s.section_type, s.parent_id, t.level+1 FROM sections s JOIN tree t ON s.parent_id=t.id) SELECT id, name, section_type, parent_id, level FROM tree ORDER BY level, id", root_id)
            else:
                rows = await conn.fetch("WITH RECURSIVE tree AS (SELECT id, name, section_type, parent_id, 1 as level FROM sections WHERE parent_id IS NULL UNION ALL SELECT s.id, s.name, s.section_type, s.parent_id, t.level+1 FROM sections s JOIN tree t ON s.parent_id=t.id) SELECT id, name, section_type, parent_id, level FROM tree ORDER BY level, id")
            return [dict(r) for r in rows]
        finally:
            await conn.close()
    
    async def delete_publication_logical(self, pub_id: int) -> Dict:
        conn = await self.get_connection()
        try:
            async with conn.transaction():
                await conn.execute("UPDATE publications SET is_current=false WHERE id=$1 AND is_current=true", pub_id)
                return {"id": pub_id, "deleted": True}
        finally:
            await conn.close()
    
    async def get_book_by_id(self, pub_id: int) -> Optional[Dict]:
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow("SELECT p.*, b.* FROM publications p JOIN books b ON p.id=b.publication_id AND p.version=b.version WHERE p.id=$1 AND p.is_current=true", pub_id)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    async def get_all_books(self) -> List[Dict]:
        conn = await self.get_connection()
        try:
            rows = await conn.fetch("SELECT p.id, p.title, p.author, b.isbn, b.pages FROM publications p JOIN books b ON p.id=b.publication_id AND p.version=b.version WHERE p.is_current=true AND p.pub_type='book'")
            return [dict(r) for r in rows]
        finally:
            await conn.close()