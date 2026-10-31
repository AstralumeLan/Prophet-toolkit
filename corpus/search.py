"""Offline classical corpus retrieval; responses preserve source wording."""
from __future__ import annotations
import json
import sqlite3
from corpus.build import DATA, INDEX, ENGINE, build_index, fold, build


def _connect(path):
    if not path.exists():
        build_index(path)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db


def search(query, book=None, limit=5, path=INDEX):
    if not query.strip():
        raise ValueError('关键词不能为空')
    if not 1 <= limit <= 100:
        raise ValueError('limit 必须在 1–100 之间')
    q = fold(query.strip())
    params = []
    where = []
    join = ''
    if len(q) >= 3:
        join = ' JOIN fulltext f ON p.seq=f.rowid'
        where.append('fulltext MATCH ?')
        params.append('"' + q.replace('"', '""') + '"')
    # Also apply literal matching so punctuation, %, _ and quotes remain literal.
    where.append("p.folded LIKE ? ESCAPE '\\'")
    params.append('%' + q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%')
    if book:
        where.append('p.book=?')
        params.append(book)
    params.append(limit)
    with _connect(path) as db:
        rows = db.execute('SELECT p.payload FROM passages p' + join + ' WHERE ' + ' AND '.join(where) + ' ORDER BY p.seq LIMIT ?', params)
        return [json.loads(r[0]) for r in rows]


def get_passage(passage_id, path=INDEX):
    with _connect(path) as db:
        row = db.execute('SELECT * FROM passages WHERE passage_id=?', (passage_id,)).fetchone()
        if row is None:
            raise ValueError(f'未知段落: {passage_id}')
        neighbours = []
        for op, order in [('<', 'DESC'), ('>', 'ASC')]:
            r = db.execute(f'SELECT payload FROM passages WHERE book=? AND chapter=? AND seq {op} ? ORDER BY seq {order} LIMIT 1',
                           (row['book'], row['chapter'], row['seq'])).fetchone()
            neighbours.append(json.loads(r[0]) if r else None)
        return {'engine': ENGINE, 'warnings': [], 'passage': json.loads(row['payload']),
                'previous': neighbours[0], 'next': neighbours[1]}


def books(path=INDEX):
    with _connect(path) as db:
        counts = dict(db.execute('SELECT book,count(*) FROM passages GROUP BY book'))
    return {'engine': ENGINE, 'warnings': [], 'books': [dict(json.loads(l), count=counts.get(json.loads(l)['book'], 0))
            for l in (DATA / 'books.jsonl').read_text().splitlines()]}


def register(subparsers):
    p = subparsers.add_parser('corpus', help='离线经典语料与全文检索')
    sub = p.add_subparsers(dest='corpus_command', required=True)
    b = sub.add_parser('build', help='重建 SQLite FTS5 trigram 索引')
    b.add_argument('--with-tianji', action='store_true', help='选择 CC BY-NC-SA 4.0 天纪语料')
    b.set_defaults(func=lambda a: build(a.with_tianji))
    s = sub.add_parser('search', help='原文子串检索（支持繁简折叠）')
    s.add_argument('query'); s.add_argument('--book'); s.add_argument('--limit', type=int, default=5)
    s.set_defaults(func=lambda a: search(a.query, a.book, a.limit))
    g = sub.add_parser('get', help='段落及同章相邻段落 ±1')
    g.add_argument('passage_id'); g.set_defaults(func=lambda a: get_passage(a.passage_id))
    ls = sub.add_parser('books', help='书目、段落数、版本与许可')
    ls.set_defaults(func=lambda a: books())
    for command in (b, s, g, ls):
        command.add_argument('--json', action='store_true', help='兼容选项；始终输出 JSON')
