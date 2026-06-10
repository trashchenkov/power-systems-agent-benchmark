import csv, json, os, re, time, html
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup

base=Path(__file__).resolve().parent
rows=json.loads((base/'local_archive_bibliography_task_table.json').read_text(encoding='utf-8'))
cache_path=base/'web_title_search_cache.json'
cache=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}

STOP_PHRASES=[
    'кафедра', 'направление подготовки', 'boxoft', 'purchase from', 'требования к',
    'использование отдельно', 'готовность применять', 'для защиты понижающих',
    'diverse industries', 'учредитель', 'вывод:', 'также в санпин', '3.10 газовая защита',
    'paper is dedicated', 'the term microgrid', 'department of electrical power',
]

def file_stem(file):
    s=os.path.splitext(os.path.basename(file or ''))[0]
    s=re.sub(r'__[0-9a-f]{8}$','',s)
    s=re.sub(r'_[0-9a-f]{8}$','',s)
    s=s.replace('_',' ').replace('-', ' ')
    s=re.sub(r'\s+',' ',s).strip()
    return s

def clean_title(s):
    s=(s or '').strip()
    s=re.sub(r'\.{3,}.*$', '', s).strip()
    s=re.sub(r'\s+', ' ', s)
    return s[:220]

def choose_query(r):
    tg=clean_title(r.get('title_guess') or '')
    fn=file_stem(r.get('file') or '')
    low=tg.lower()
    bad=(len(tg)<18 or any(p in low for p in STOP_PHRASES) or re.match(r'^[0-9_\-\s\.]+$', tg or ''))
    if not bad and len(tg) <= 180:
        return tg
    return fn

def unwrap(href):
    href=html.unescape(href or '')
    if 'duckduckgo.com/l/' in href:
        qs=parse_qs(urlparse(href).query)
        if 'uddg' in qs:
            href=unquote(qs['uddg'][0])
    return href

def parse_results(text, max_results=5):
    soup=BeautifulSoup(text,'html.parser')
    results=[]
    for a in soup.select('a.result__a'):
        title=' '.join(a.get_text(' ', strip=True).split())
        href=unwrap(a.get('href',''))
        if title and href:
            results.append({'title':title,'url':href})
        if len(results)>=max_results: break
    return results

def ddg_search(query, max_results=5):
    if query in cache:
        return cache[query]
    out=None
    for q in ['"'+query+'"', query]:
        try:
            url='https://html.duckduckgo.com/html/?'+urlencode({'q': q})
            r=requests.get(url, headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64)'}, timeout=25)
            results=parse_results(r.text, max_results)
            if results:
                out={'query':query,'searched_as':q,'results':results,'status':'found'}
                break
            out={'query':query,'searched_as':q,'results':[],'status':'no_results'}
        except Exception as e:
            out={'query':query,'searched_as':q,'results':[],'status':'error','error':str(e)}
    cache[query]=out
    cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2), encoding='utf-8')
    time.sleep(0.2)
    return out

target=[]; seen=set()
for r in rows:
    if r.get('match_review_status') in ('not_found','false_match','needs_manual_verification') and r.get('task_count') not in ('',None,'0'):
        target.append(r); seen.add(r.get('file'))
for r in rows:
    if r.get('match_review_status')=='not_found' and r.get('file') not in seen:
        target.append(r); seen.add(r.get('file'))
print('targets',len(target),'task-bearing',sum(1 for r in target if r.get('task_count') not in ('',None,'0')))

for i,r in enumerate(target,1):
    q=choose_query(r)
    res=ddg_search(q,5)
    r['web_title_search_query']=q
    r['web_title_search_status']=res.get('status')
    r['web_title_search_results']=res.get('results',[])
    if res.get('results'):
        r['web_title_top_result_title']=res['results'][0]['title']
        r['web_title_top_result_url']=res['results'][0]['url']
    else:
        r['web_title_top_result_title']=''
        r['web_title_top_result_url']=''
    print(f"{i}/{len(target)} {res.get('status'):10} :: {q[:100]}", flush=True)

(base/'local_archive_bibliography_task_table.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2), encoding='utf-8')
keys=[]
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
with open(base/'local_archive_bibliography_task_table.csv','w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
print('wrote cache/json/csv')
