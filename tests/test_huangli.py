import json
import subprocess
from lunar_python import Solar
from eastern.huangli import day


def test_huangli_public_calendar_reference():
    # lunar-python Solar(2000-01-01): 己卯年 丙子月 戊午日。
    # Public implementation: https://github.com/6tail/lunar-python
    r = day('2000-01-01')
    assert r['干支'] == {'年':'己卯','月':'丙子','日':'戊午'}


def test_huangli_yi_ji_and_hours():
    l = Solar.fromYmdHms(2026,10,31,12,0,0).getLunar()
    r = day('2026-10-31')
    assert r['宜'] == l.getDayYi() and r['忌'] == l.getDayJi()
    assert len(r['时辰']) == 13
    for row, hour in zip(r['时辰'], [0,*range(1,23,2),23]):
        h = Solar.fromYmdHms(2026,10,31,hour,30,0).getLunar()
        assert row['吉凶'] == h.getTimeTianShenLuck()


def test_huangli_cli_and_approx_person():
    p = subprocess.run(['bin/prophet','huangli','day','--date','2026-10-31'],capture_output=True,text=True)
    assert p.returncode == 0 and json.loads(p.stdout)['宜'] == day('2026-10-31')['宜']
    p = subprocess.run(['bin/prophet','huangli','day','--person','S02'],capture_output=True,text=True)
    r = json.loads(p.stdout)
    assert p.returncode == 0 and len(r['branches']) == 2
    assert '干支' in r['invariants']['不随时间变化']
