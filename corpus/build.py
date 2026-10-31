"""Offline, reproducible normalisation and SQLite FTS5 index construction."""
from __future__ import annotations
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('PROPHET_CORPUS_DATA', ROOT / 'corpus/data'))
INDEX = Path(os.environ.get('PROPHET_CORPUS_INDEX', ROOT / 'corpus/index.sqlite'))
VENDOR = ROOT / 'vendor/chinese-fortune'
ZIWEI = Path(os.environ.get('PROPHET_RENHUAI_DIR', ROOT / 'vendor/ziwei-doushu'))
ENGINE = {'name': 'corpus', 'version': '1.0.0', 'rules': {
    'search': 'literal substring; FTS5 trigram >=3 characters, escaped LIKE otherwise',
    'normalisation': 'single-character traditional-to-simplified fold; original text retained',
    'neighbours': 'same book and chapter, original passage order'}}


def _write(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')


def normalise_sources(with_tianji=False):
    """Generate local JSONL from pinned upstream checkouts; restricted course is opt-in."""
    DATA.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((VENDOR / 'knowledge/manifest.json').read_text())
    books, rows = [], []
    for meta in manifest['books']:
        book = meta['id']
        if book not in ('yuanhai', 'ziping', 'ditian', 'qiongtong', 'sanming', 'ziwei'):
            continue
        books.append(dict(meta, book=book))
        for path in sorted((VENDOR / 'knowledge/books' / book).glob('*.json')):
            chapter = json.loads(path.read_text())
            for p in chapter['passages']:
                rows.append({**{k: v for k, v in chapter.items() if k != 'passages'}, **p,
                    'book': book, 'book_title': meta['title'], 'chapter': chapter['chapter_id'],
                    'title': chapter['title'], 'source': chapter['source_url'],
                    'license': meta['license'], 'edition': meta.get('edition'),
                    'selection_info': {k: v for k, v in meta.items() if 'select' in k or 'scope' in k}})
    _write(DATA / 'ziping_classics.jsonl', rows)
    # Parse string literals only; never execute TypeScript. The local data format
    # consists of chapter titles followed by {id, idx, text} paragraph objects.
    literal = r"'(?:\\.|[^'\\])*'"
    field = re.compile(r'\b(title|id|text):\s*(' + literal + ')')
    rows = []
    for book in ('quanshu', 'quanji', 'gusuifu'):
        path = ZIWEI / 'lib/classics/data' / (book + '.ts')
        text = path.read_text()
        title, chapter, pid = None, None, None
        count = 0
        for match in field.finditer(text):
            key, value = match[1], ast.literal_eval(match[2])
            if key == 'title':
                if title is None:
                    title = value
                else:
                    chapter = value
            elif key == 'id':
                pid = value
            elif pid is not None:
                count += 1
                rows.append({'passage_id': pid, 'book': book, 'book_title': title,
                    'chapter': chapter, 'title': chapter, 'text': value,
                    'source': f'https://github.com/Renhuai123/ziwei-doushu/blob/main/lib/classics/data/{book}.ts',
                    'source_url': f'https://github.com/Renhuai123/ziwei-doushu/blob/main/lib/classics/data/{book}.ts',
                    'revision': 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest(),
                    'layer': 'upstream_classics_selection', 'transcription_status': 'not_collated_modern_editorial_content_possible',
                    'license': 'Public domain historical work; upstream selection, not a verified edition'})
                pid = None
        if not count:
            raise ValueError(f'No paragraphs parsed: {path}')
        books.append({'book': book, 'title': title, 'license': 'Public domain historical work',
                      'edition': 'Upstream core selections; not a collated full text',
                      'upstream_header': text.split('*/', 1)[0] + '*/'})
    _write(DATA / 'ziwei_classics.jsonl', rows)
    # Default rebuild also removes previously opted-in course material.
    for name in ('tianji.jsonl', 'tianji-LICENSE.md'):
        (DATA / name).unlink(missing_ok=True)
    if with_tianji:
        rows = []
        path = ZIWEI / 'docs/tianji-ziwei/entries.jsonl'
        for i, line in enumerate(path.read_text().splitlines(), 1):
            p = json.loads(line)
            rows.append({**p, 'original_book': p['book'], 'book': 'tianji',
                'passage_id': f'tianji:{i:05d}', 'chapter': p['book'],
                'title': ' / '.join(filter(None, [p.get('h2'), p.get('h3')])), 'text': p['quote'],
                'source': f'https://www.bilibili.com/video/{p["bvid"]}?p={p["part"]}&t={p["t_hms"]}',
                'layer': 'course_quote', 'license': 'CC BY-NC-SA 4.0',
                'attribution': '倪海厦《天纪》；Renhuai123/ziwei-doushu 结构化整理'})
        _write(DATA / 'tianji.jsonl', rows)
        books.append({'book': 'tianji', 'title': '倪师天纪', 'license': 'CC BY-NC-SA 4.0',
                      'attribution': '倪海厦及其权利继承人；Renhuai123/ziwei-doushu 整理；个人学习研究'})
        shutil.copyfile(ZIWEI / 'docs/tianji-ziwei/LICENSE.md', DATA / 'tianji-LICENSE.md')
    for book, title in [('nakshatra', '二十七月宿简表'), ('parashara', '帕拉沙拉规则摘要')]:
        books.append({'book': book, 'title': title, 'license': 'CC0-1.0 compiled summaries', 'edition': 'Prophet concise compilation'})
    _write(DATA / 'books.jsonl', books)
    shutil.copyfile(VENDOR / 'assets/han-variants.json', DATA / 'han-variants.json')
    shutil.copyfile(VENDOR / 'LICENSE', DATA / 'chinese-fortune-LICENSE')


def fold(text):
    mapping = json.loads((DATA / 'han-variants.json').read_text())['mapping']
    return text.translate(str.maketrans(mapping)).lower()


def build_index(path=INDEX):
    """Atomically replace only the derived index, never source files."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='corpus-', suffix='.sqlite', dir=path.parent)
    import os
    os.close(fd)
    try:
        with sqlite3.connect(temp) as db:
            db.execute('CREATE TABLE passages (seq INTEGER PRIMARY KEY, passage_id TEXT UNIQUE, book TEXT, chapter TEXT, payload TEXT, folded TEXT)')
            db.execute("CREATE VIRTUAL TABLE fulltext USING fts5(folded, tokenize='trigram')")
            db.execute('CREATE INDEX book_order ON passages(book, chapter, seq)')
            table = str.maketrans(json.loads((DATA / 'han-variants.json').read_text())['mapping'])
            for file in sorted(DATA.glob('*.jsonl')):
                if file.name == 'books.jsonl':
                    continue
                for line in file.read_text().splitlines():
                    p = json.loads(line)
                    folded = (p.get('title', '') + '\n' + p['text']).translate(table).lower()
                    cur = db.execute('INSERT INTO passages(passage_id,book,chapter,payload,folded) VALUES(?,?,?,?,?)',
                        (p['passage_id'], p['book'], p.get('chapter', ''), json.dumps(p, ensure_ascii=False), folded))
                    db.execute('INSERT INTO fulltext(rowid,folded) VALUES(?,?)', (cur.lastrowid, folded))
            count = db.execute('SELECT count(*) FROM passages').fetchone()[0]
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return {'engine': ENGINE, 'warnings': [], 'passages': count, 'sqlite_version': sqlite3.sqlite_version,
            'tokenizer': 'trigram', 'index': str(path)}


def build(with_tianji=False, path=INDEX):
    normalise_sources(with_tianji=with_tianji)
    result = build_index(path)
    if with_tianji:
        result['warnings'].append('天纪 CC BY-NC-SA 4.0: Attribution (倪海厦；Renhuai123/ziwei-doushu), NonCommercial, ShareAlike. See local tianji-LICENSE.md.')
    return result
