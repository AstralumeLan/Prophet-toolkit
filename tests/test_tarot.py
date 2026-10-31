import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from western.tarot import deck,draw,lookup,draw_record
from core.draws import draw_once


def test_tarot_deck_reference():
    # Waite, The Pictorial Key to the Tarot (1910), Parts II/III:
    # 22 trumps, four suits of 14; Strength VIII and Justice XI in RWS order.
    cards=deck()
    assert len(cards)==len({c['id'] for c in cards})==78
    assert len({c['name_en'] for c in cards})==78
    assert sum(c['arcana']=='major' for c in cards)==22
    assert lookup('Strength')['card']['number']==8
    assert lookup('Justice')['card']['number']==11
    assert all(c['upright'] and c['reversed'] and c['name_zh'] for c in cards)


def test_tarot_seed_and_journal():
    assert draw(42,'celtic')==draw(42,'celtic')
    assert len({c['id'] for c in draw(42,'celtic')})==10
    with TemporaryDirectory() as t:
        path=Path(t)/'draws.jsonl'
        first=draw_once('tarot-three','test',42,lambda s:draw(s,'three'),path=path)
        again=draw_once('tarot-three','test',42,lambda s:1/0,path=path)
        assert again['reused'] and again['result']==first['result']
        assert len(path.read_text().splitlines())==1


def test_tarot_cli():
    for args in (['draw','--spread','three','--question','tarot smoke test','--seed','98765','--no-record'],['card','愚人']):
        p=subprocess.run(['bin/prophet','tarot',*args],capture_output=True,text=True)
        assert p.returncode==0,p.stdout+p.stderr
        assert json.loads(p.stdout)['engine']['name']=='western.tarot'


def test_tarot_reuses_older_seed():
    with TemporaryDirectory() as t:
        path=Path(t)/'draws.jsonl'
        a=draw_record('one','old seed test',10,path=path)
        draw_record('one','old seed test',11,path=path)
        b=draw_record('one','old seed test',10,path=path)
        assert b['reused'] and b['result']==a['result'] and b['time']==a['time']
        assert len(path.read_text().splitlines())==2
