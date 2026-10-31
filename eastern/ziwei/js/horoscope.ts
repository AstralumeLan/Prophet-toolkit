/** Adapt iztro 2.6.1 HoroscopeItem arrays (indices are natal palace indices). */
export function horoscope(raw: any, date: string, hour?: number) {
  const timeIndex = hour == null ? 0 : hour === 23 ? 12 : Math.floor((hour + 1) / 2);
  const h = raw.horoscope(date, timeIndex);
  const flows: any = {};
  for (const key of ['decadal', 'age', 'yearly', 'monthly', 'daily', ...(hour == null ? [] : ['hourly'])]) {
    const scope = h[key];
    const valid = scope.index >= 0 && scope.index < 12;
    const locate = (star: string) => raw.palaces.find((p: any) =>
      [...p.majorStars, ...p.minorStars, ...p.adjectiveStars].some((s: any) => s.name === star));
    flows[key] = {
      name: scope.name, index: scope.index,
      heavenlyStem: valid ? scope.heavenlyStem : null,
      earthlyBranch: valid ? scope.earthlyBranch : null,
      palace_names: valid ? Object.fromEntries(scope.palaceNames.map((name: string, i: number) =>
        [name, {natal_palace: raw.palaces[i].name, branch: raw.palaces[i].earthlyBranch}])) : {},
      mutagen: valid ? scope.mutagen.map((star: string, i: number) => {
        const p = locate(star);
        return {transformation: ['化禄', '化权', '化科', '化忌'][i], star,
          natal_palace: p?.name ?? null, branch: p?.earthlyBranch ?? null,
          ...(!p ? {note: '四化星未在本命主星、辅星或杂曜中找到'} : {})};
      }) : [],
      ...(!valid ? {note: '目标年龄不在 iztro 支持的运限范围内'} : {}),
    };
    const out = flows[key];
    if (scope.nominalAge != null) out.nominalAge = scope.nominalAge;
    if (key === 'decadal') {
      out.childhood = scope.name === '童限';
      out.age_range = valid && !out.childhood ? raw.palaces[scope.index].decadal.range : null;
    }
    if (scope.stars) out.stars = scope.stars.map((stars: any[], i: number) => ({
      natal_palace: raw.palaces[i].name, branch: raw.palaces[i].earthlyBranch, stars}));
    if (scope.yearlyDecStar) out.yearlyDecStar = scope.yearlyDecStar;
  }
  return {target: {date, hour: hour ?? null, ...(hour == null ? {} : {timeIndex})},
    solarDate: h.solarDate, lunarDate: h.lunarDate, flows};
}
