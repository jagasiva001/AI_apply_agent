import json, requests
from bs4 import BeautifulSoup
from .ats import HEADERS

def _jsonld(soup):
    for tag in soup.find_all('script',type='application/ld+json'):
        try:
            data=json.loads(tag.string or tag.get_text())
        except Exception:
            continue
        items=data if isinstance(data,list) else [data]
        for item in items:
            if isinstance(item,dict) and item.get('@type')=='JobPosting': return item
    return None

def job_from_url(url):
    r=requests.get(url,headers=HEADERS,timeout=25); r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser'); data=_jsonld(soup)
    if data:
        org=data.get('hiringOrganization') or {}
        loc=data.get('jobLocation') or ''
        if isinstance(loc,list): loc='; '.join(str(x) for x in loc)
        return {'title':data.get('title') or 'Imported Job','company':org.get('name',''),'location':str(loc),'url':url,'description':BeautifulSoup(data.get('description',''),'html.parser').get_text('\n',strip=True),'source':'URL import'}
    title=soup.title.get_text(' ',strip=True) if soup.title else 'Imported Job'
    return {'title':title,'company':'','location':'','url':url,'description':soup.get_text('\n',strip=True)[:60000],'source':'URL import'}

def job_from_text(title,company,location,url,description):
    return {'title':title,'company':company,'location':location,'url':url,'description':description,'source':'Pasted description'}
