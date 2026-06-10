#!/usr/bin/env python3
import json
import os
import re
import sys
import time
import signal
from pathlib import Path

import gdown


class DownloadTimeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise DownloadTimeout('per-file download timeout')

BASE = Path('/root/investigation-runs/power-systems-agent-benchmark')
MANIFEST = BASE / 'literature/metadata/selected_drive_download_manifest.json'
OUTROOT = BASE / 'literature/curated_drive_corpus'
REPORT = BASE / 'literature/metadata/selected_drive_download_report.json'
LOG = BASE / 'literature/metadata/selected_drive_download.log'


def safe_part(s: str, max_len: int = 150) -> str:
    s = s.replace('\x00', '')
    s = re.sub(r'[\\:*?"<>|]', '_', s)
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > max_len:
        stem = Path(s).stem[:max_len-20]
        suf = Path(s).suffix
        s = stem + '…' + suf
    return s or '_'


def local_path(item):
    parts = [safe_part(p) for p in item['path'].split('/')]
    return OUTROOT / safe_part(item['source']) / Path(*parts)


def main():
    items = json.loads(MANIFEST.read_text(encoding='utf-8'))
    OUTROOT.mkdir(parents=True, exist_ok=True)
    done = []
    failed = []
    existing = []
    started = time.time()
    with LOG.open('a', encoding='utf-8') as log:
        log.write(f'\n=== run start {time.strftime("%Y-%m-%d %H:%M:%S")} items={len(items)} ===\n')
        for i, item in enumerate(items, 1):
            dst = local_path(item)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and dst.stat().st_size > 0:
                existing.append({**item, 'local_path': str(dst), 'bytes': dst.stat().st_size})
                print(f'[{i}/{len(items)}] SKIP existing {dst}')
                continue
            url = 'https://drive.google.com/uc?id=' + item['id']
            print(f'[{i}/{len(items)}] DOWNLOAD {item["source"]}: {item["path"]}', flush=True)
            try:
                # Per-file alarm prevents one broken Drive file from blocking the whole corpus intake.
                old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
                signal.alarm(90)
                try:
                    res = gdown.download(url=url, output=str(dst), quiet=True, resume=True, use_cookies=False)
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                if not res or not dst.exists() or dst.stat().st_size == 0:
                    raise RuntimeError(f'gdown returned {res}; file missing/empty')
                rec = {**item, 'local_path': str(dst), 'bytes': dst.stat().st_size}
                done.append(rec)
                log.write('OK\t{}\t{}\t{}\n'.format(item['id'], dst.stat().st_size, item['path']))
            except Exception as e:
                failed.append({**item, 'local_path': str(dst), 'error': repr(e)})
                log.write('FAIL\t{}\t{}\t{}\n'.format(item['id'], repr(e), item['path']))
                # Remove empty/partial files with zero bytes; keep nonzero partials for resume.
                try:
                    if dst.exists() and dst.stat().st_size == 0:
                        dst.unlink()
                except Exception:
                    pass
    report = {
        'started_at_epoch': started,
        'duration_seconds': round(time.time() - started, 2),
        'manifest': str(MANIFEST),
        'outroot': str(OUTROOT),
        'total_manifest': len(items),
        'downloaded': len(done),
        'existing': len(existing),
        'failed': len(failed),
        'downloaded_bytes': sum(x.get('bytes', 0) for x in done),
        'existing_bytes': sum(x.get('bytes', 0) for x in existing),
        'items_downloaded': done,
        'items_existing': existing,
        'items_failed': failed,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['total_manifest','downloaded','existing','failed','downloaded_bytes','existing_bytes','duration_seconds','outroot']}, ensure_ascii=False, indent=2))
    if failed:
        print(f'FAILED details saved: {REPORT}', file=sys.stderr)
    return 0 if not failed else 2

if __name__ == '__main__':
    raise SystemExit(main())
