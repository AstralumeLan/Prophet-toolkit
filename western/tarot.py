"""Seeded Rider-Waite-Smith draws with the shared append-only draw journal."""
import json
import random
from pathlib import Path
from core.draws import draw_once, find, DRAWS

ENGINE={'name':'western.tarot','version':'1.0.0','rules':{'deck':'RWS 78','shuffle':'random.Random(seed).shuffle','reversal_probability':0.5,'meanings':'Waite 1910 Part III; original keyword paraphrases'}}
SPREADS={'one':['focus'],'three':['past','present','future'],'celtic':['present','crossing','foundation','past','conscious aim','near future','self','environment','hopes and fears','outcome']}

def deck():
    return json.loads((Path(__file__).parent/'data/tarot_rws.json').read_text(encoding='utf-8'))['cards']

def draw(seed,spread='one'):
    rng=random.Random(seed); cards=deck(); rng.shuffle(cards)
    result=[]
    for position,c in zip(SPREADS[spread],cards):
        reverse=rng.random()<0.5
        result.append({**c,'position':position,'orientation':'reversed' if reverse else 'upright','keywords':c['reversed' if reverse else 'upright']})
    return result

def lookup(name):
    key=name.casefold().strip()
    cards=[c for c in deck() if key in (c['id'].casefold(),c['name_en'].casefold(),c['name_zh'])]
    if not cards: raise ValueError('Unknown card; use English name, Chinese name, or card id')
    return {'engine':ENGINE,'warnings':[],'card':cards[0]}

def draw_record(spread,question,seed=None,tz='Asia/Shanghai',no_record=False,path=DRAWS):
    method='tarot-'+spread
    previous=find(method,question,seed,path) if seed is not None else None
    # The shared helper checks the latest question entry. Preserve an older seed too.
    rec=draw_once(method,question,seed,lambda s:previous['result'] if previous else draw(s,spread),tz=tz,no_record=no_record or previous is not None,path=path)
    return {**previous,'reused':True} if previous else rec

def run(a):
    rec=draw_record(a.spread,a.question,a.seed,a.tz,a.no_record)
    return {'engine':ENGINE,'warnings':[rec['redraw_warning']] if rec.get('redraw_warning') else [],**rec}

def register(subparsers):
    p=subparsers.add_parser('tarot',help='RWS 塔罗'); sp=p.add_subparsers(dest='sub',required=True)
    d=sp.add_parser('draw'); d.add_argument('--spread',choices=list(SPREADS),default='one'); d.add_argument('--question',required=True); d.add_argument('--seed',type=int); d.add_argument('--no-record',action='store_true'); d.add_argument('--tz',default='Asia/Shanghai'); d.add_argument('--json',action='store_true'); d.set_defaults(func=run)
    c=sp.add_parser('card'); c.add_argument('name'); c.add_argument('--json',action='store_true'); c.set_defaults(func=lambda a:lookup(a.name))
