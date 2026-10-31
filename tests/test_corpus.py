"""Offline reference and CLI regressions for locally generated corpora."""
import json
from pathlib import Path
import subprocess
import tempfile

from corpus.build import DATA, ROOT, build_index
from corpus.search import books, get_passage, search


def _cli(*args):
    p = subprocess.run([str(ROOT / 'bin/prophet'), 'corpus', *args], cwd=ROOT,
                       capture_output=True, text=True, timeout=10)
    assert p.returncode == 0, p.stderr + p.stdout
    return json.loads(p.stdout)


def test_corpus_build_and_autobuild():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'index.sqlite'
        # Search builds missing indexes without access to the upstream repositories.
        assert search('用神', 'ziping', 1, path)
        result = build_index(path)
        assert result['passages'] > 2000 and result['tokenizer'] == 'trigram'
        assert result['engine']['rules'] and result['warnings'] == []
        assert sum(b['count'] for b in books(path)['books']) == result['passages']


def test_corpus_ziping_public_reference_and_neighbours():
    # Public-domain 子平真诠, 一、論十干十二支, opening paragraph.
    # Local transcription source: https://www.donglishuzhai.net/chapter/3714.html
    p = get_passage('ziping:c001:p0001')
    assert p['passage']['text'].startswith('天地之間，一氣而已。惟有動靜，遂分陰陽')
    assert p['previous'] is None
    assert p['next']['passage_id'] == 'ziping:c001:p0002'
    assert p['passage']['layer'] == 'base_text'
    assert p['passage']['revision'].startswith('sha256:')
    hits = search('天地之间', 'ziping')
    assert any(h['passage_id'] == 'ziping:c001:p0001' for h in hits)
    assert all('天地之间' not in h['text'] for h in hits)
    assert search('用神', 'ziping')
    assert search('阴阳', 'ziping')  # two characters: escaped LIKE fallback
    assert search('天地之间', 'tianji') == []
    middle = get_passage('ziping:c001:p0002')
    assert middle['previous']['passage_id'] == 'ziping:c001:p0001'
    assert middle['next']['passage_id'] == 'ziping:c001:p0003'


def test_corpus_tables_reference():
    # Standard 27-mansion Jyotisha scheme (BPHS nakshatra/Vimshottari tradition):
    # Ashwini begins the cycle, ruled by Ketu; Revati ends it, ruled by Mercury.
    rows = [json.loads(l) for l in (DATA / 'nakshatra.jsonl').read_text().splitlines()]
    assert len(rows) == 27
    assert rows[0]['name_sanskrit'] == 'Ashwini' and rows[0]['lord'] == 'Ketu'
    assert rows[-1]['name_sanskrit'] == 'Revati' and rows[-1]['lord'] == 'Mercury'
    assert all(r['layer'] == 'compiled_summary' and r['deity'] and r['traits'] for r in rows)
    # BPHS graha drishti: Mars has full special aspects on fourth/eighth, plus seventh.
    mars = get_passage('parashara:drishti:Mars')['passage']
    assert mars['full_aspect_houses'] == [4, 7, 8]
    sun = get_passage('parashara:planet:Sun')['passage']
    assert sun['exaltation_sign'] == 'Aries' and sun['exaltation_degree'] == 10


def test_corpus_books_licences_and_counts():
    listing = {b['book']: b for b in books()['books']}
    assert all(b['count'] > 0 and b['license'] for b in listing.values())
    assert listing['nakshatra']['count'] == 27
    if 'tianji' in listing:
        assert listing['tianji']['count'] == 1848
        assert listing['tianji']['license'] == 'CC BY-NC-SA 4.0'
    assert all(name in listing for name in ['yuanhai', 'ziping', 'ditian', 'qiongtong', 'quanshu', 'quanji', 'gusuifu'])
    for book in ['yuanhai', 'ziping', 'ditian', 'qiongtong', 'sanming', 'ziwei']:
        files = sorted((ROOT / 'vendor/chinese-fortune/knowledge/books' / book).glob('*.json'))
        expected = sum(len(json.loads(f.read_text())['passages']) for f in files)
        assert listing[book]['count'] == expected
    if 'tianji' in listing:
        from corpus.build import ZIWEI
        assert (DATA / 'tianji-LICENSE.md').read_bytes() == (ZIWEI / 'docs/tianji-ziwei/LICENSE.md').read_bytes()


def test_corpus_cli_smoke():
    assert _cli('build', *(['--with-tianji'] if (DATA/'tianji.jsonl').exists() else []))['passages'] > 2000
    hits = _cli('search', '用神', '--book', 'ziping', '--limit', '2', '--json')
    assert 1 <= len(hits) <= 2 and all(h['book'] == 'ziping' for h in hits)
    assert _cli('get', hits[0]['passage_id'])['passage']['passage_id'] == hits[0]['passage_id']
    assert _cli('books')['books']
    assert _cli('search', 'zzzz-unmatched-phrase') == []


