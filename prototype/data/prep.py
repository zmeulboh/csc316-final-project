import csv,json,collections,sys
D='data/'
def fred(n):
    out=[]
    for r in csv.DictReader(open(D+n+'.csv',encoding='utf-8-sig')):
        k=list(r.keys())[1]
        if r[k] not in ('.',''): out.append((r['observation_date'],float(r[k])))
    return out
gs10=[(d[:7],v) for d,v in fred('GS10') if d>='1962']
daily=[(d,v) for d,v in fred('DGS10')]
oct26=[v for d,v in daily if d.startswith('2026-10')]
gs10.append(('2026-10',round(sum(oct26)/len(oct26),2)))
rec=[d[:7] for d,v in fred('USREC') if d>='1962' and v==1]
def monthly(pairs):
    m=collections.defaultdict(list)
    for d,v in pairs: m[d[:7]].append(v)
    return [(k,round(sum(v)/len(v),2)) for k,v in sorted(m.items())]
mort=[x for x in monthly(fred('MORTGAGE30US')) if x[0]>='2019-01']
boc=[]
lines=open(D+'boc5.csv',encoding='utf-8-sig').read().split('\n')
i=lines.index('"date","BD.CDN.5YR.DQ.YLD"')
for l in lines[i+1:]:
    p=l.replace('"','').split(',')
    if len(p)==2 and p[1]: boc.append((p[0],float(p[1])))
boc=monthly(boc)
# statcan ontario
want={'Construction [23]':'con','Manufacturing [31-33]':'man','Finance, insurance, real estate, rental and leasing [52-53]':'fin',
'Wholesale and retail trade [41, 44-45]':'ret','Accommodation and food services [72]':'food','Professional, scientific and technical services [54]':'tech',
'Educational services [61]':'edu','Health care and social assistance [62]':'health','Public administration [91]':'pub','Total employed, all industries':'all'}
s=collections.defaultdict(dict)
for r in csv.DictReader(open('statcan/14100355.csv',encoding='utf-8-sig')):
    if r['GEO']=='Ontario' and r['Statistics']=='Estimate' and r['Data type']=='Seasonally adjusted' and r['VALUE'] and r['North American Industry Classification System (NAICS)'] in want and r['REF_DATE']>='2019-01':
        s[want[r['North American Industry Classification System (NAICS)']]][r['REF_DATE']]=float(r['VALUE'])
ind={k:{'now':v['2026-09'],'feb22':v['2022-02'],'yr':v['2025-09'],'series':[[d,v[d]] for d in sorted(v)]} for k,v in s.items()}
for k in ind:
    if k not in('con','all'): ind[k].pop('series')
out=dict(gs10=gs10,rec=rec,daily=[x for x in daily if x[0]>='2025-10'],mort=mort,boc=boc,ind=ind)
json.dump(out,open('bundle.json','w'),separators=(',',':'))
print(len(json.dumps(out,separators=(',',':'))))
g=dict(gs10)
for y in ['1981','1994','2000','2007','2020','2023']:
    xs=[(d,v) for d,v in gs10 if d.startswith(y)]; print(y,max(xs,key=lambda t:t[1]),min(xs,key=lambda t:t[1]))
print(gs10[-4:], boc[-3:], mort[-3:])
print('2021',[x for x in boc if x[0].startswith('2021')][:3], [x for x in gs10 if x[0].startswith('2021')][:2])
