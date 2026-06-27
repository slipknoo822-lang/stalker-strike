"""Cyber Intelligence Orchestrator — Phase 3+ advanced modules.

Runs automatically after the base investigation pipeline completes.
Adds: GitHub intel, Reddit analysis, Gravatar, Wayback Machine,
Correlation Engine, Keyword Alert, Timeline Builder, Risk Score.

Called from pipeline.py or menu.py after run_investigation().
"""
from __future__ import annotations
from typing import Dict, Any
import asyncio

from .reporters import terminal as term


async def run_cyber_intel(result: Dict[str, Any], input_type: str = "username") -> Dict[str, Any]:
    """Run all advanced cyber intel modules on investigation result.
    
    Args:
        result: Output from run_investigation() or similar pipeline
        input_type: "username", "email", or "phone"
    
    Returns:
        Updated result dict with new intel fields added.
    """
    target = result.get("username","") or result.get("email","") or result.get("phone","")
    maigret = result.get("maigret", {})
    found_sites = maigret.get("found_sites", [])

    # ── Phase A: Platform-specific intel (parallel) ───────────
    term.print_phase("A", "Cyber Intel", f"Running advanced intelligence modules...")
    
    a_tasks = {}

    if input_type == "username":
        from .modules.github_intel import full_github_intel
        from .modules.reddit_analyzer import full_reddit_intel
        from .modules.wayback_checker import full_wayback_intel
        from .modules.gravatar_lookup import lookup_gravatar, username_to_hash

        a_tasks["github"] = full_github_intel(target)
        a_tasks["reddit"] = full_reddit_intel(target)
        a_tasks["wayback"] = full_wayback_intel(target)
        a_tasks["gravatar"] = lookup_gravatar(username_to_hash(target), is_hash=True)

    elif input_type == "email":
        from .modules.email_intel import full_email_intel
        from .modules.gravatar_lookup import lookup_gravatar, email_to_hash
        from .modules.crt_lookup import search_email_domain

        a_tasks["email_intel"] = full_email_intel(target)
        a_tasks["gravatar"] = lookup_gravatar(target)
        a_tasks["crt"] = search_email_domain(target)

        # Also check GitHub by email
        from .modules.github_intel import search_by_email
        a_tasks["github_by_email"] = search_by_email(target)

    elif input_type == "phone":
        # For phone: try to extract username from bio and run those checks
        from .modules.wayback_checker import check_url_archived
        # Check WhatsApp/Telegram archive
        phone_clean = target.replace("+","").replace("-","").replace(" ","")
        a_tasks["wa_archive"] = check_url_archived(f"https://wa.me/{phone_clean}")

    # Run all A tasks
    task_keys = list(a_tasks.keys())
    task_coros = list(a_tasks.values())
    a_results = await asyncio.gather(*task_coros, return_exceptions=True)

    for key, res in zip(task_keys, a_results):
        if isinstance(res, dict):
            if key == "github": result["github_intel"] = res; _print_github(res)
            elif key == "reddit": result["reddit_intel"] = res; _print_reddit(res)
            elif key == "wayback": result["wayback_intel"] = res; _print_wayback(res)
            elif key == "gravatar": result["gravatar"] = res; _print_gravatar(res)
            elif key == "email_intel": result["email_intel"] = res; _print_email_intel(res)
            elif key == "crt": result["crt_intel"] = res; _print_crt(res)
            elif key == "github_by_email": result["github_by_email"] = res
            elif key == "wa_archive": result["wa_archive"] = res
        else:
            term.print_warning(f"  {key}: {res}")

    # ── Phase B: Cross-cutting analysis ───────────────────────
    term.print_phase("B", "Analysis", "Running correlation, keyword scan, timeline, risk scoring...")

    from .modules.correlation_engine import correlate, format_correlation
    from .modules.keyword_alert import scan_all, format_alerts
    from .modules.timeline_builder import build_timeline, analyze_timeline, format_timeline
    from .modules.risk_scorer import calculate_risk, format_risk_report

    correlation = correlate(result)
    result["correlation"] = correlation
    kw_alerts = scan_all(result)
    result["keyword_alerts"] = kw_alerts
    timeline_events = build_timeline(result)
    timeline_analysis = analyze_timeline(timeline_events)
    result["timeline"] = {"events": [{"date": e["date"], "label": e["label"], "source": e["source"], "detail": e.get("detail","")} for e in timeline_events], "analysis": timeline_analysis}
    risk = calculate_risk(result)
    result["risk_score"] = risk

    # Print results
    print(format_correlation(correlation))
    print(format_alerts(kw_alerts))
    print(format_timeline(timeline_events, timeline_analysis))
    print(format_risk_report(risk))

    return result