def test_corpus_literal_search_and_errors():
    for q in ['%', '_', '"', '\\', '" OR "']:
        hits = search(q, limit=100)
        assert all(q.lower() in (h['title'] + '\n' + h['text']).lower() for h in hits)
    for query, limit in [('', 5), ('用神', 0), ('用神', 101)]:
        try:
            search(query, limit=limit)
        except ValueError:
            pass
        else:
            assert False, 'invalid query must fail'


def test_corpus_normalisation_default_and_opt_in():
    """Exercise generation in an empty temp data dir, including opt-in removal.

    Never consult or mutate a user's existing generated course collection.
    """
    import shutil
    from unittest.mock import patch
    import corpus.build as builder
    with tempfile.TemporaryDirectory() as directory:
        data = Path(directory)/'data'
        data.mkdir()
        for name in ('nakshatra.jsonl', 'parashara.jsonl'):
            shutil.copyfile(DATA/name, data/name)
        with patch.object(builder, 'DATA', data):
            result = builder.build(path=Path(directory)/'index.sqlite')
            assert result['passages'] > 2000
            assert not (data/'tianji.jsonl').exists()
            listing = [json.loads(l)['book'] for l in (data/'books.jsonl').read_text().splitlines()]
            assert 'tianji' not in listing
            if (builder.ZIWEI/'docs/tianji-ziwei/entries.jsonl').is_file():
                course = builder.build(True, path=Path(directory)/'index.sqlite')
                assert course['passages'] == result['passages'] + 1848
                terms = ' '.join(course['warnings'])
                assert all(term in terms for term in ('CC BY-NC-SA 4.0', 'Attribution', 'NonCommercial', 'ShareAlike'))
                assert (data/'tianji-LICENSE.md').is_file()
                builder.build(path=Path(directory)/'index.sqlite')
                assert not (data/'tianji.jsonl').exists()
                assert not (data/'tianji-LICENSE.md').exists()


def test_corpus_missing_opt_in_source_is_explicit():
    import shutil
    from unittest.mock import patch
    import corpus.build as builder
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        data = root/'data'
        data.mkdir()
        (root/'lib/classics').mkdir(parents=True)
        # Only the public-domain TS sources exist; course material is absent.
        (root/'lib/classics/data').symlink_to(builder.ZIWEI/'lib/classics/data', target_is_directory=True)
        for name in ('nakshatra.jsonl', 'parashara.jsonl'):
            shutil.copyfile(DATA/name, data/name)
        with patch.object(builder, 'DATA', data), patch.object(builder, 'ZIWEI', root):
            assert builder.build(path=root/'index.sqlite')['passages'] > 2000
            try:
                builder.build(True, path=root/'index.sqlite')
            except FileNotFoundError:
                pass
            else:
                raise AssertionError('Explicit course opt-in must not silently succeed without its source')


# Every corpus test builds an isolated collection. The release contains no generated
# upstream text, and selftest must not modify an existing user's collection.
def isolated_corpus(fn):
    import os
    import shutil
    from functools import wraps, partial
    from unittest.mock import patch
    import corpus.build as builder
    import importlib
    retrieval = importlib.import_module('corpus.search')
    @wraps(fn)
    def isolated():
        source = DATA
        with tempfile.TemporaryDirectory(prefix='prophet-corpus-') as directory:
            data = Path(directory)/'data'
            data.mkdir()
            index = Path(directory)/'index.sqlite'
            for name in ('nakshatra.jsonl', 'parashara.jsonl'):
                shutil.copyfile(source/name, data/name)
            with patch.object(builder, 'DATA', data), patch.object(retrieval, 'DATA', data), \
                 patch.dict(os.environ, {'PROPHET_CORPUS_DATA': str(data), 'PROPHET_CORPUS_INDEX': str(index)}), \
                 patch.dict(globals(), {'DATA': data,
                     'search': lambda *args, **kw: retrieval.search(*args, **(kw if len(args) >= 4 or 'path' in kw else dict(kw, path=index))),
                     'get_passage': partial(retrieval.get_passage, path=index),
                     'books': lambda *args, **kw: retrieval.books(*args, **(kw if args or 'path' in kw else dict(kw, path=index)))}):
                builder.build(with_tianji=(source/'tianji.jsonl').exists(), path=index)
                return fn()
    return isolated

for _name in [name for name in globals() if name.startswith('test_')]:
    globals()[_name] = isolated_corpus(globals()[_name])
