from fastapi import FastAPI,Form
from fastapi.responses import HTMLResponse,RedirectResponse,FileResponse
from .search_links import search_links
from .import_job import job_from_url,job_from_text
from .matcher import match
from .tailor import tailor_cv,application_answers
from .documents import pdf,docx
from .tracker import add,load
from .apply_agent import run_apply_agent

app=FastAPI(title='Jagadeesh Job Agent')
STATE={}

def esc(s):
    return str(s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def page(body):
    return HTMLResponse(f'''<!doctype html><html><head><meta charset="utf-8"><title>Jagadeesh Job Agent</title><style>body{{font-family:Arial,sans-serif;max-width:1100px;margin:25px auto;padding:0 18px;background:#f5f7fa;color:#222}}.card{{background:#fff;padding:20px;margin:14px 0;border-radius:12px;box-shadow:0 1px 5px #ddd}}input,textarea{{width:100%;box-sizing:border-box;padding:10px;margin:6px 0 12px;border:1px solid #ccc;border-radius:7px}}textarea{{min-height:220px}}button,.btn{{background:#222;color:#fff;border:0;border-radius:8px;padding:10px 14px;text-decoration:none;display:inline-block;margin:3px;cursor:pointer}}a{{color:#1757a6}}.score{{font-size:30px;font-weight:700}}pre{{white-space:pre-wrap;background:#f2f3f5;padding:14px;border-radius:8px;overflow:auto}}.muted{{color:#666}}</style></head><body>{body}</body></html>''')

@app.get('/',response_class=HTMLResponse)
def home():
    rows=''.join(f"<div class='card'><b>{esc(r['role'])}</b><br><a target='_blank' href='{r['naukri']}'>Naukri</a> · <a target='_blank' href='{r['linkedin']}'>LinkedIn</a> · <a target='_blank' href='{r['google_ats']}'>Google / public ATS</a></div>" for r in search_links())
    return page(f'''<h1>Jagadeesh Agentic Job Search</h1><p>Search → import → match → tailor → review → export. <b>Final application submission stays manual.</b></p>
    <div class='card'><h2>1. Import a public job URL</h2><form method='post' action='/import'><input name='url' placeholder='Public job / ATS URL' required><button>Review Application</button></form>
    <h2>2. Or paste a job description</h2><form method='post' action='/paste'><input name='title' placeholder='Job title' required><input name='company' placeholder='Company'><input name='location' placeholder='Location'><input name='url' placeholder='Job URL'><textarea name='description' placeholder='Paste the complete job description' required></textarea><button>Review Application</button></form></div>
    <div class='card'><h2>Application tracker</h2><a class='btn' href='/tracker'>Open tracker</a></div><h2>Search links</h2>{rows}''')

@app.post('/import')
def imp(url:str=Form(...)):
    try:
        STATE['job']=job_from_url(url); STATE['cv']=tailor_cv(STATE['job']); STATE['ans']=application_answers(STATE['job']); STATE['m']=match(STATE['job']); return RedirectResponse('/review',303)
    except Exception as e: return page(f'<div class="card"><h2>Could not import this URL</h2><pre>{esc(e)}</pre><p>Try pasting the job description instead.</p><a href="/">Back</a></div>')

@app.post('/paste')
def paste(title:str=Form(...),company:str=Form(''),location:str=Form(''),url:str=Form(''),description:str=Form(...)):
    STATE['job']=job_from_text(title,company,location,url,description); STATE['cv']=tailor_cv(STATE['job']); STATE['ans']=application_answers(STATE['job']); STATE['m']=match(STATE['job']); return RedirectResponse('/review',303)

@app.get('/review',response_class=HTMLResponse)
def review():
    if 'job' not in STATE: return page('<div class="card"><h2>No job loaded</h2><a href="/">Back</a></div>')
    j=STATE['job']; sc,hit,exp,flags=STATE['m']; qa=''.join(f'<p><b>{esc(q)}</b><br>{esc(a)}</p>' for q,a in STATE['ans'].items())
    return page(f'''<h1>Review Application</h1><div class='card'><h2>{esc(j['title'])}</h2><p>{esc(j['company'])} · {esc(j['location'])} · Source: {esc(j['source'])}</p><p><a target='_blank' href='{esc(j['url'])}'>Open original job</a></p><div class='score'>{sc}/100 match</div><p><b>Matched skills:</b> {esc(', '.join(hit) or 'None identified')}</p><p><b>Experience evidence:</b> {esc(str(exp) or 'None detected')}</p><p><b>Review flags:</b> {esc(', '.join(flags) or 'None detected')}</p></div>
    <div class='card'><h2>Tailored CV</h2><pre>{esc(STATE['cv'])}</pre><a class='btn' href='/pdf'>Export PDF</a><a class='btn' href='/docx'>Export DOCX</a></div>
    <div class='card'><h2>Application Answers</h2>{qa}</div>
    <div class='card'><h2>AI Apply Agent</h2><p>The agent can open the original job page in a real Chrome window, fill supported fields from your profile and generated answers, and show you the completed form.</p><form method='post' action='/apply-agent'><label><input type='checkbox' name='auto_submit' value='yes'> Allow final submit when no CAPTCHA/MFA/login warning is detected</label><br><button>Start AI Apply Agent</button></form><p class='muted'>It will not solve CAPTCHA, bypass MFA, or accept legal/consent checkboxes automatically. Review mode is the default.</p></div><div class='card'><h2>Approval Gate</h2><p>Review every claim and field before applying.</p><form method='post' action='/track'><button>Mark as Reviewed</button></form><a class='btn' target='_blank' href='{esc(j['url'])}'>Open Job / Apply</a></div><a href='/'>← Search another job</a>''')


@app.post('/apply-agent', response_class=HTMLResponse)
def apply_agent(auto_submit: str = Form('')):
    if 'job' not in STATE:
        return page('<div class="card"><h2>No job loaded</h2><a href="/">Back</a></div>')
    try:
        result = run_apply_agent(STATE['job'], STATE.get('ans', {}), auto_submit=(auto_submit == 'yes'))
        status = 'SUBMITTED' if result['submitted'] else 'NOT SUBMITTED'
        filled = ''.join(f'<li>{esc(x)}</li>' for x in result['filled']) or '<li>No fields filled automatically.</li>'
        warnings = ''.join(f'<li>{esc(x)}</li>' for x in result['warnings']) or '<li>None</li>'
        return page(f'''<h1>AI Apply Agent — {status}</h1><div class='card'><p><b>Job:</b> {esc(STATE['job'].get('title'))} · {esc(STATE['job'].get('company'))}</p><p><b>URL:</b> <a target='_blank' href='{esc(result['url'])}'>Open job</a></p></div><div class='card'><h2>Fields filled</h2><ul>{filled}</ul></div><div class='card'><h2>Warnings / manual steps</h2><ul>{warnings}</ul></div><div class='card'><p>The Chrome window opened by the agent remains available for you to inspect and continue manually.</p><a class='btn' href='/review'>← Back to Review</a></div>''')
    except Exception as e:
        return page(f'<div class="card"><h2>Apply Agent error</h2><pre>{esc(e)}</pre><p>Make sure Chrome is installed and run <code>python -m playwright install chromium</code> if needed.</p><a href="/review">Back</a></div>')

@app.post('/track')
def track():
    if 'job' in STATE: add(STATE['job'],'Reviewed')
    return RedirectResponse('/tracker',303)

@app.get('/tracker',response_class=HTMLResponse)
def tracker():
    rows=''.join(f"<tr><td>{esc(x['title'])}</td><td>{esc(x['company'])}</td><td>{esc(x['status'])}</td><td><a target='_blank' href='{esc(x['url'])}'>Job</a></td></tr>" for x in load()) or '<tr><td colspan=4>No tracked applications yet.</td></tr>'
    return page(f'''<h1>Application Tracker</h1><div class='card'><table border='1' cellpadding='8' cellspacing='0' width='100%'><tr><th>Role</th><th>Company</th><th>Status</th><th>Link</th></tr>{rows}</table></div><a href='/'>← Back</a>''')

@app.get('/pdf')
def pdf_route(): return FileResponse(pdf(STATE['cv']),filename='Jagadeesh-Tailored-CV.pdf')
@app.get('/docx')
def docx_route(): return FileResponse(docx(STATE['cv']),filename='Jagadeesh-Tailored-CV.docx')