# ── Pretty printers ───────────────────────────────────────────

def _print_github(data: Dict):
    if not data.get("found"): term.print_warning("  GitHub: not found"); return
    p = data.get("profile", {})
    emails = [e["email"] for e in data.get("extracted_emails", []) if isinstance(e,dict)]
    term.print_success(f"  GitHub: @{p.get('username','')} | repos={p.get('public_repos',0)} | followers={p.get('followers',0)}")
    if emails: term.print_warning(f"    Real emails from commits: {', '.join(emails[:3])}")
    if p.get("location"): term.print_warning(f"    Location: {p['location']}")
    if data.get("organizations"): term.print_warning(f"    Orgs: {', '.join(o['name'] for o in data['organizations'][:3])}")
    if data.get("languages"): term.print_warning(f"    Languages: {', '.join(list(data['languages'].keys())[:5])}")

def _print_reddit(data: Dict):
    if not data.get("found"): term.print_warning("  Reddit: not found"); return
    p = data.get("profile", {}); a = data.get("activity", {})
    term.print_success(f"  Reddit: karma={p.get('total_karma',0)} | age={p.get('account_age_days',0)} days")
    subs = [s[0] for s in a.get("top_subreddits",[])[:5]]
    if subs: term.print_warning(f"    Top subreddits: {', '.join(subs)}")
    if a.get("estimated_timezone"): term.print_warning(f"    Est. timezone: {a['estimated_timezone']}")
    if a.get("location_clues"): term.print_warning(f"    Location clues: {', '.join(a['location_clues'])}")

def _print_wayback(data: Dict):
    archived = data.get("total_archived", 0)
    if archived > 0:
        platforms = list(data.get("platforms_archived",{}).keys())
        term.print_success(f"  Wayback: {archived} platform(s) archived: {', '.join(platforms)}")
    else:
        term.print_warning("  Wayback: no archived profiles found")

def _print_gravatar(data: Dict):
    if data.get("found"):
        term.print_success(f"  Gravatar: found — {data.get('display_name','')} | accounts: {len(data.get('accounts',[]))}")
        accs = [a["domain"] for a in data.get("accounts",[])[:5]]
        if accs: term.print_warning(f"    Linked: {', '.join(accs)}")
    elif data.get("has_avatar"):
        term.print_warning("  Gravatar: avatar found (no public profile)")

def _print_email_intel(data: Dict):
    term.print_success(f"  Email Intel: {data.get('provider','')} | disposable={data.get('is_disposable',False)} | pattern={data.get('naming_pattern','')}")
    for platform, pdata in data.get("platforms",{}).items():
        if isinstance(pdata,dict) and pdata.get("exists"):
            term.print_warning(f"    Account found on: {platform}")

def _print_crt(data: Dict):
    if data.get("total_certs",0) > 0:
        term.print_success(f"  CRT.sh: {data['total_certs']} cert(s) | {len(data.get('subdomains',[]))} subdomains")
        if data.get("subdomains"): term.print_warning(f"    Subdomains: {', '.join(data['subdomains'][:5])}")
