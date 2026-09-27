from .profile import PROFILE

def tailor_cv(job):
    text=(job.get('title','')+' '+job.get('description','')).lower()
    allskills=sum(PROFILE['skills'].values(),[])
    priority=[s for s in allskills if s.lower() in text]
    priority=list(dict.fromkeys(priority + ['Python','AWS','Linux','Docker','Jenkins','Generative AI','RAG']))[:12]
    projects=sorted(PROFILE['projects'],key=lambda p:sum(s.lower() in text for s in p['skills']),reverse=True)
    lines=[f"# {PROFILE['name']}",f"**Target Role:** {job.get('title','')}",f"{PROFILE['location']} | {PROFILE['email']} | {PROFILE['linkedin']} | {PROFILE['github']}",'', '## PROFESSIONAL SUMMARY',PROFILE['summary']+f" Relevant strengths for this position: **{', '.join(priority)}**.",'','## TECHNICAL SKILLS']
    for group,skills in PROFILE['skills'].items(): lines.append(f"**{group}:** {', '.join(skills)}")
    lines += ['', '## PROJECTS']
    for p in projects:
        relevant=[s for s in p['skills'] if s.lower() in text]
        lines += [f"### {p['name']}",p['description'],f"Relevant: {', '.join(relevant or p['skills'])}",'']
    lines += ['## INTERNSHIP',PROFILE['internship'],'','## EDUCATION',PROFILE['education'],'','## CAREER FOCUS',', '.join(PROFILE['target_roles'])]
    return '\n'.join(lines)

def application_answers(job):
    title=job.get('title','this role')
    return {
      'Why are you interested in this role?':f'I am interested in the {title} role because it aligns with my MCA background and hands-on exposure to Python, cloud/DevOps fundamentals and practical AI projects.',
      'Why should we consider you?':'I am an entry-level candidate with practical project experience in Python, Generative AI, RAG, AI agents and DevOps fundamentals. I focus on learning quickly, troubleshooting systematically and applying technical concepts to real tasks.',
      'Describe your relevant experience.':'My experience includes an internship at Besant Technologies covering ML with Python, DevOps and Generative AI, plus projects involving a meeting intelligence/support bot, medicine recommendation system and job matching bot.',
      'Availability':'Available to discuss joining and availability based on the employer’s requirement.'
    }
