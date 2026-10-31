"""Table-driven trigger lookups, not personal predictions.

Selected compatibility tables adapted from chinese-fortune (MIT, ShousenZHANG;
see vendor/chinese-fortune/LICENSE). No vendor code/data is loaded at runtime.
Classical passage pointers identify evidence scope, not a collated edition.
"""
from lunar_python.util import LunarUtil

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
GROUPS = ('申子辰', '寅午戌', '巳酉丑', '亥卯未')
SEASONS = ('亥子丑', '寅卯辰', '巳午未', '申酉戌')
TABLES = {'天乙贵人': {'甲': ['丑', '未'],
          '戊': ['丑', '未'],
          '庚': ['丑', '未'],
          '乙': ['子', '申'],
          '己': ['子', '申'],
          '丙': ['亥', '酉'],
          '丁': ['亥', '酉'],
          '壬': ['卯', '巳'],
          '癸': ['卯', '巳'],
          '辛': ['午', '寅']},
 '文昌贵人': {'甲': '巳', '乙': '午', '丙': '申', '戊': '申', '丁': '酉', '己': '酉', '庚': '亥', '辛': '子', '壬': '寅', '癸': '卯'},
 '太极贵人': {'甲': ['子', '午'],
          '乙': ['子', '午'],
          '丙': ['卯', '酉'],
          '丁': ['卯', '酉'],
          '戊': ['辰', '戌', '丑', '未'],
          '己': ['辰', '戌', '丑', '未'],
          '庚': ['寅', '亥'],
          '辛': ['寅', '亥'],
          '壬': ['巳', '申'],
          '癸': ['巳', '申']},
 '国印贵人': {'甲': '戌', '乙': '亥', '丙': '丑', '丁': '寅', '戊': '丑', '己': '寅', '庚': '辰', '辛': '巳', '壬': '未', '癸': '申'},
 '学堂': {'甲': '亥', '乙': '午', '丙': '寅', '丁': '酉', '戊': '寅', '己': '酉', '庚': '巳', '辛': '子', '壬': '申', '癸': '卯'},
 '词馆': {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳', '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'},
 '天德贵人': {'寅月': '丁',
          '卯月': '申',
          '辰月': '壬',
          '巳月': '辛',
          '午月': '亥',
          '未月': '甲',
          '申月': '癸',
          '酉月': '寅',
          '戌月': '丙',
          '亥月': '乙',
          '子月': '巳',
          '丑月': '庚'},
 '月德贵人': {'寅午戌': '丙', '申子辰': '壬', '巳酉丑': '庚', '亥卯未': '甲'},
 '天德合': {'寅月': '壬',
         '卯月': '巳',
         '辰月': '丁',
         '巳月': '丙',
         '午月': '寅',
         '未月': '己',
         '申月': '戊',
         '酉月': '亥',
         '戌月': '辛',
         '亥月': '庚',
         '子月': '申',
         '丑月': '乙'},
 '月德合': {'寅午戌': '辛', '申子辰': '丁', '巳酉丑': '乙', '亥卯未': '己'},
 '天厨贵人': {'甲': '巳', '乙': '午', '丙': '子', '丁': '巳', '戊': '午', '己': '申', '庚': '寅', '辛': '午', '壬': '酉', '癸': '亥'},
 '红鸾': {'子': '卯',
        '丑': '寅',
        '寅': '丑',
        '卯': '子',
        '辰': '亥',
        '巳': '戌',
        '午': '酉',
        '未': '申',
        '申': '未',
        '酉': '午',
        '戌': '巳',
        '亥': '辰'},
 '天喜': {'子': '酉',
        '丑': '申',
        '寅': '未',
        '卯': '午',
        '辰': '巳',
        '巳': '辰',
        '午': '卯',
        '未': '寅',
        '申': '丑',
        '酉': '子',
        '戌': '亥',
        '亥': '戌'},
 '金舆': {'甲': '辰', '乙': '巳', '丙': '未', '丁': '申', '戊': '未', '己': '申', '庚': '戌', '辛': '亥', '壬': '丑', '癸': '寅'},
 '羊刃': {'甲': '卯', '乙': '寅', '丙': '午', '丁': '巳', '戊': '午', '己': '巳', '庚': '酉', '辛': '申', '壬': '子', '癸': '亥'},
 '飞刃': {'甲': '酉', '乙': '申', '丙': '子', '丁': '亥', '戊': '子', '己': '亥', '庚': '卯', '辛': '寅', '壬': '午', '癸': '巳'},
 '劫煞': {'申子辰': '巳', '寅午戌': '亥', '巳酉丑': '寅', '亥卯未': '申'},
 '灾煞': {'申子辰': '午', '寅午戌': '子', '巳酉丑': '卯', '亥卯未': '酉'},
 '桃花咸池': {'申子辰': '酉', '寅午戌': '卯', '巳酉丑': '午', '亥卯未': '子'},
 '红艳煞': {'甲': '午', '乙': '申', '丙': '寅', '丁': '未', '戊': '辰', '己': '辰', '庚': '戌', '辛': '酉', '壬': '子', '癸': '申'},
 '孤辰': {'亥子丑': '寅', '寅卯辰': '巳', '巳午未': '申', '申酉戌': '亥'},
 '寡宿': {'亥子丑': '戌', '寅卯辰': '丑', '巳午未': '辰', '申酉戌': '未'},
 '驿马': {'申子辰': '寅', '寅午戌': '申', '巳酉丑': '亥', '亥卯未': '巳'},
 '华盖': {'申子辰': '辰', '寅午戌': '戌', '巳酉丑': '丑', '亥卯未': '未'},
 '将星': {'申子辰': '子', '寅午戌': '午', '巳酉丑': '酉', '亥卯未': '卯'},
 '亡神': {'申子辰': '亥', '寅午戌': '巳', '巳酉丑': '申', '亥卯未': '寅'}}


def stem_table(values):
    return dict(zip(GAN, values))


TABLES.update({
    '禄神': stem_table('寅卯巳午巳午申酉亥子'),
    # 通行福星歌；与 vendor 的食神五鼠遁推导表有意不同。
    '福星贵人': stem_table(('寅子','丑卯','子寅','亥','申','未','午','巳','辰','卯')),
    '血刃': dict(zip('寅卯辰巳午未申酉戌亥子丑', '丑未寅申卯酉辰戌巳亥午子')),
    '流霞': stem_table('酉戌未申巳午辰寅亥卯'),
})
DAY_SETS = {
    '魁罡': '庚辰 庚戌 壬辰 戊戌'.split(),
    '阴差阳错': '丙子 丁丑 戊寅 辛卯 壬辰 癸巳 丙午 丁未 戊申 辛酉 壬戌 癸亥'.split(),
    '十恶大败': '甲辰 乙巳 丙申 丁亥 戊戌 己丑 庚辰 辛巳 壬申 癸亥'.split(),
    '孤鸾': '甲寅 乙巳 丁巳 戊申 辛亥 壬子 丙午 戊午'.split(),
    '十灵': '甲辰 乙亥 丙辰 丁酉 戊午 庚戌 庚寅 辛亥 壬寅 癸未'.split(),
    '六秀': '丙午 丁未 戊子 戊午 己丑 己未'.split(),
}
ALIASES = {'文昌贵人': '文昌', '国印贵人': '国印', '天厨贵人': '天厨',
           '红艳煞': '红艳', '桃花咸池': '桃花(咸池)'}
VARIANTS = {
    '太极贵人': ['默认日干查四支；渊海c026:p0005明确以生年为主，另有年日干兼查法'],
    '月德贵人': ['默认查四柱天干；渊海c028:p0007另有日上见之限定'],
    '天乙贵人': ['默认甲戊庚丑未、辛寅午；另一口诀甲戊并牛羊、庚辛逢虎马（庚改寅午）', '另有年干兼查、昼夜贵人分查法'],
    '羊刃': ['默认阴干逆行帝旺：乙寅丁己巳辛申癸亥', '另有阴干不论刃、阴干冠带（乙辰丁己未辛戌癸丑）法'],
    '飞刃': ['默认冲本表羊刃；随阴干羊刃派别而变'],
    '学堂': ['默认日干长生支简表；古法另以年命纳音长生及真学堂干支查，不可混称'],
    '词馆': ['默认日干临官支简表；古法另以年命纳音临官及真词馆干支查'],
    '福星贵人': ['默认通行歌甲丙寅子、乙丑卯；vendor 使用食神五鼠遁推导表，非本表',
               '渊海c032有丙戌、丁酉及癸乙牛卯等异文，当前不据其重排通行表'],
    '三奇贵人': ['默认四干集合齐全，不限顺序；严格派要求顺布连续、得时得地，命中不等于成格'],
    '天罗地网': ['默认男查戌亥、女查辰巳单支，与vendor兼容', '古法另限年命纳音火遇戌亥、水土遇辰巳；另有须两支齐见法'],
    '孤鸾': ['默认通行八日简表；另有剔除甲寅、须日时并见及性别限定法'],
    '六秀': ['默认丙午丁未戊子戊午己丑己未六日；另有按月令及纳音论秀法'],
    '金神': ['默认仅乙丑己巳癸酉时柱；另有日柱法，成格尚须火制等条件'],
    '童子': ['仅采用春秋寅子、冬夏卯未辰及年命纳音支诀，查日时；民间表与真/假童子分法不一，非身份或疾病判断'],
    '元辰(大耗)': ['默认阳男阴女冲前一位、阴男阳女冲后一位；vendor大耗固定冲后一位'],
    '勾绞': ['默认阳男阴女前勾后三，阴男阳女反之；另有不分性别固定前勾后绞法'],
    '德秀贵人': ['默认月令组见德干且见秀干（可为同柱）；严格派另要求合化、不受克破'],
}
for _name in ('桃花(咸池)', '驿马', '华盖', '将星', '劫煞', '亡神', '灾煞'):
    VARIANTS[_name] = ['默认年支查四支；另有日支查、年日支兼查；旧shensha年日兼查的三项保持不变']

RULES_EXT = {
    'version': '1.0.0', 'scope': '查表命中，不作吉凶断语或格局成立判断',
    'sanhe_basis': 'year_branch', 'stem_basis': 'day_stem',
    'tianyi': '甲戊庚丑未，辛寅午', 'yin_blade': '逆行帝旺',
    'sources': '通行口诀为未完成古籍校勘；定位段落仅支持note所述部分',
    'gender_dependent': '性别未知时不查元辰、勾绞、天罗地网',
}

# These pointers were checked with offline corpus search/get. Do not treat a
# related discussion as proof of every simplified lookup condition.
SOURCES = {
    '天乙贵人': ('yuanhai:c024:p0003', '口诀续p0004作庚辛马虎；本表庚用丑未、辛用寅午，与该异本不同'),
    '太极贵人': ('yuanhai:c026:p0003', '口诀续p0004；p0005主生年，本表日干为vendor简法'),
    '三奇贵人': ('yuanhai:c027:p0003', '三组三干；集合不限序仅为候选，不判断成格'),
    '月德贵人': ('yuanhai:c028:p0003', '四组三合续p0004–p0006；p0007日上见之，本表查四干'),
    '月德合': ('yuanhai:c029:p0003', '四组三合对应五合干'),
    '福星贵人': ('yuanhai:c032:p0003', '续p0004有丙戌、丁酉及癸乙牛卯异文；当前选通行简表，不称逐字复现'),
    '禄神': ('yuanhai:c034:p0003', '十干禄支；本表选日干查四支'),
    '学堂': ('yuanhai:c038:p0003', '该段为纳音五行及正学堂，非本表日干长生简法；仅定位异说'),
    '金舆': ('yuanhai:c040:p0003', '十干禄前第二位；本表日干查四支'),
    '空亡(旬空)': ('yuanhai:c047:p0002', '六旬空支续p0003–p0007'),
    '羊刃': ('yuanhai:c054:p0004', '续p0005–p0013阴干用禄前支，与本表逆帝旺不同；c088:p0003另有阴干无刃法'),
    '飞刃': ('yuanhai:c054:p0003', '羊刃对宫即飞刃；本表阴干羊刃取逆帝旺，故与后续阴干示例不同'),
    '金神': ('yuanhai:c096:p0003', '三时柱原文；仅记录时柱命中，不判断火制等成格条件'),
    '天德贵人': ('yuanhai:c030:p0003', '十二月天德口诀；以节月对应月支'),
    '天赦': ('yuanhai:c036:p0003', '四季日柱原文，季节按节月'),
    '十恶大败': ('yuanhai:c050:p0003', '语料作乙丑；本表取通行己丑，保留异文，不改原文'),
    '天罗地网': ('yuanhai:c053:p0003', '原文有纳音限定；本表仅为vendor兼容简法，非完整原法'),
    '驿马': ('sanming:c003:p0004', '四局马支；木局在己异文，卷六p0109作亥卯未马在巳；年支独查属简法'),
    '华盖': ('sanming:c002:p0039', '三合底处得库；年支独查属简法'),
    '将星': ('sanming:c002:p0039', '三合中位；年支独查属简法'),
}


def detect(pillars, gender=None):
    """Return one item per trigger, with explicit pillar and source evidence."""
    gz = {k: p['ganzhi'] for k, p in pillars.items()}
    stems = {k: v[0] for k, v in gz.items()}
    branches = {k: v[1] for k, v in gz.items()}
    day, year, month = gz['day'], gz['year'], branches['month']
    hits = []

    def emit(name, positions, basis, rule, hit=None):
        if not positions:
            return
        loc = SOURCES.get(name)
        source = {'book': loc[0].split(':')[0] if loc else '通行口诀',
                  'note': loc[1] if loc else '选定通行简表；尚未定位完整起法原文，未作影像校勘'}
        if loc:
            source.update(chapter=loc[0].split(':')[1], passage_id=loc[0])
        hits.append(dict(name=name, pillars=list(positions), basis=basis, rule=rule,
                         source=source, school_variants=list(VARIANTS.get(name, [])),
                         hit=hit, interpretation_status='trigger_only'))

    def scan(name, target, basis, rule, values=None):
        values = branches if values is None else values
        for k, value in values.items():
            if value in target:
                emit(name, [k], basis, rule, value)

    year_group = next(g for g in GROUPS if year[1] in g)
    season = next(g for g in SEASONS if year[1] in g)
    month_group = next(g for g in GROUPS if month in g)
    for raw_name, table in TABLES.items():
        name = ALIASES.get(raw_name, raw_name)
        keys = set(table)
        if keys <= set(GAN):
            target = table[day[0]]
            basis = '以日干查地支'
        elif keys <= set(GROUPS):
            is_month = raw_name in ('月德贵人', '月德合')
            target = table[month_group if is_month else year_group]
            basis = '以月支三合查天干' if is_month else '以年支三合查地支'
        elif keys <= set(SEASONS):
            target = table[season]
            basis = '以年支方局查地支'
        elif any(k.endswith('月') for k in keys):
            target = table[month+'月']
            basis = '以月支查四柱干支'
        elif raw_name == '血刃':
            target = table[month]
            basis = '以月支查地支'
        else:
            target = table[year[1]]
            basis = '以年支查地支'
        rule = '；'.join(k+'→'+''.join(v) for k, v in table.items())
        if raw_name in ('月德贵人', '月德合'):
            scan(name, target, basis, rule, stems)
        elif raw_name in ('天德贵人', '天德合'):
            scan(name, target, basis, rule, stems)
            scan(name, target, basis, rule)
        else:
            scan(name, target, basis, rule)

    for name, days in DAY_SETS.items():
        if day in days:
            emit(name, ['day'], '以日柱查', '、'.join(days), day)
    scan('空亡(旬空)', LunarUtil.getXunKong(day), '以日柱旬空查地支',
         '甲子戌亥、甲戌申酉、甲申午未、甲午辰巳、甲辰寅卯、甲寅子丑')
    scan('天医', ZHI[(ZHI.index(month)-1) % 12], '以月支查地支', '生月前一支为天医')
    for name, offset in (('丧门', 2), ('吊客', -2), ('披麻', -3)):
        scan(name, ZHI[(ZHI.index(year[1])+offset) % 12], '以年支查地支',
             f'子丑寅卯顺序，年支偏移{offset:+d}支')
    if gender in ('male', 'female'):
        forward = (GAN.index(year[0]) % 2 == 0) == (gender == 'male')
        yi = ZHI.index(year[1])
        scan('元辰(大耗)', ZHI[(yi+(7 if forward else 5)) % 12],
             '以年干阴阳、性别、年支查地支', '阳男阴女冲前一位，阴男阳女冲后一位')
        for label, offset in (('勾', 3 if forward else -3), ('绞', -3 if forward else 3)):
            scan('勾绞', ZHI[(yi+offset) % 12], '以年干阴阳、性别、年支查地支',
                 '阳男阴女前三为勾、后三为绞；阴男阳女反之；本次'+label)
        scan('天罗地网', '戌亥' if gender == 'male' else '辰巳',
             '以性别查四柱地支（简法）', '男戌亥为天罗，女辰巳为地网')
    season_index = next(i for i, g in enumerate(('寅卯辰','巳午未','申酉戌','亥子丑')) if month in g)
    if day == ('戊寅','甲午','戊申','甲子')[season_index]:
        emit('天赦', ['day'], '以节月季节查日柱', '春戊寅、夏甲午、秋戊申、冬甲子', day)
    for triple in ('甲戊庚', '乙丙丁', '壬癸辛'):
        if set(triple) <= set(stems.values()):
            emit('三奇贵人', [k for k, s in stems.items() if s in triple],
                 '以四柱天干集合查三奇（不限序）', '天上甲戊庚，地下乙丙丁，人中壬癸辛', triple)
    if gz['hour'] in ('乙丑', '己巳', '癸酉'):
        emit('金神', ['hour'], '以时柱查', '乙丑、己巳、癸酉时', gz['hour'])
    de, xiu = {'寅午戌': ('丙丁','戊癸'), '申子辰': ('壬癸戊己','丙辛甲己'),
               '巳酉丑': ('庚辛','乙庚'), '亥卯未': ('甲乙','丁壬')}[month_group]
    if any(s in de for s in stems.values()) and any(s in xiu for s in stems.values()):
        emit('德秀贵人', [k for k, s in stems.items() if s in de+xiu],
             '以月支三合查德干与秀干兼见', f'{month_group}：德{de}，秀{xiu}')
    # 民间童子口诀的两种条件分别留痕，不能作为宗教身份断定。
    target = '寅子' if season_index in (0, 2) else '卯未辰'
    dayhour = {k: branches[k] for k in ('day','hour')}
    scan('童子', target, '以节月季节查日时支', '春秋寅子贵，冬夏卯未辰', dayhour)
    element = LunarUtil.NAYIN[year][-1]
    scan('童子', {'金':'午卯','木':'午卯','水':'酉戌','火':'酉戌','土':'辰巳'}[element],
         '以年柱纳音查日时支', '金木午卯合，水火酉戌多，土命逢辰巳', dayhour)
    return hits
