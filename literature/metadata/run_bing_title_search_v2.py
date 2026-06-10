import csv,json,os,re,time,html,base64
from pathlib import Path
from urllib.parse import urlencode,urlparse,parse_qs,unquote
import requests
from bs4 import BeautifulSoup
base=Path(__file__).resolve().parent
rows=json.loads((base/'local_archive_bibliography_task_table.json').read_text(encoding='utf-8'))
cache_path=base/'bing_title_search_cache_v2.json'
cache=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}
STOP_PHRASES=['кафедра','направление подготовки','boxoft','purchase from','требования к','использование отдельно','готовность применять','для защиты понижающих','diverse industries','учредитель','вывод:','также в санпин','3.10 газовая защита','paper is dedicated','the term microgrid','department of electrical power']
def file_stem(file):
 s=os.path.splitext(os.path.basename(file or ''))[0]; s=re.sub(r'__[0-9a-f]{8}$','',s); s=re.sub(r'_[0-9a-f]{8}$','',s); s=s.replace('_',' ').replace('-', ' '); return re.sub(r'\s+',' ',s).strip()
def clean_title(s):
 s=(s or '').strip(); s=re.sub(r'\.{3,}.*$','',s).strip(); s=re.sub(r'\s+',' ',s); return s[:220]
def choose_query(r):
 tg=clean_title(r.get('title_guess') or ''); fn=file_stem(r.get('file') or ''); low=tg.lower(); bad=(len(tg)<18 or any(p in low for p in STOP_PHRASES) or re.match(r'^[0-9_\-\s\.]+$',tg or '')); return tg if (not bad and len(tg)<=180) else fn
def unwrap_bing(href):
 href=html.unescape(href or '')
 qs=parse_qs(urlparse(href).query)
 u=qs.get('u',[''])[0]
 if u.startswith('a1'):
  try:
   s=u[2:]; s += '='*((4-len(s)%4)%4); return base64.urlsafe_b64decode(s).decode('utf-8','ignore')
  except Exception: pass
 return href
def parse(text):
 soup=BeautifulSoup(text,'html.parser'); out=[]
 for h2 in soup.select('li.b_algo h2'):
  a=h2.find('a',href=True)
  if not a: continue
  li=h2.find_parent('li')
  sn=''
  p=li.find('p') if li else None
  if p: sn=' '.join(p.get_text(' ',strip=True).split())
  out.append({'title':' '.join(a.get_text(' ',strip=True).split()),'url':unwrap_bing(a['href']),'snippet':sn})
  if len(out)>=5: break
 return out
def search(q):
 if q in cache: return cache[q]
 out=None
 for qq in ['"'+q+'"',q]:
  try:
   url='https://www.bing.com/search?'+urlencode({'q':qq,'mkt':'ru-RU','setlang':'ru'})
   r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=12)
   res=parse(r.text); out={'query':q,'searched_as':qq,'status':'found' if res else 'no_results','results':res}
   if res: break
  except Exception as e: out={'query':q,'searched_as':qq,'status':'error','results':[],'error':str(e)}
 cache[q]=out; cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8'); time.sleep(.1); return out

target=[]; seen=set()
for r in rows:
 if r.get('match_review_status') in ('not_found','false_match','needs_manual_verification') and r.get('task_count') not in ('',None,'0'):
  target.append(r); seen.add(r.get('file'))
for r in rows:
 if r.get('match_review_status')=='not_found' and r.get('file') not in seen:
  target.append(r); seen.add(r.get('file'))
print('targets',len(target))
for i,r in enumerate(target,1):
 q=choose_query(r); res=search(q)
 r['bing_title_search_v2_status']=res.get('status'); r['bing_title_search_v2_results']=res.get('results',[])
 if res.get('results'):
  r['bing_title_v2_top_result_title']=res['results'][0]['title']; r['bing_title_v2_top_result_url']=res['results'][0]['url']
 print(i,res.get('status'),q[:80], '=>', (res.get('results') or [{'title':''}])[0].get('title','')[:80], flush=True)
(base/'local_archive_bibliography_task_table.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
keys=[]
for r in rows:
 for k in r:
  if k not in keys: keys.append(k)
with open(base/'local_archive_bibliography_task_table.csv','w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
print('done')
