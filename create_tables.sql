-- ============================================
-- БИБЛИОТЕЧНАЯ СИСТЕМА
-- ============================================

-- 1. ИЕРАРХИЯ: разделы литературы (древовидная структура)
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    section_type VARCHAR(50) NOT NULL, -- 'genre', 'category', 'subcategory'
    parent_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. НАСЛЕДОВАНИЕ: базовая таблица изданий с версионированием
CREATE TABLE publications (
    id SERIAL,
    version INTEGER NOT NULL DEFAULT 1,
    title VARCHAR(300) NOT NULL,
    author VARCHAR(200) NOT NULL,
    year INTEGER NOT NULL,
    publisher VARCHAR(200),
    section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
    pub_type VARCHAR(50) NOT NULL, -- 'book', 'magazine', 'newspaper'
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, version)
);

-- 3. НАСЛЕДНИК: КНИГА (Book)
CREATE TABLE books (
    publication_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    isbn VARCHAR(20) NOT NULL,
    pages INTEGER NOT NULL,
    genre VARCHAR(100),
    PRIMARY KEY (publication_id, version),
    FOREIGN KEY (publication_id, version) REFERENCES publications(id, version) ON DELETE CASCADE
);

-- 4. НАСЛЕДНИК: ЖУРНАЛ (Magazine)
CREATE TABLE magazines (
    publication_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    issn VARCHAR(20) NOT NULL,
    issue_number INTEGER NOT NULL,
    frequency VARCHAR(50),
    PRIMARY KEY (publication_id, version),
    FOREIGN KEY (publication_id, version) REFERENCES publications(id, version) ON DELETE CASCADE
);

-- 5. НАСЛЕДНИК: ГАЗЕТА (Newspaper)
CREATE TABLE newspapers (
    publication_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    issn VARCHAR(20) NOT NULL,
    date_published DATE NOT NULL,
    city VARCHAR(100),
    PRIMARY KEY (publication_id, version),
    FOREIGN KEY (publication_id, version) REFERENCES publications(id, version) ON DELETE CASCADE
);

-- 6. Индексы для производительности
CREATE INDEX idx_sections_parent ON sections(parent_id);
CREATE INDEX idx_publications_current ON publications(is_current);
CREATE INDEX idx_publications_section ON publications(section_id);
CREATE INDEX idx_publications_type ON publications(pub_type);
CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_magazines_issn ON magazines(issn);
CREATE INDEX idx_newspapers_date ON newspapers(date_published);