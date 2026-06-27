"""Cyber Intelligence Orchestrator v2.1 — all advanced modules auto-activated by input type."""
from __future__ import annotations
from typing import Dict, Any
import asyncio

from .reporters import terminal as term


async def run_cyber_intel(result: Dict[str, Any], input_type: str = "username") -> Dict[str, Any]:
    """Run all advanced cyber intel modules. Called after base pipeline.
    
    Input types:
      "username" → GitHub, Reddit, Gravatar, Wayback, WhatsApp (if phone found)
      "email"    → Email Intel, Gravatar, CRT.sh, GitHub by email
      "phone"    → WhatsApp Intel full suite
    All types   → Correlation, Keyword Alert, Timeline, Risk Score, Stealth Report
    """
    target = result.get("username","") or result.get("email","") or result.get("phone","")

    # ── Phase A: Input-type specific intel ─────────────────────
    term.print_phase("A", "Cyber Intel", "Running advanced intelligence modules...")
    a_tasks = {}

    if input_type == "username":
        from .modules.github_intel import full_github_intel
        from .modules.reddit_analyzer import full_reddit_intel
        from .modules.wayback_checker import full_wayback_intel
        from .modules.gravatar_lookup import lookup_gravatar, username_to_hash
        a_tasks["github"]   = full_github_intel(target)
        a_tasks["reddit"]   = full_reddit_intel(target)
        a_tasks["wayback"]  = full_wayback_intel(target)
        a_tasks["gravatar"] = lookup_gravatar(username_to_hash(target), is_hash=True)

    elif input_type == "email":
        from .modules.email_intel import full_email_intel
        from .modules.gravatar_lookup import lookup_gravatar
        from .modules.crt_lookup import search_email_domain
        from .modules.github_intel import search_by_email
        a_tasks["email_intel"]      = full_email_intel(target)
        a_tasks["gravatar"]         = lookup_gravatar(target)
        a_tasks["crt"]              = search_email_domain(target)
        a_tasks["github_by_email"]  = search_by_email(target)

    elif input_type == "phone":
        from .modules.whatsapp_intel import full_whatsapp_intel
        a_tasks["whatsapp_intel"] = full_whatsapp_intel(target)

    # Also check WhatsApp for any phones found during investigation
    if input_type != "phone":
        corr_phones = result.get("text_profile", {}).get("phones", [])
        if corr_phones:
            from .modules.whatsapp_intel import full_whatsapp_intel
            a_tasks["whatsapp_intel_found"] = full_whatsapp_intel(corr_phones[0])

    # Run Phase A tasks
    task_keys  = list(a_tasks.keys())
    task_coros = list(a_tasks.values())
    a_results  = await asyncio.gather(*task_coros, return_exceptions=True)

    for key, res in zip(task_keys, a_results):
        if not isinstance(res, dict):
            term.print_warning(f"  {key}: skipped ({type(res).__name__})")
            continue
        if key == "github":
            result["github_intel"] = res
            _print_github(res)
        elif key == "reddit":
            result["reddit_intel"] = res
            _print_reddit(res)
        elif key == "wayback":
            result["wayback_intel"] = res
            _print_wayback(res)
        elif key == "gravatar":
            result["gravatar"] = res
            _print_gravatar(res)
        elif key == "email_intel":
            result["email_intel"] = res
            _print_email_intel(res)
        elif key == "crt":
            result["crt_intel"] = res
            _print_crt(res)
        elif key == "github_by_email":
            result["github_by_email"] = res
            if res:
                term.print_success(f"  GitHub (by email): {len(res)} commit(s) found")
                for r in res[:2]:
                    term.print_warning(f"    → @{r.get('author_login','')} in {r.get('repo','')}")
        elif key in ("whatsapp_intel", "whatsapp_intel_found"):
            result["whatsapp_intel"] = res
            _print_whatsapp(res)

    # ── Phase B: Cross-cutting analysis ────────────────────────
    term.print_phase("B", "Analysis", "Correlation → Keyword Scan → Timeline → Risk Score...")

    from .modules.correlation_engine import correlate, format_correlation
    from .modules.keyword_alert     import scan_all, format_alerts
    from .modules.timeline_builder  import build_timeline, analyze_timeline, format_timeline
    from .modules.risk_scorer       import calculate_risk, format_risk_report

    correlation = correlate(result)
    result["correlation"] = correlation

    kw_alerts = scan_all(result)
    result["keyword_alerts"] = kw_alerts

    events   = build_timeline(result)
    analysis = analyze_timeline(events)
    result["timeline"] = {
        "events":   [{"date": e["date"], "label": e["label"], "source": e["source"], "detail": e.get("detail","")} for e in events],
        "analysis": analysis,
    }

    risk = calculate_risk(result)
    result["risk_score"] = risk

    print(format_correlation(correlation))
    print(format_alerts(kw_alerts))
    print(format_timeline(events, analysis))
    print(format_risk_report(risk))

    # ── Phase C: Stealth Report ─────────────────────────────────
    term.print_phase("C", "Stealth Report", "Generating final intelligence brief...")
    from .modules.stealth_reporter import generate_terminal_brief, save_full_report
    print(generate_terminal_brief(result))
    saved = await save_full_report(result)
    if saved.get("json"):     term.print_success(f"  JSON  → {saved['json']}")
    if saved.get("markdown"): term.print_success(f"  MD    → {saved['markdown']}")
    result["saved_reports"] = saved

    return result


