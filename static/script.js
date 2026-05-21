let currentPublicationId = null;
let currentPubType = null;

function showMessage(elementId, text, isError) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = '<div class="message ' + (isError ? 'message-error' : 'message-success') + '">' + text + '</div>';
        setTimeout(function() { if (el.innerHTML === text || el.innerHTML.includes(text)) el.innerHTML = ''; }, 3000);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text).replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

async function getMode() {
    try {
        const res = await fetch('/api/mode');
        const data = await res.json();
        document.getElementById('modeIndicator').innerText = data.mode;
    } catch(e) {
        document.getElementById('modeIndicator').innerText = 'ORM (SQLAlchemy)';
    }
}

// ========== ИЕРАРХИЯ ==========
async function createSection() {
    const name = document.getElementById('sectionName').value;
    const sectionType = document.getElementById('sectionType').value;
    let parentId = document.getElementById('parentSectionId').value;
    
    if (!name) { alert('Введите название раздела'); return; }
    parentId = (parentId === '' || parentId === '0') ? null : parseInt(parentId);
    
    try {
        const res = await fetch('/api/sections', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, section_type: sectionType, parent_id: parentId })
        });
        const data = await res.json();
        if (res.ok) {
            alert('✅ Раздел создан! ID: ' + data.id);
            document.getElementById('sectionName').value = '';
            document.getElementById('parentSectionId').value = '';
            loadTree();
        } else {
            alert('❌ Ошибка: ' + JSON.stringify(data));
        }
    } catch(e) { alert('Ошибка: ' + e.message); }
}

async function loadTree() {
    try {
        const res = await fetch('/api/sections/tree');
        const nodes = await res.json();
        if (!nodes || nodes.length === 0) {
            document.getElementById('treeContainer').innerHTML = '<i>📭 Нет разделов. Создайте первый!</i>';
            return;
        }
        let html = '';
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            let indent = '';
            for (let j = 0; j < (node.level || 1) - 1; j++) indent += '&nbsp;&nbsp;';
            let icon = '📁';
            if (node.section_type === 'genre') icon = '📖';
            else if (node.section_type === 'category') icon = '📂';
            else if (node.section_type === 'subcategory') icon = '📁';
            html += '<div>' + indent + icon + ' <b>' + escapeHtml(node.name) + '</b> (ID: ' + node.id + ', ' + node.section_type + ')</div>';
        }
        document.getElementById('treeContainer').innerHTML = html;
    } catch(e) {
        document.getElementById('treeContainer').innerHTML = '<i style="color:red">❌ Ошибка загрузки</i>';
    }
}

