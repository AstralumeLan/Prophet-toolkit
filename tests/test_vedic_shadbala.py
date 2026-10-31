"""Published worked references: B.V. Raman, Graha and Bhava Balas.

Reference text is vendor/refs/raman_graha_bhava_balas.txt, never imported as code.
"""
from vedic._shadbala import calculate_shadbala, NAISARGIKA, REQUIRED, aspect_value


def standard():
    # Arts.5–7, 99, 101–105. Decimal degrees, not degrees.minutes.
    values = [(180,53,55), (311,17,19), (229,30,34), (181,31,34),
              (84,0,49), (171,9,56), (124,22,41)]
    names = tuple(NAISARGIKA)
    longs = {p: d+m/60+s/3600 for p,(d,m,s) in zip(names,values)}
    means = dict(zip(('Sun','Mars','Mercury','Jupiter','Venus','Saturn'),
                     (181.2275,266.34,181.2275,66.91,181.2275,111.23)))
    seeghra = dict(zip(('Mars','Mercury','Jupiter','Venus','Saturn'),
                       (181.23,174.49,181.23,158.35,181.23)))
    return calculate_shadbala(longs, {p: 0 for p in names}, 298+27/60,216+30/60,
        ayanamsa=21+16/60, natha_hours=(5+50/60)*.4,
        hours_since_sunrise=(20+32/60)*.4, day_hours=(29+20/60)*.4,
        weekday_lord='Mercury', year_lord='Saturn', month_lord='Mercury',
        mean_longitudes=means, seeghrochcha=seeghra, mercury_benefic=False,
        # Ex.32–33 rounded intermediate krantis; Moon's art.32 longitude
        # disagrees with art.6 by one degree, so use the printed intermediate.
        krantis=dict(zip(names,(-8.75,-10.75,-22.45,-9,23.5,-4.96,13))))


def test_vedic_shadbala_raman_sthana():
    # Examples 3, 9–13. Book has several OCR/printing errors in table sums.
    g = standard()['grahas']
    for p,v in zip(g,(198,126.50,172.06,279.50,157.58,178.20,177.30)):
        # Mars ex.3 prints 37.06 for 111:30:34 / 3 (=37.1698).
        assert abs(g[p]['sthana']-v)<.12, (p,g[p]['sthana'],v)
    assert abs(g['Sun']['sthana_components']['uchcha']-3)<.04
    assert g['Sun']['sthana_components']['saptavargaja']==90
    assert g['Sun']['sthana_components']['ojayugmarasyamsa']==30
    assert g['Sun']['sthana_components']['kendra']==60
    assert [g[p]['sthana_components']['saptavargaja'] for p in g] == [90,48.75,90,135,71.25,116.25,97.5]


def test_vedic_shadbala_raman_components_and_totals():
    # Examples 15, 35, 51, 55–56. Dig uses art.7 MC=216:30 rather than
    # ex.14's inconsistent 216:36. Mars ex.56 Kala=33.06 vs ex.35=30.06.
    g = standard()['grahas']
    expected = {
        'dig': (48.10,31.56,55.70,21.09,11.50,15.15,58.02),
        'kala': (102.98,202.04,30.06,192.79,211.18,115.53,116.97),
        'chesta': (0,0,22.23,2.30,35.26,5.95,21.14),
        'drik': (15.86,-21.73,.95,15.64,-16.04,18.47,7.21),
        'total_rupas': (7.08,6.50,4.97,8.85,7.23,6.27,6.49)}
    for key, values in expected.items():
        for p,v in zip(g,values):
            tolerance = .15 if key=='total_rupas' else .10
            assert abs(g[p][key]-v)<tolerance, (p,key,g[p][key],v)
    assert g['Sun']['chesta']==0 and 22<g['Sun']['phala_chesta']<23
    assert abs(g['Moon']['phala_chesta']-43.46)<.01
    assert g['Mars']['strong'] is False
    assert all(g[p]['required_rupas']==REQUIRED[p] for p in g)


def test_vedic_shadbala_naisargika_and_aspects():
    # Art.108 constants (Raman's printed decimals, not rounded multiples of 60/7).
    assert list(NAISARGIKA.values())==[60,51.43,17.14,25.70,34.28,42.85,8.57]
    # Arts.114–115: full ordinary opposition and special aspects.
    assert aspect_value(180,'Sun')==60
    assert aspect_value(90,'Mars')==60
    assert aspect_value(120,'Jupiter')==60
    assert aspect_value(60,'Saturn')==60
    assert aspect_value(0,'Jupiter')==0


def test_vedic_shadbala_cli_s01_and_approx():
    from tests.test_vedic import cli
    a=cli('shadbala','--person','S01','--levels','1')
    g=a['branches'][0]['chart']['shadbala']['grahas']
    assert len(g)==7 and all(r['total_rupas']>0 for r in g.values())
    b=cli('chart','--person','S01','--shadbala','--levels','1')
    assert b['branches'][0]['chart']['shadbala']['grahas']==g
    c=cli('shadbala','--person','S02','--levels','1')
    assert len(c['branches'])==5 and 'invariants' in c
