import csv, json, os, re, time, html
from pathlib import Path
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

base=Path(__file__).resolve().parent
rows=json.loads((base/'local_archive_bibliography_task_table.json').read_text(encoding='utf-8'))
cache_path=base/'bing_title_search_cache.json'
cache=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}

STOP_PHRASES=['кафедра','направление подготовки','boxoft','purchase from','требования к','использование отдельно','готовность применять','для защиты понижающих','diverse industries','учредитель','вывод:','также в санпин','3.10 газовая защита','paper is dedicated','the term microgrid','department of electrical power']

def file_stem(file):
    s=os.path.splitext(os.path.basename(file or ''))[0]
    s=re.sub(r'__[0-9a-f]{8}$','',s); s=re.sub(r'_[0-9a-f]{8}$','',s)
    s=s.replace('_',' ').replace('-', ' ')
    return re.sub(r'\s+',' ',s).strip()

def clean_title(s):
    s=(s or '').strip(); s=re.sub(r'\.{3,}.*$','',s).strip(); s=re.sub(r'\s+',' ',s)
    return s[:220]

def choose_query(r):
    tg=clean_title(r.get('title_guess') or ''); fn=file_stem(r.get('file') or '')
    low=tg.lower(); bad=(len(tg)<18 or any(p in low for p in STOP_PHRASES) or re.match(r'^[0-9_\-\s\.]+$',tg or ''))
    return tg if (not bad and len(tg)<=180) else fn

def parse_bing(text, max_results=5):
    soup=BeautifulSoup(text,'html.parser')
    out=[]
    for li in soup.select('li.b_algo'):
        a=li.find('a')
        if not a: continue
        title=' '.join(a.get_text(' ',strip=True).split())
        href=a.get('href','')
        snippet=''
        p=li.find('p')
        if p: snippet=' '.join(p.get_text(' ',strip=True).split())
        if title and href:
            out.append({'title':title,'url':href,'snippet':snippet})
        if len(out)>=max_results: break
    return out

def bing_search(query):
    if query in cache: return cache[query]
    out=None
    for q in ['"'+query+'"', query]:
        try:
            url='https://www.bing.com/search?'+urlencode({'q':q,'setlang':'ru-RU'})
            r=requests.get(url,headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64)'},timeout=12)
            results=parse_bing(r.text,5)
            out={'query':query,'searched_as':q,'results':results,'status':'found' if results else 'no_results'}
            if results: break
        except Exception as e:
            out={'query':query,'searched_as':q,'results':[],'status':'error','error':str(e)}
    cache[query]=out
    cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
    time.sleep(0.15)
    return out

def save_rows():
    (base/'local_archive_bibliography_task_table.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open(base/'local_archive_bibliography_task_table.csv','w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)

target=[]; seen=set()
for r in rows:
    if r.get('match_review_status') in ('not_found','false_match','needs_manual_verification') and r.get('task_count') not in ('',None,'0'):
        target.append(r); seen.add(r.get('file'))
for r in rows:
    if r.get('match_review_status')=='not_found' and r.get('file') not in seen:
        target.append(r); seen.add(r.get('file'))
print('targets',len(target),'task-bearing',sum(1 for r in target if r.get('task_count') not in ('',None,'0')))
for i,r in enumerate(target,1):
    q=choose_query(r); res=bing_search(q)
    r['web_title_search_query']=q
    r['bing_title_search_status']=res.get('status')
    r['bing_title_search_results']=res.get('results',[])
    if res.get('results'):
        r['bing_title_top_result_title']=res['results'][0]['title']; r['bing_title_top_result_url']=res['results'][0]['url']
    else:
        r['bing_title_top_result_title']=''; r['bing_title_top_result_url']=''
    print(f"{i}/{len(target)} {res.get('status'):10} :: {q[:100]}",flush=True)
    if i%5==0: save_rows()
save_rows()
print('done')
