import json
import subprocess
from datetime import datetime
from eastern.qimen import chart

# Frozen from chinese-fortune commit 81a980a5707505468a10f596f1f19c9088457a9e:
# qimen_cast.py --date 2026-05-16 --time 14:30 --target-timezone Asia/Shanghai
# --plate-method rotating-compat (installed lunar-python preloaded).
REFERENCE = {'ganzhi': {'year': '丙午', 'month': '癸巳', 'day': '庚'+'寅', 'hour': '癸未'}, 'jieqi': '立夏', 'ju_type': '阳遁', 'ju_number': 7, 'san_yuan': '下元', 'xun_head': '甲戌', 'zhi_fu_star': '天任', 'zhi_fu_palace': 3, 'zhi_shi_men': '生门', 'zhi_shi_palace': 8, 'palaces': [{'index': 1, 'palace': '坎', 'direction': '北', 'wuxing': '水', 'earth_yi_qi': '辛', 'heaven_yi_qi': '乙', 'men': '休门', 'star': '天心', 'shen': '九地', 'notes': ''}, {'index': 2, 'palace': '坤', 'direction': '西南', 'wuxing': '土', 'earth_yi_qi': '壬', 'heaven_yi_qi': '戊', 'men': '死门', 'star': '天英', 'shen': '六合', 'notes': ''}, {'index': 3, 'palace': '震', 'direction': '东', 'wuxing': '木', 'earth_yi_qi': '癸', 'heaven_yi_qi': '己', 'men': '伤门', 'star': '天任', 'shen': '值符', 'notes': ''}, {'index': 4, 'palace': '巽', 'direction': '东南', 'wuxing': '木', 'earth_yi_qi': '丁', 'heaven_yi_qi': '庚', 'men': '杜门', 'star': '天冲', 'shen': '螣蛇', 'notes': ''}, {'index': 5, 'palace': '中', 'direction': '中央', 'wuxing': '土', 'earth_yi_qi': '丙', 'heaven_yi_qi': '辛', 'men': None, 'star': '天禽', 'shen': None, 'notes': '中宫；寄宫须按所选方法另核，不能固定称天芮天禽同宫'}, {'index': 6, 'palace': '乾', 'direction': '西北', 'wuxing': '金', 'earth_yi_qi': '乙', 'heaven_yi_qi': '壬', 'men': '开门', 'star': '天柱', 'shen': '玄武', 'notes': ''}, {'index': 7, 'palace': '兑', 'direction': '西', 'wuxing': '金', 'earth_yi_qi': '戊', 'heaven_yi_qi': '癸', 'men': '惊门', 'star': '天芮', 'shen': '白虎', 'notes': ''}, {'index': 8, 'palace': '艮', 'direction': '东北', 'wuxing': '土', 'earth_yi_qi': '己', 'heaven_yi_qi': '丁', 'men': '生门', 'star': '天蓬', 'shen': '九天', 'notes': ''}, {'index': 9, 'palace': '离', 'direction': '南', 'wuxing': '火', 'earth_yi_qi': '庚', 'heaven_yi_qi': '丙', 'men': '景门', 'star': '天辅', 'shen': '太阴', 'notes': ''}]}


def test_qimen_frozen_rotating_reference():
    r = chart(datetime.fromisoformat('2026-05-16T14:30:00+08:00'))
    assert {k:r[k] for k in REFERENCE} == REFERENCE
    assert r['空亡'] == ['申','酉'] and r['马星'] == '巳'


def test_qimen_winter_solstice_is_yang():
    r = chart(datetime.fromisoformat('2026-12-23T12:00:00+08:00'))
    assert r['jieqi'] == '冬至' and r['ju_type'] == '阳遁'


def test_qimen_cli_and_approx_range():
    p = subprocess.run(['bin/prophet','qimen','chart','--datetime','2026-05-16T14:30'],capture_output=True,text=True)
    assert p.returncode == 0 and json.loads(p.stdout)['palaces'] == REFERENCE['palaces']
    p = subprocess.run(['bin/prophet','qimen','chart','--person','S02'],capture_output=True,text=True)
    r = json.loads(p.stdout)
    assert p.returncode == 0 and len(r['branches']) == 2 and 'invariants' in r


def test_qimen_solstice_instant_and_timezone():
    from datetime import timedelta
    from lunar_python import Solar
    from zoneinfo import ZoneInfo
    term = Solar.fromYmdHms(2026,12,23,12,0,0).getLunar().getPrevJieQi().getSolar()
    boundary = datetime(term.getYear(),term.getMonth(),term.getDay(),term.getHour(),term.getMinute(),term.getSecond(),tzinfo=ZoneInfo('Asia/Shanghai'))
    assert chart(boundary-timedelta(seconds=1))['ju_type'] == '阴遁'
    assert chart(boundary+timedelta(seconds=1))['ju_type'] == '阳遁'
    p = subprocess.run(['bin/prophet','qimen','chart','--datetime','2026-05-16T06:30:00Z','--tz','Asia/Shanghai'],capture_output=True,text=True)
    assert p.returncode == 0 and json.loads(p.stdout)['palaces'] == REFERENCE['palaces']
