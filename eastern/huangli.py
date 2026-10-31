"""黄历日查询，历书字段来自安装的 lunar-python。"""
from __future__ import annotations
from datetime import datetime
from . import _iching as ic

ENGINE = ic.engine('eastern.huangli', calendar='lunar-python', month='solar-term month',
                   yi_ji='lunar-python default sect=1', day_boundary='midnight', hours='早子、丑至亥、夜子')


def day(date):
    dt = datetime.fromisoformat(date+'T12:00:00')
    lunar = ic.lunar_at(dt)
    hours = []
    for label, hour, span in [('早子', 0, '00:00-01:00')] + [
            (b, h, f'{h:02d}:00-{h+2:02d}:00') for b, h in zip('丑寅卯辰巳午未申酉戌亥', range(1, 23, 2))] + [('夜子', 23, '23:00-24:00')]:
        l = ic.lunar_at(dt.replace(hour=hour, minute=30))
        hours.append({'时辰': label, '时间范围': span, '干支': l.getTimeInGanZhi(),
                      '值神': l.getTimeTianShen(), '黄黑道': l.getTimeTianShenType(),
                      '吉凶': l.getTimeTianShenLuck(), '宜': l.getTimeYi(), '忌': l.getTimeJi()})
    return {'engine': ENGINE, 'warnings': [], 'date': date,
            '农历': lunar.toString(), '干支': {'年': lunar.getYearInGanZhi(),
            '月': lunar.getMonthInGanZhi(), '日': lunar.getDayInGanZhi()},
            '宜': lunar.getDayYi(), '忌': lunar.getDayJi(),
            '冲煞': {'冲': lunar.getDayChongDesc(), '煞': lunar.getDaySha()},
            '值神': {'名称': lunar.getDayTianShen(), '黄黑道': lunar.getDayTianShenType(), '吉凶': lunar.getDayTianShenLuck()},
            '十二建除': lunar.getZhiXing(),
            '二十八宿': {'宿': lunar.getXiu(), '政': lunar.getZheng(), '动物': lunar.getAnimal(), '吉凶': lunar.getXiuLuck()},
            '彭祖百忌': [lunar.getPengZuGan(), lunar.getPengZuZhi()],
            '吉神': lunar.getDayJiShen(), '凶煞': lunar.getDayXiongSha(), '时辰': hours}


def register(subparsers):
    p = subparsers.add_parser('huangli', help='黄历宜忌')
    sp = p.add_subparsers(dest='method', required=True)
    q = ic.add_event_args(sp.add_parser('day'))
    q.set_defaults(func=lambda a: ic.branch(a, lambda dt: day(dt.date().isoformat())))
