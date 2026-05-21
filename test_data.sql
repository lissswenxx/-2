-- ============================================
-- ТЕСТОВЫЕ ДАННЫЕ
-- ============================================

-- Добавление разделов литературы (иерархия)
INSERT INTO sections (name, section_type, parent_id) VALUES
    ('Художественная литература', 'genre', NULL),
    ('Научная литература', 'genre', NULL),
    ('Детективы', 'category', 1),
    ('Фантастика', 'category', 1),
    ('Информатика', 'category', 2),
    ('Программирование', 'subcategory', 5),
    ('Базы данных', 'subcategory', 6);

-- Добавление изданий
INSERT INTO publications (title, author, year, publisher, section_id, pub_type, is_current) VALUES
    ('Война и мир', 'Толстой Л.Н.', 1869, 'Русский вестник', 3, 'book', true),
    ('Преступление и наказание', 'Достоевский Ф.М.', 1866, 'Русский вестник', 3, 'book', true),
    ('1984', 'Оруэлл Д.', 1949, 'Secker & Warburg', 4, 'book', true),
    ('Наука и жизнь', 'Редколлегия', 2024, 'Наука', 2, 'magazine', true),
    ('Коммерсантъ', 'Редакция', 2024, 'Коммерсантъ', 2, 'newspaper', true);

-- Добавление книг
INSERT INTO books (publication_id, version, isbn, pages, genre) VALUES
    (1, 1, '978-5-17-118-7', 1300, 'Роман-эпопея'),
    (2, 1, '978-5-17-119-7', 700, 'Роман'),
    (3, 1, '978-5-17-120-5', 400, 'Антиутопия');

-- Добавление журналов
INSERT INTO magazines (publication_id, version, issn, issue_number, frequency) VALUES
    (4, 1, 'ISSN-1234-5678', 12, 'Ежемесячный');

-- Добавление газет
INSERT INTO newspapers (publication_id, version, issn, date_published, city) VALUES
    (5, 1, 'ISSN-8765-4321', '2024-01-15', 'Москва');

-- Демонстрация версионирования (обновление книги)
UPDATE publications SET title = '1984 (переиздание)', publisher = 'АСТ' WHERE id = 3 AND is_current = TRUE;
INSERT INTO books (publication_id, version, isbn, pages, genre) VALUES
    (3, 2, '978-5-17-120-5', 450, 'Антиутопия');