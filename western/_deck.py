"""Compact original keyword paraphrases of Waite's public-domain Pictorial Key, Part III."""
MAJOR = [
('The Fool','愚人','folly, extravagance, wandering','negligence, absence, carelessness'),
('The Magician','魔术师','skill, diplomacy, will','insecurity, intrigue, weakness'),
('The High Priestess','女祭司','secrets, mystery, wisdom','conceit, superficial knowledge, passion'),
('The Empress','皇后','fruitfulness, action, initiative','vacillation, difficulty, delayed action'),
('The Emperor','皇帝','stability, protection, authority','obstruction, immaturity, lost authority'),
('The Hierophant','教皇','alliance, tradition, counsel','unconventional alliance, weakness, concord'),
('The Lovers','恋人','attraction, love, beauty','failure, contrary forces, frustrated union'),
('The Chariot','战车','triumph, resolve, conflict','quarrel, dispute, defeat'),
('Strength','力量','courage, energy, magnanimity','abuse of power, weakness, discord'),
('The Hermit','隐者','prudence, circumspection, guidance','concealment, fear, unreasonable caution'),
('Wheel of Fortune','命运之轮','fortune, success, elevation','excess, instability, interrupted fortune'),
('Justice','正义','equity, rightness, accountability','bias, severity, legal complications'),
('The Hanged Man','倒吊人','discernment, sacrifice, trials','self-interest, conformity, futile sacrifice'),
('Death','死神','ending, mortality, destruction','inertia, lethargy, stagnation'),
('Temperance','节制','moderation, management, accommodation','disunion, competing interests, imbalance'),
('The Devil','恶魔','force, bondage, fatality','weakness, pettiness, blindness'),
('The Tower','高塔','adversity, calamity, ruin','oppression, confinement, lesser upheaval'),
('The Star','星星','hope, bright prospects, renewal','arrogance, impotence, frustrated hope'),
('The Moon','月亮','hidden enemies, deception, darkness','instability, silence, lesser deception'),
('The Sun','太阳','happiness, contentment, fortunate union','diminished happiness, delayed success'),
('Judgement','审判','renewal, change, outcome','weakness, indecision, delayed judgement'),
('The World','世界','success, journey, completion','inertia, permanence, stagnation')]
MINOR = {
'Wands': [('beginning, creation, enterprise','decline, clouded joy'),('wealth, dominion, planning','surprise, trouble, fear'),('enterprise, commerce, discovery','end of adversity, suspended effort'),('harmony, refuge, prosperity','unchanged harmony, prosperity'),('competition, struggle, contest','dispute, litigation, contradiction'),('victory, good news, expectation','fear, disloyalty, delay'),('valour, negotiation, competition','anxiety, indecision, embarrassment'),('speed, movement, messages','jealousy, disputes, delay'),('strength, opposition, endurance','obstacles, adversity, delay'),('oppression, burden, responsibility','contradiction, intrigue, difficulty'),('messenger, loyalty, news','indecision, instability, bad news'),('departure, journey, change','interruption, rupture, discord'),('warmth, honour, generosity','jealousy, opposition, deceit'),('honesty, conscience, enterprise','severity, austerity, tolerance')],
'Cups': [('contentment, abundance, nourishment','instability, false heart, change'),('love, friendship, affinity','misunderstanding, false love, folly'),('merriment, fulfilment, healing','excess, conclusion, dispatch'),('weariness, aversion, dissatisfaction','novelty, new relations, instruction'),('loss, remaining hope, inheritance','return, alliance, false projects'),('memories, childhood, past joys','future, renewal, approaching events'),('imagination, fantasy, sentiment','resolve, desire, project'),('departure, decline, abandoned pursuit','joy, happiness, feasting'),('contentment, success, satisfaction','imperfection, mistakes, misplaced confidence'),('contentment, friendship, domestic joy','false harmony, indignation, violence'),('service, study, reflection','attachment, seduction, deception'),('arrival, invitation, proposition','fraud, artifice, duplicity'),('devotion, intelligence, intuition','unreliability, vice, dishonour'),('responsibility, equity, creativity','dishonesty, scandal, injustice')],
'Swords': [('triumph, force, conquest','destructive force, excess'),('balance, courage, concord','falsehood, duplicity, disloyalty'),('separation, rupture, sorrow','confusion, disorder, alienation'),('retreat, solitude, repose','precaution, economy, circumspection'),('loss, dishonour, destruction','mourning, burial, loss'),('journey, passage, expedient','declaration, confession, publicity'),('design, attempt, uncertain plan','counsel, slander, disputed advice'),('restriction, crisis, censure','disquiet, difficulty, opposition'),('desolation, disappointment, despair','suspicion, doubt, shame'),('pain, sadness, desolation','temporary advantage, passing success'),('vigilance, examination, oversight','unpreparedness, unforeseen events'),('skill, bravery, defence','imprudence, extravagance, incapacity'),('privation, separation, mourning','malice, deceit, severity'),('judgement, command, authority','cruelty, perversity, bad intention')],
'Pentacles': [('prosperity, contentment, gold','misused wealth, adverse riches'),('recreation, messages, agitation','forced enjoyment, simulated happiness'),('craft, skilled labour, renown','mediocrity, weakness, poor work'),('possessions, security, inheritance','suspense, delay, opposition'),('material trouble, destitution','disorder, discord, ruin'),('gifts, gratification, generosity','envy, desire, jealousy'),('money, business, cultivation','anxiety about money, impatience'),('work, craftsmanship, commission','vanity, empty ambition, usury'),('prudence, safety, accomplishment','deception, bad faith, void project'),('wealth, family, inheritance','loss, chance, family difficulty'),('study, reflection, practical news','prodigality, dissipation, unfavourable news'),('utility, service, responsibility','inertia, discouragement, carelessness'),('security, generosity, liberty','fear, suspicion, mistrust'),('business aptitude, intelligence, success','corruption, vice, weakness')]}

def build():
    cards=[{'id':f'major-{i:02}', 'name_en':en,'name_zh':zh,'arcana':'major','number':i,'upright':u.split(', '),'reversed':r.split(', ')} for i,(en,zh,u,r) in enumerate(MAJOR)]
    ranks=['Ace','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Page','Knight','Queen','King']
    chinese=['王牌','二','三','四','五','六','七','八','九','十','侍从','骑士','王后','国王']
    for suit,zh in [('Wands','权杖'),('Cups','圣杯'),('Swords','宝剑'),('Pentacles','星币')]:
        for i,(u,r) in enumerate(MINOR[suit]):
            cards.append({'id':f'{suit.lower()}-{i+1:02}','name_en':f'{ranks[i]} of {suit}','name_zh':zh+chinese[i],'arcana':'minor','suit':suit,'rank':ranks[i],'upright':u.split(', '),'reversed':r.split(', ')})
    return {'source':'A. E. Waite, The Pictorial Key to the Tarot (1910), Part III; original concise English keyword paraphrases. Public-domain source, no vendor assets.','cards':cards}