# ── Pretty printers ─────────────────────────────────────────────
def _print_github(d: Dict):
    if not d.get("found"): term.print_warning("  GitHub: not found"); return
    p = d.get("profile", {})
    emails = [e["email"] for e in d.get("extracted_emails",[]) if isinstance(e,dict)]
    term.print_success(f"  GitHub: @{p.get('username','')} | repos={p.get('public_repos',0)} | followers={p.get('followers',0)}")
    if emails:   term.print_warning(f"    ⚡ Real commit emails: {', '.join(emails[:5])}")
    if p.get("location"): term.print_warning(f"    Location: {p['location']}")
    orgs = [o["name"] for o in d.get("organizations",[])[:3]]
    if orgs: term.print_warning(f"    Orgs: {', '.join(orgs)}")
    langs = list(d.get("languages",{}).keys())[:5]
    if langs: term.print_warning(f"    Languages: {', '.join(langs)}")

def _print_reddit(d: Dict):
    if not d.get("found"): term.print_warning("  Reddit: not found"); return
    p = d.get("profile",{}); a = d.get("activity",{})
    term.print_success(f"  Reddit: karma={p.get('total_karma',0)} | age={p.get('account_age_days',0)} days")
    subs = [s[0] for s in a.get("top_subreddits",[])[:5]]
    if subs: term.print_warning(f"    Top subs: {', '.join(subs)}")
    if a.get("estimated_timezone"): term.print_warning(f"    Timezone est.: {a['estimated_timezone']}")
    if a.get("location_clues"):     term.print_warning(f"    Location clues: {', '.join(a['location_clues'])}")

def _print_wayback(d: Dict):
    n = d.get("total_archived", 0)
    if n > 0:
        plats = list(d.get("platforms_archived",{}).keys())
        term.print_success(f"  Wayback: {n} platform(s) archived — {', '.join(plats)}")
    else:
        term.print_warning("  Wayback: no archived profiles found")

def _print_gravatar(d: Dict):
    if d.get("found"):
        accs = [a["domain"] for a in d.get("accounts",[])[:5]]
        term.print_success(f"  Gravatar: {d.get('display_name','')} | linked: {', '.join(accs) or 'none'}")
    elif d.get("has_avatar"):
        term.print_warning("  Gravatar: avatar exists (no public profile)")

def _print_email_intel(d: Dict):
    plats = [p for p, pd in d.get("platforms",{}).items() if isinstance(pd,dict) and pd.get("exists")]
    term.print_success(
        f"  Email: {d.get('provider','')} | disposable={d.get('is_disposable',False)} | "
        f"pattern={d.get('naming_pattern','')} | accounts: {', '.join(plats) or 'none'}")

def _print_crt(d: Dict):
    if d.get("total_certs",0) > 0:
        term.print_success(f"  CRT.sh: {d['total_certs']} cert(s) | {len(d.get('subdomains',[]))} subdomains found")
        if d.get("subdomains"): term.print_warning(f"    Subdomains: {', '.join(d['subdomains'][:6])}")

def _print_whatsapp(d: Dict):
    wa = d.get("whatsapp",{}); country = d.get("country",{})
    tc = d.get("truecaller",{}); rep = d.get("reputation",{})
    status = "ACTIVE ✅" if wa.get("wa_exists") else "NOT FOUND ❌"
    term.print_success(
        f"  WhatsApp: {status} | {country.get('flag','')} {country.get('country','')} | "
        f"{country.get('carrier','')}")
    if tc.get("name"):  term.print_warning(f"    Caller name: {tc['name']}")
    if rep.get("total_reports",0) > 0:
        term.print_warning(f"    ⚠  Spam reports: {rep['total_reports']}")
    plat = d.get("platforms",{})
    if plat.get("telegram",{}).get("found"):
        tg_name = plat["telegram"].get("name","")
        term.print_warning(f"    Telegram: {tg_name or 'found'}")
    if plat.get("google_mentions",{}).get("urls"):
        term.print_warning(f"    Google mentions: {len(plat['google_mentions']['urls'])} URL(s)")
