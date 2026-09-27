import re
from .profile import PROFILE

def match(job):
    text=(job.get('title','')+' '+job.get('description','')).lower()
    skills=sum(PROFILE['skills'].values(),[])
    hit=[x for x in skills if re.search(r'(?<!\w)'+re.escape(x.lower())+r'(?!\w)',text)]
    experience=[]
    for pat in [r'(\d+)\+?\s+years',r'(\d+)\s*[-–]\s*(\d+)\s+years']:
        experience += re.findall(pat,text)
    role_bonus=25 if any(r.lower() in job.get('title','').lower() for r in PROFILE['target_roles']) else 0
    score=min(100,role_bonus+len(hit)*7)
    flags=[]
    if re.search(r'\b([3-9]|10)\+?\s*years?\b',text): flags.append('Job may require more experience than this entry-level profile.')
    if any(x in text for x in ['must have','required','mandatory']) and not hit: flags.append('Review mandatory requirements carefully.')
    return score,hit,experience,flags
