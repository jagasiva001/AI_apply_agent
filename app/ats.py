import os, requests
from dotenv import load_dotenv
load_dotenv()

HEADERS={'User-Agent':'Jagadeesh-Job-Agent/1.0'}

def greenhouse_jobs(board):
    url=f'https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true'
    r=requests.get(url,headers=HEADERS,timeout=20); r.raise_for_status()
    jobs=[]
    for j in r.json().get('jobs',[]):
        jobs.append({'title':j.get('title',''),'company':board,'location':(j.get('location') or {}).get('name',''),'url':j.get('absolute_url',''),'description':j.get('content',''),'source':'Greenhouse'})
    return jobs

def lever_jobs(company):
    url=f'https://api.lever.co/v0/postings/{company}?mode=json'
    r=requests.get(url,headers=HEADERS,timeout=20); r.raise_for_status()
    jobs=[]
    for j in r.json():
        desc=' '.join(x for x in [j.get('descriptionPlain',''),j.get('additionalPlain','')] if x)
        jobs.append({'title':j.get('text',''),'company':company,'location':(j.get('categories') or {}).get('location',''),'url':j.get('hostedUrl',''),'description':desc,'source':'Lever'})
    return jobs

def configured_jobs():
    out=[]
    for board in filter(None,(x.strip() for x in os.getenv('GREENHOUSE_BOARDS','').split(','))):
        try: out.extend(greenhouse_jobs(board))
        except Exception: pass
    for company in filter(None,(x.strip() for x in os.getenv('LEVER_COMPANIES','').split(','))):
        try: out.extend(lever_jobs(company))
        except Exception: pass
    return out
