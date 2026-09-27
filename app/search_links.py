from urllib.parse import quote_plus
from .profile import PROFILE

def search_links():
    rows=[]
    for role in PROFILE['target_roles']:
        q=quote_plus(f'{role} Bengaluru fresher 0-1 years')
        rows.append({'role':role,
          'naukri':f'https://www.naukri.com/{q}-jobs-in-bangalore',
          'linkedin':f'https://www.linkedin.com/jobs/search/?keywords={q}&location=Bengaluru%2C%20Karnataka%2C%20India',
          'google_ats':f'https://www.google.com/search?q={quote_plus("site:jobs.lever.co OR site:boards.greenhouse.io "+role+" Bengaluru")}'})
    return rows
