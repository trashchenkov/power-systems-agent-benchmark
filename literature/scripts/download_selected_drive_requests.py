#!/usr/bin/env python3
import json, re, time
from pathlib import Path
import requests

BASE=Path('/root/investigation-runs/power-systems-agent-benchmark')
MANIFEST=BASE/'literature/metadata/selected_drive_download_manifest.json'
OUTROOT=BASE/'literature/curated_drive_corpus'
REPORT=BASE/'literature/metadata/selected_drive_download_report_requests.json'


def safe_part(s,max_len=150):
    s=s.replace('\x00','')
    s=re.sub(r'[\\:*?"<>|]','_',s)
    s=re.sub(r'\s+',' ',s).strip()
    if len(s)>max_len:
        p=Path(s); s=p.stem[:max_len-20]+'…'+p.suffix
    return s or '_'

def local_path(item):
    return OUTROOT/safe_part(item['source'])/Path(*[safe_part(p) for p in item['path'].split('/')])

def download(fid,dst):
    url='https://drive.google.com/uc?export=download&id='+fid
    with requests.Session() as s:
        r=s.get(url,headers={'User-Agent':'Mozilla/5.0'},allow_redirects=True,timeout=(10,60),stream=True)
        r.raise_for_status()
        # If Google shows virus-confirm page, follow confirm token.
        first=b''
        chunks=[]
        for chunk in r.iter_content(1024*256):
            if chunk:
                chunks.append(chunk)
                first += chunk[:max(0,1024-len(first))]
                if len(first)>=1024: break
        text=first.decode('utf-8','ignore')
        if 'confirm=' in text and 'drive.google.com' in text and 'download_warning' in text:
            import urllib.parse, re as _re
            m=_re.search(r'confirm=([0-9A-Za-z_\-]+)', text)
            if m:
                r.close()
                r=s.get(url+'&confirm='+m.group(1),headers={'User-Agent':'Mozilla/5.0'},allow_redirects=True,timeout=(10,60),stream=True)
                r.raise_for_status(); chunks=[]
        dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('wb') as f:
            for c in chunks: f.write(c)
            for c in r.iter_content(1024*1024):
                if c: f.write(c)
    return dst.stat().st_size

def main():
    items=json.loads(MANIFEST.read_text(encoding='utf-8'))
    ok=[]; existing=[]; failed=[]; start=time.time()
    for i,item in enumerate(items,1):
        dst=local_path(item)
        if dst.exists() and dst.stat().st_size>0:
            existing.append({**item,'local_path':str(dst),'bytes':dst.stat().st_size}); continue
        print(f'[{i}/{len(items)}] {item["source"]}: {item["path"]}', flush=True)
        try:
            n=download(item['id'],dst)
            if n==0: raise RuntimeError('empty file')
            ok.append({**item,'local_path':str(dst),'bytes':n})
        except Exception as e:
            failed.append({**item,'local_path':str(dst),'error':repr(e)})
            try:
                if dst.exists() and dst.stat().st_size==0: dst.unlink()
            except Exception: pass
    report={'total_manifest':len(items),'downloaded':len(ok),'existing':len(existing),'failed':len(failed),'downloaded_bytes':sum(x['bytes'] for x in ok),'existing_bytes':sum(x['bytes'] for x in existing),'duration_seconds':round(time.time()-start,2),'items_downloaded':ok,'items_existing':existing,'items_failed':failed,'outroot':str(OUTROOT)}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['total_manifest','downloaded','existing','failed','downloaded_bytes','existing_bytes','duration_seconds','outroot']},ensure_ascii=False,indent=2))
    return 0 if not failed else 2
if __name__=='__main__': raise SystemExit(main())
