"""Create GitHub Issues from docs/60_USE_CASES.md. Requires GITHUB_TOKEN and repository owner/name."""
import os, re, sys, urllib.request, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs'/'60_USE_CASES.md'
REPO=os.getenv('GITHUB_REPOSITORY','').strip() or 'YOUR_OWNER/BookSpace'
TOKEN=os.getenv('GITHUB_TOKEN','').strip()
if not TOKEN:
    sys.exit('Set GITHUB_TOKEN first. Example: export GITHUB_TOKEN=ghp_...')
if REPO=='YOUR_OWNER/BookSpace':
    sys.exit('Set GITHUB_REPOSITORY=owner/repository first.')
text=DOC.read_text(encoding='utf-8')
items=re.findall(r'^\d+\. \[(MVP|NEXT)\] (.+)$',text,re.M)
if len(items)!=60:
    sys.exit(f'Expected 60 user stories, parsed {len(items)}')
created=0; skipped=0
for idx,(kind,story) in enumerate(items,1):
    title=f'US-{idx:02d} · {story.split(",")[0][:95]}'
    body=f'## User story\n{story}\n\n**Release:** {kind}\n**Project:** BookSpace — электронная библиотека\n\n### Acceptance criteria\n- [ ] Реализован основной пользовательский сценарий.\n- [ ] Проверены права доступа и ошибки ввода.\n- [ ] Обновлена документация при необходимости.'
    req=urllib.request.Request(f'https://api.github.com/repos/{REPO}/issues',data=json.dumps({'title':title,'body':body,'labels':['MVP' if kind=='MVP' else 'backlog']}).encode(),headers={'Authorization':f'Bearer {TOKEN}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            data=json.loads(response.read().decode());created+=1;print(f"Created #{data['number']}: {title}")
    except Exception as exc:
        skipped+=1;print(f'Failed US-{idx:02d}: {exc}',file=sys.stderr)
print(f'Done. Created: {created}; failed: {skipped}; total stories: {len(items)}')
