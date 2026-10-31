// MIT excerpts from Renhuai123/ziwei-doushu; see LICENSE and NOTICE.md.
/**
 * 排盘流派配置 — 9 类排盘流派开关 + 默认值 + 持久化
 *
 * 数据源：按通行口径整理（详见 docs/school-alignment.md）
 *
 * 用户在 chart 页设置面板切换，立即重新排盘
 */

import type { BrightnessSchool } from './school-data';

// ─── 9 类流派配置 ───────────────────────────────────────────────────────

/** 1. 14 主星亮度表 */
export type BrightnessSchoolOption = 'default' | BrightnessSchool;

/** 2. 庚年四化（5 种变体）*/
export type GengYearSihua =
  | 'GYWYT'   // 阳武阴同（主流默认口径，与 iztro 一致）
  | 'GYWTY'   // 阳武同阴（科忌互换说）
  | 'GYWFT'   // 阳武府同
  | 'GYWFX'   // 阳武府相
  | 'GYWTX';  // 阳武同相

/** 3. 安天马 */
export type TianmaSchool = 'year-branch' | 'month-branch';

/** 4. 安天空 */
export type TiankongSchool = 'normal' | 'shun-jia-shi';

/** 5. 截空旬空 */
export type JiekongSchool = 'single' | 'double' | 'zhanyan';

/** 6. 安魁钺 */
export type KuiyueSchool = 'qs1' | 'qs2' | 'zhong-yiming' | 'network';

/** 7. 安天使天伤 */
export type TianshiTianshangSchool = 'normal' | 'zhongzhou';

/** 8. 安长生十二神 */
export type ChangshengSchool = 'yin-yang-shun-ni' | 'shui-tu' | 'huo-tu';

/** 9. 晚子时处理 */
export type LateZishi =
  | 'next-day'           // 视为次日（主流默认口径 + 我们当前）
  | 'current-day'        // 视为当日（倪师派）
  | 'all-current'        // 日柱当日时柱当日（八字）
  | 'day-cur-time-next'; // 日柱当日时柱次日（八字）

/** 10. 闰月处理（用户反馈：倪师派要求闰月归下月）*/
export type LeapMonth =
  | 'split'         // 分半（前 15 天归上月，后 15 天归下月）— ★我们默认 = 主流排盘默认口径「月中分界」（2026-09-05 150 组金标准盘对照：9 张闰月后半月盘唯此口径逐星全同）
  | 'next-month'    // 整月归下月（倪师派：闰四月当五月）
  | 'prev-month'    // 整月当本月普通月（闰四月当四月）— 可选口径「视为本月」；早先 2.6 万盘验证针对的是另一套参照引擎，与金标准盘默认口径不一致
  | 'origin-month'; // 不调整（闰四月仍标闰月，iztro fixLeap=false）


export const DEFAULT_LEAP_MONTH: LeapMonth = 'split';