// ========== КНИГИ ==========
async function createBook() {
    const data = {
        title: document.getElementById('bookTitle').value,
        author: document.getElementById('bookAuthor').value,
        year: parseInt(document.getElementById('bookYear').value),
        publisher: document.getElementById('bookPublisher').value || null,
        section_id: parseInt(document.getElementById('bookSectionId').value),
        isbn: document.getElementById('bookIsbn').value,
        pages: parseInt(document.getElementById('bookPages').value),
        genre: document.getElementById('bookGenre').value || null
    };
    
    if (!data.title || !data.author || !data.year || !data.section_id || !data.isbn || !data.pages) {
        showMessage('bookMessage', '❌ Заполните все поля!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/books', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (res.ok) {
            showMessage('bookMessage', '✅ Книга создана! ID: ' + result.id + ', версия: ' + result.version, false);
            clearBookForm();
            loadBooks();
        } else {
            showMessage('bookMessage', '❌ Ошибка: ' + (result.detail || 'Неизвестная'), true);
        }
    } catch(e) { showMessage('bookMessage', '❌ Ошибка: ' + e.message, true); }
}

function clearBookForm() {
    document.getElementById('bookTitle').value = '';
    document.getElementById('bookAuthor').value = '';
    document.getElementById('bookYear').value = '';
    document.getElementById('bookPublisher').value = '';
    document.getElementById('bookSectionId').value = '';
    document.getElementById('bookIsbn').value = '';
    document.getElementById('bookPages').value = '';
    document.getElementById('bookGenre').value = '';
}

async function loadBooks() {
    try {
        const res = await fetch('/api/books');
        if (!res.ok) { document.getElementById('booksList').innerHTML = '<i style="color:red">❌ Ошибка загрузки</i>'; return; }
        const books = await res.json();
        if (!books || books.length === 0) {
            document.getElementById('booksList').innerHTML = '<i>📭 Нет книг. Добавьте первую!</i>';
            return;
        }
        let html = '<table><thead><tr><th>ID</th><th>Название</th><th>Автор</th><th>ISBN</th><th>Страниц</th><th></th></tr></thead><tbody>';
        for (let i = 0; i < books.length; i++) {
            const b = books[i];
            html += '<tr>';
            html += '<td>' + b.id + '</td>';
            html += '<td>' + escapeHtml(b.title) + '</td>';
            html += '<td>' + escapeHtml(b.author) + '</td>';
            html += '<td>' + escapeHtml(b.isbn) + '</td>';
            html += '<td>' + (b.pages || '-') + '</td>';
            html += '<td><button onclick="selectPublication(' + b.id + ')">🔍 Выбрать</button></td>';
            html += '</tr>';
        }
        html += '</tbody></table>';
        document.getElementById('booksList').innerHTML = html;
    } catch(e) {
        document.getElementById('booksList').innerHTML = '<i style="color:red">❌ Ошибка: ' + e.message + '</i>';
    }
}

// ========== ЖУРНАЛЫ ==========
async function createMagazine() {
    const data = {
        title: document.getElementById('magTitle').value,
        author: document.getElementById('magAuthor').value,
        year: parseInt(document.getElementById('magYear').value),
        publisher: document.getElementById('magPublisher').value || null,
        section_id: parseInt(document.getElementById('magSectionId').value),
        issn: document.getElementById('magIssn').value,
        issue_number: parseInt(document.getElementById('magIssueNumber').value),
        frequency: document.getElementById('magFrequency').value || null
    };
    
    if (!data.title || !data.author || !data.year || !data.section_id || !data.issn || !data.issue_number) {
        showMessage('magMessage', '❌ Заполните все поля!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/magazines', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (res.ok) {
            showMessage('magMessage', '✅ Журнал создан! ID: ' + result.id + ', версия: ' + result.version, false);
            clearMagazineForm();
        } else {
            showMessage('magMessage', '❌ Ошибка: ' + (result.detail || 'Неизвестная'), true);
        }
    } catch(e) { showMessage('magMessage', '❌ Ошибка: ' + e.message, true); }
}

function clearMagazineForm() {
    document.getElementById('magTitle').value = '';
    document.getElementById('magAuthor').value = '';
    document.getElementById('magYear').value = '';
    document.getElementById('magPublisher').value = '';
    document.getElementById('magSectionId').value = '';
    document.getElementById('magIssn').value = '';
    document.getElementById('magIssueNumber').value = '';
    document.getElementById('magFrequency').value = '';
}

// ========== ГАЗЕТЫ ==========
async function createNewspaper() {
    const data = {
        title: document.getElementById('newsTitle').value,
        author: document.getElementById('newsAuthor').value,
        year: parseInt(document.getElementById('newsYear').value),
        publisher: document.getElementById('newsPublisher').value || null,
        section_id: parseInt(document.getElementById('newsSectionId').value),
        issn: document.getElementById('newsIssn').value,
        date_published: document.getElementById('newsDate').value,
        city: document.getElementById('newsCity').value || null
    };
    
    if (!data.title || !data.author || !data.year || !data.section_id || !data.issn || !data.date_published) {
        showMessage('newsMessage', '❌ Заполните все поля!', true);
        return;
    }
    
    try {
        const res = await fetch('/api/newspapers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (res.ok) {
            showMessage('newsMessage', '✅ Газета создана! ID: ' + result.id + ', версия: ' + result.version, false);
            clearNewspaperForm();
        } else {
            showMessage('newsMessage', '❌ Ошибка: ' + (result.detail || 'Неизвестная'), true);
        }
    } catch(e) { showMessage('newsMessage', '❌ Ошибка: ' + e.message, true); }
}

function clearNewspaperForm() {
    document.getElementById('newsTitle').value = '';
    document.getElementById('newsAuthor').value = '';
    document.getElementById('newsYear').value = '';
    document.getElementById('newsPublisher').value = '';
    document.getElementById('newsSectionId').value = '';
    document.getElementById('newsIssn').value = '';
    document.getElementById('newsDate').value = '';
    document.getElementById('newsCity').value = '';
}

// ========== ПОИСК ==========
async function searchPublication() {
    const id = document.getElementById('searchId').value;
    if (!id) { alert('Введите ID издания'); return; }
    
    try {
        let res = await fetch('/api/books/' + id);
        if (res.ok) {
            const data = await res.json();
            currentPublicationId = data.id;
            currentPubType = 'book';
            displayPublicationInfo(data, 'Книга');
            return;
        }
        
        alert('Издание не найдено');
        currentPublicationId = null;
    } catch(e) {
        document.getElementById('publicationInfo').innerHTML = '<div class="message message-error">❌ Ошибка: ' + e.message + '</div>';
    }
}

function displayPublicationInfo(data, type) {
    let html = '<div class="publication-info"><h3>📖 ' + type + ' (текущая версия)</h3>';
    html += '<p><b>ID:</b> ' + data.id + ' | <b>Версия:</b> ' + data.version + ' | <b>Статус:</b> ' + (data.is_current ? '✅ Актуальная' : '❌ Неактуальная') + '</p>';
    html += '<p><b>Название:</b> ' + escapeHtml(data.title) + '</p>';
    html += '<p><b>Автор/Редакция:</b> ' + escapeHtml(data.author) + '</p>';
    html += '<p><b>Год:</b> ' + data.year + '</p>';
    html += '<p><b>Издательство:</b> ' + escapeHtml(data.publisher || '-') + '</p>';
    
    if (type === 'Книга') {
        html += '<p><b>ISBN:</b> ' + escapeHtml(data.isbn) + '</p>';
        html += '<p><b>Страниц:</b> ' + data.pages + '</p>';
        html += '<p><b>Жанр:</b> ' + escapeHtml(data.genre || '-') + '</p>';
    }
    html += '</div>';
    document.getElementById('publicationInfo').innerHTML = html;
}

function selectPublication(id) {
    document.getElementById('searchId').value = id;
    searchPublication();
}

// ========== ИСТОРИЯ ВЕРСИЙ ==========
async function showHistory() {
    const id = document.getElementById('searchId').value;
    if (!id) { alert('Введите ID издания'); return; }
    
    try {
        const res = await fetch('/api/publications/' + id + '/history');
        const history = await res.json();
        if (!history || history.length === 0) {
            document.getElementById('historyInfo').innerHTML = '<p>📜 Нет истории версий</p>';
            return;
        }
        
        let html = '<h3>📜 История версий</h3><table><thead><tr><th>Версия</th><th>Дата</th><th>Название</th><th>Автор</th><th>Статус</th></tr></thead><tbody>';
        for (let i = 0; i < history.length; i++) {
            const v = history[i];
            html += '<tr style="' + (v.is_current ? 'background:#d4edda' : '') + '">';
            html += '<td>' + v.version + '</td>';
            html += '<td>' + new Date(v.created_at).toLocaleString() + '</td>';
            html += '<td>' + escapeHtml(v.title) + '</td>';
            html += '<td>' + escapeHtml(v.author) + '<td>';
            html += '<td>' + (v.is_current ? '<span class="badge badge-current">✅ Актуальная</span>' : '<span class="badge badge-old">📦 Старая</span>') + '</td>';
            html += '</tr>';
        }
        html += '</tbody></table>';
        document.getElementById('historyInfo').innerHTML = html;
    } catch(e) {
        document.getElementById('historyInfo').innerHTML = '<p style="color:red">❌ Ошибка: ' + e.message + '</p>';
    }
}

// ========== ОБНОВЛЕНИЕ ==========
function openUpdateModal() {
    if (!currentPublicationId) { alert('Сначала найдите издание (кнопка "Найти")'); return; }
    document.getElementById('updateModal').style.display = 'block';
    document.getElementById('updateTitle').value = '';
    document.getElementById('updateAuthor').value = '';
    document.getElementById('updatePublisher').value = '';
    document.getElementById('updateMessage').innerHTML = '';
}

function closeUpdateModal() { document.getElementById('updateModal').style.display = 'none'; }

async function updatePublication() {
    const title = document.getElementById('updateTitle').value;
    const author = document.getElementById('updateAuthor').value;
    const publisher = document.getElementById('updatePublisher').value;
    const updateData = {};
    if (title) updateData.title = title;
    if (author) updateData.author = author;
    if (publisher) updateData.publisher = publisher;
    
    if (Object.keys(updateData).length === 0) {
        document.getElementById('updateMessage').innerHTML = '<div style="color:red">Заполните хотя бы одно поле</div>';
        return;
    }
    
    try {
        const res = await fetch('/api/publications/' + currentPublicationId, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });
        const result = await res.json();
        if (res.ok) {
            document.getElementById('updateMessage').innerHTML = '<div style="color:green">✅ Обновлено! Новая версия: ' + result.version + '</div>';
            setTimeout(function() {
                closeUpdateModal();
                searchPublication();
                showHistory();
                loadBooks();
            }, 1500);
        } else {
            document.getElementById('updateMessage').innerHTML = '<div style="color:red">❌ Ошибка: ' + (result.detail || 'Неизвестная') + '</div>';
        }
    } catch(e) {
        document.getElementById('updateMessage').innerHTML = '<div style="color:red">❌ Ошибка: ' + e.message + '</div>';
    }
}

// ========== УДАЛЕНИЕ ==========
async function deletePublication() {
    if (!currentPublicationId) { alert('Сначала найдите издание'); return; }
    if (!confirm('🗑️ Удалить издание с ID ' + currentPublicationId + '? (логическое удаление)')) return;
    
    try {
        const res = await fetch('/api/publications/' + currentPublicationId, { method: 'DELETE' });
        const data = await res.json();
        if (data.deleted) {
            alert('✅ Издание логически удалено');
            searchPublication();
            showHistory();
            loadBooks();
        } else {
            alert('❌ Ошибка удаления');
        }
    } catch(e) { alert('Ошибка: ' + e.message); }
}

window.onclick = function(event) { if (event.target === document.getElementById('updateModal')) closeUpdateModal(); }

getMode();
loadTree();
loadBooks();