from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uvicorn

from db_orm import AsyncSessionLocal
from db_orm import create_book as orm_create_book
from db_orm import create_magazine as orm_create_magazine
from db_orm import create_newspaper as orm_create_newspaper
from db_orm import get_book_by_id as orm_get_book
from db_orm import update_publication as orm_update
from db_orm import get_publication_history as orm_history
from db_orm import create_section as orm_create_section
from db_orm import get_section_tree as orm_get_tree
from db_orm import delete_publication_logical as orm_delete
from db_orm import get_all_books as orm_get_books

from db_native import NativeDB

from schemas import *

app = FastAPI(title="Библиотечная система")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

USE_ORM = True
native_db = NativeDB()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ========== ИЕРАРХИЯ ==========
@app.post("/api/sections", response_model=SectionResponse)
async def create_section(section: SectionCreate, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_create_section(db, section.name, section.section_type, section.parent_id)
    else:
        return await native_db.create_section(section.name, section.section_type, section.parent_id)

@app.get("/api/sections/tree")
async def get_tree(root_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_get_tree(db, root_id)
    else:
        return await native_db.get_section_tree(root_id)

# ========== КНИГИ ==========
@app.post("/api/books", response_model=dict)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_create_book(db, book.dict())
    else:
        return await native_db.create_book(book.dict())

@app.get("/api/books/{pub_id}")
async def get_book(pub_id: int, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        result = await orm_get_book(db, pub_id)
    else:
        result = await native_db.get_book_by_id(pub_id)
    if not result:
        raise HTTPException(status_code=404, detail="Book not found")
    return result

@app.get("/api/books")
async def get_all_books(db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_get_books(db)
    else:
        return await native_db.get_all_books()

# ========== ЖУРНАЛЫ ==========
@app.post("/api/magazines", response_model=dict)
async def create_magazine(magazine: MagazineCreate, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_create_magazine(db, magazine.dict())
    else:
        return await native_db.create_magazine(magazine.dict())

# ========== ГАЗЕТЫ ==========
@app.post("/api/newspapers", response_model=dict)
async def create_newspaper(newspaper: NewspaperCreate, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_create_newspaper(db, newspaper.dict())
    else:
        return await native_db.create_newspaper(newspaper.dict())

# ========== ОБНОВЛЕНИЕ, ИСТОРИЯ, УДАЛЕНИЕ ==========
@app.put("/api/publications/{pub_id}")
async def update_publication(pub_id: int, update_data: dict, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_update(db, pub_id, update_data)
    else:
        return await native_db.update_publication(pub_id, update_data)

@app.get("/api/publications/{pub_id}/history")
async def get_history(pub_id: int, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_history(db, pub_id)
    else:
        return await native_db.get_publication_history(pub_id)

@app.delete("/api/publications/{pub_id}")
async def delete_publication(pub_id: int, db: AsyncSession = Depends(get_db)):
    if USE_ORM:
        return await orm_delete(db, pub_id)
    else:
        return await native_db.delete_publication_logical(pub_id)

@app.get("/api/mode")
async def get_mode():
    return {"mode": "ORM (SQLAlchemy)" if USE_ORM else "Native SQL (asyncpg)"}

# ========== ВЕБ-ИНТЕРФЕЙС ==========
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)