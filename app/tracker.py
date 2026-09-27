import json
from pathlib import Path
DB=Path(__file__).resolve().parent.parent/'data'/'applications.json'

def load():
    if not DB.exists(): return []
    try: return json.loads(DB.read_text(encoding='utf-8'))
    except Exception: return []

def add(job,status='Reviewed'):
    rows=load(); rows.append({'title':job.get('title',''),'company':job.get('company',''),'location':job.get('location',''),'url':job.get('url',''),'source':job.get('source',''),'status':status}); DB.write_text(json.dumps(rows,indent=2),encoding='utf-8'); return rows
