from pathlib import Path
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from .profile import PROFILE

BROWSER_DIR = Path(__file__).resolve().parents[1] / '.browser_profile'


def _field_key(label: str) -> str:
    return re.sub(r'[^a-z0-9 ]+', ' ', (label or '').lower()).strip()


def value_for(label: str, job: dict, answers: dict) -> str | None:
    k = _field_key(label)
    if any(x in k for x in ['full name', 'your name', 'name']):
        return PROFILE['name']
    if 'email' in k:
        return PROFILE['email']
    if 'phone' in k or 'mobile' in k or 'contact number' in k:
        return PROFILE.get('phone', '')
    if 'linkedin' in k:
        return PROFILE['linkedin']
    if 'github' in k:
        return PROFILE['github']
    if 'portfolio' in k or 'website' in k:
        return PROFILE['portfolio']
    if any(x in k for x in ['current location', 'location', 'city']):
        return PROFILE['location']
    if 'notice period' in k or 'availability' in k or 'joining' in k:
        return 'Immediately'
    if 'current ctc' in k or 'current salary' in k:
        return 'Not applicable - Fresher'
    if 'expected ctc' in k or 'expected salary' in k:
        return 'As per company standards'
    if 'experience' in k and ('year' in k or 'total' in k):
        return 'Fresher'
    for q, a in answers.items():
        qk = _field_key(q)
        if qk and (qk in k or k in qk):
            return a
    return None


def _label_for(locator):
    try:
        aria = locator.get_attribute('aria-label') or ''
        placeholder = locator.get_attribute('placeholder') or ''
        name = locator.get_attribute('name') or ''
        ident = locator.get_attribute('id') or ''
        return ' '.join(x for x in [aria, placeholder, name, ident] if x)
    except Exception:
        return ''


def run_apply_agent(job: dict, answers: dict, auto_submit: bool = False):
    url = job.get('url') or ''
    if not url:
        raise ValueError('This job has no URL. Open the original job page and add its URL first.')

    result = {'url': url, 'filled': [], 'skipped': [], 'warnings': [], 'submitted': False, 'screenshot': ''}
    BROWSER_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(BROWSER_DIR),
            headless=False,
            channel='chrome',
            viewport={'width': 1440, 'height': 950},
            args=['--start-maximized'],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        try:
            page.wait_for_load_state('networkidle', timeout=15000)
        except Exception:
            pass

        body = (page.locator('body').inner_text(timeout=10000) or '').lower()
        if any(x in body for x in ['captcha', 'recaptcha', 'hcaptcha', 'verify you are human']):
            result['warnings'].append('CAPTCHA/human verification detected. Complete it manually in the browser.')
        if any(x in body for x in ['two-factor', 'two factor', 'mfa', 'otp', 'one-time password']):
            result['warnings'].append('MFA/OTP detected. Complete authentication manually in the browser.')
        if any(x in body for x in ['sign in', 'log in', 'login']):
            result['warnings'].append('The site may require login. Log in manually in the opened browser if needed.')

        # Fill visible text-like controls using their accessible metadata.
        for selector in ['input:not([type=hidden]):not([type=file]):not([type=submit]):not([type=button])', 'textarea']:
            loc = page.locator(selector)
            count = min(loc.count(), 80)
            for i in range(count):
                el = loc.nth(i)
                try:
                    if not el.is_visible():
                        continue
                    label = _label_for(el)
                    val = value_for(label, job, answers)
                    if val:
                        awaitable = False
                        el.fill(val)
                        result['filled'].append(label[:120])
                    else:
                        result['skipped'].append(label[:120] or selector)
                except Exception as exc:
                    result['warnings'].append(f'Could not fill field: {str(exc)[:100]}')

        # Never automatically accept legal attestations or consent checkboxes.
        checks = page.locator('input[type=checkbox]')
        for i in range(min(checks.count(), 50)):
            el = checks.nth(i)
            try:
                if el.is_visible():
                    label = _label_for(el)
                    result['skipped'].append('Checkbox/consent: ' + (label[:100] or 'unlabeled'))
            except Exception:
                pass

        shot = BROWSER_DIR / 'last_application_review.png'
        page.screenshot(path=str(shot), full_page=True)
        result['screenshot'] = str(shot)

        if auto_submit and not result['warnings']:
            buttons = page.locator('button, input[type=submit], a[role=button]')
            submitted = False
            for i in range(min(buttons.count(), 60)):
                b = buttons.nth(i)
                try:
                    if not b.is_visible() or not b.is_enabled():
                        continue
                    txt = (b.inner_text() or b.get_attribute('value') or '').strip().lower()
                    if any(x in txt for x in ['submit application', 'submit', 'apply now', 'apply', 'send application']):
                        b.click()
                        submitted = True
                        result['submitted'] = True
                        break
                except Exception:
                    continue
            if not submitted:
                result['warnings'].append('No safe application submit button was detected; nothing was submitted.')

        # Keep browser open briefly for manual review. The user can continue interacting with it.
        page.bring_to_front()
        if not auto_submit:
            result['warnings'].append('Review mode: fields were filled, but the final application was NOT submitted.')
        return result
