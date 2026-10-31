import fs from 'node:fs';
import { astro } from 'iztro';
import { horoscope } from './horoscope';
import { generateChart, setBrightnessSchool, resolveEffectiveLunarDate } from './renhuai/algorithm';
const branches = '子丑寅卯辰巳午未申酉戌亥';
// Renhuai installs brightness overrides on import. Keep raw iztro brightness native.
const renhuaiBrightness = {...astro.getConfig().brightness};

function chart(r: any) {
  const date = new Date(`${r.date}T00:00:00Z`);
  const timeIndex = r.hour === 23 ? 12 : Math.floor((r.hour + 1) / 2);
  // bySolar forward late-zi performs the date shift internally.
  astro.config({yearDivide:'normal', horoscopeDivide:'normal', dayDivide:'forward'});
  const brightness = astro.getConfig().brightness;
  for (const key of Object.keys(brightness)) delete (brightness as any)[key];
  let raw: any;
  if (r.leapMonth === 'split') {
    raw = astro.bySolar(r.date, timeIndex, r.gender === 'male' ? '男' : '女', true, 'zh-CN');
  } else {
    // Resolve on the actual chart day; byLunar receives early zi after explicit shift.
    const ld = new Date(date);
    if (timeIndex === 12) ld.setUTCDate(ld.getUTCDate()+1);
    const e = resolveEffectiveLunarDate(ld.getUTCFullYear(), ld.getUTCMonth()+1, ld.getUTCDate(), r.leapMonth);
    raw = astro.byLunar(`${e.lunarYear}-${e.lunarMonth}-${e.lunarDay}`, timeIndex % 12,
      r.gender === 'male' ? '男' : '女', e.isLeapMonth, false, 'zh-CN');
  }
  if (r.command === 'horoscope') return {...horoscope(raw, r.targetDate, r.targetHour), timeIndex};
  if (timeIndex === 12) date.setUTCDate(date.getUTCDate()+1);
  astro.config({brightness:renhuaiBrightness});
  setBrightnessSchool(r.school);
  const renhuai = generateChart({year:date.getUTCFullYear(),month:date.getUTCMonth()+1,day:date.getUTCDate(),
    hour:timeIndex%12,gender:r.gender, origInput:{year:Number(r.date.slice(0,4)),month:Number(r.date.slice(5,7)),
    day:Number(r.date.slice(8,10)),clockHour:r.hour,clockMinute:r.minute}}, {leapMonth:r.leapMonth});
  const iztro = JSON.parse(JSON.stringify(raw));
  // Remove functional backreferences, retaining the serializable raw astrolabe.
  const normalized = raw.palaces.map((p:any)=>({name:p.name, heavenlyStem:p.heavenlyStem,
    earthlyBranch:p.earthlyBranch, isBodyPalace:p.isBodyPalace,
    majorStars:p.majorStars, minorStars:p.minorStars, adjectiveStars:p.adjectiveStars, decadal:p.decadal}));
  iztro.palaces = normalized;
  const positions = Object.fromEntries(raw.palaces.flatMap((p:any)=>p.majorStars
    .filter((s:any)=>s.type === 'major' || s.type === '主星')
    .map((s:any)=>[s.name,p.earthlyBranch])));
  // iztro majorStars also contains lucky stars; only compare Renhuai's 14 major stars.
  const diffs:any[]=[];
  for(const p of renhuai.palaces) for(const s of p.stars.filter(s=>s.type==='major')) {
    const actual=positions[s.name];
    if(actual!==branches[p.branch]) diffs.push({star:s.name,iztro:actual ?? null,renhuai:branches[p.branch]});
  }
  const sihua = raw.palaces.flatMap((p:any)=>[...p.majorStars,...p.minorStars,...p.adjectiveStars]
    .filter((s:any)=>s.mutagen).map((s:any)=>({star:s.name,transformation:s.mutagen,branch:p.earthlyBranch})));
  let annual:any = null;
  if(r.year) {
    const h=raw.horoscope(`${r.year}-7-1`).yearly;
    annual={year:r.year, referenceDate:`${r.year}-07-01`, ...h,
      mingPalace:raw.palaces[h.index].earthlyBranch};
  }
  return {timeIndex, iztro:{...iztro,engine:{name:'iztro',version:'2.6.1',rules:{yearDivide:'normal',dayDivide:'forward'}},warnings:[]},
    renhuai:{...renhuai,patterns:detectPatterns(renhuai),engine:{name:'renhuai',version:'495b79e',rules:{brightness:r.school,leapMonth:r.leapMonth}},warnings:[]},
    daxian:raw.palaces.map((p:any)=>({palace:p.name,branch:p.earthlyBranch,...p.decadal})), annual,sihua,
    comparison:{agree:diffs.length===0,diffs}};
}
import { detectPatterns } from './renhuai/patterns';
try {
  const req=JSON.parse(process.argv[2] || fs.readFileSync(0,'utf8'));
  console.log(JSON.stringify({results:req.candidates.map(chart)}));
} catch(e) { console.log(JSON.stringify({error:String(e)})); process.exitCode=1; }
