"""Social graph — interactive network visualization of account connections.

Uses pyvis + networkx to render an interactive HTML graph showing:
  - Target username as the central node
  - Found social media profiles as nodes (color-coded by platform)
  - Edges connecting the target to each profile
  - Recursive usernames as linked sub-nodes

Output: self-contained interactive HTML file.
"""

from __future__ import annotations
from typing import Dict, Any, List, Set, Optional
from pathlib import Path
import re

from ..config import Config


# Platform color map
PLATFORM_COLORS = {
    "github": "#6e40c9",
    "twitter": "#1da1f2",
    "instagram": "#e1306c",
    "youtube": "#ff0000",
    "tiktok": "#000000",
    "facebook": "#1877f2",
    "reddit": "#ff4500",
    "linkedin": "#0a66c2",
    "telegram": "#0088cc",
    "twitch": "#9146ff",
    "discord": "#5865f2",
    "medium": "#00ab6c",
    "spotify": "#1db954",
    "pinterest": "#e60023",
    "snapchat": "#fffc00",
    "steam": "#171a21",
    "vkontakte": "#0077ff",
    "patreon": "#ff424d",
    "tumblr": "#35465c",
    "flickr": "#0063dc",
    "deviantart": "#05cc47",
    "soundcloud": "#ff5500",
    "default": "#58a6ff",
}


def _platform_color(site_name: str) -> str:
    name_lower = site_name.lower().replace(" ", "")
    for key, color in PLATFORM_COLORS.items():
        if key in name_lower:
            return color
    return PLATFORM_COLORS["default"]


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", str(text)).lower()[:30]


def generate(
    result: Dict[str, Any],
    output_path: Optional[Path] = None,
) -> Path:
    """Generate an interactive social graph HTML file.

    Args:
        result: Full investigation result dict from pipeline.
        output_path: Where to write the HTML file.

    Returns:
        Path to the generated HTML file.
    """
    try:
        from pyvis.network import Network
        import networkx as nx
    except ImportError:
        raise ImportError("pyvis + networkx required. Install: pip install pyvis networkx")

    if output_path is None:
        Config.ensure_dirs()
        output_path = Config.OUTPUT_DIR / f"stalker_{result['username']}_graph.html"

    username = result["username"]
    net = Network(height="600px", width="100%", bgcolor="#0d1117", font_color="#c9d1d9")
    net.set_options("""
    {
      "nodes": {"shape": "dot", "size": 20, "font": {"size": 14, "face": "Inter, sans-serif"}},
      "edges": {"color": {"color": "#30363d", "opacity": 0.6}, "smooth": {"type": "curvedCW"}},
      "physics": {"barnesHut": {"gravitationalConstant": -3000, "springLength": 180}},
      "interaction": {"hover": true, "tooltipDelay": 100}
    }
    """)

    # Central target node
    net.add_node(
        username,
        label=f"@{username}",
        title=f"Target: {username}",
        color="#f0883e",
        size=30,
        shape="star",
    )

    # Maigret found sites
    found_sites = result.get("maigret", {}).get("found_sites", [])
    seen_nodes: Set[str] = {_slug(username)}

    for site in found_sites:
        site_name = site.get("site_name", "?")
        node_id = _slug(f"{site_name}_{len(seen_nodes)}")
        if node_id in seen_nodes:
            continue
        seen_nodes.add(node_id)

        label = site_name[:20]
        title_parts = [f"<b>{site_name}</b>"]
        if site.get("url_user"):
            title_parts.append(f'<a href="{site["url_user"]}" target="_blank">Profile</a>')
        if site.get("real_name"):
            title_parts.append(f"Name: {site['real_name']}")
        if site.get("bio"):
            bio = site["bio"][:100]
            title_parts.append(f"Bio: {bio}")

        net.add_node(
            node_id,
            label=label,
            title="\n".join(title_parts),
            color=_platform_color(site_name),
            size=18,
        )
        net.add_edge(username, node_id)

    # Custom API profiles (merged into found_sites already)
    custom_profiles = result.get("maigret", {}).get("custom_profiles", {})
    for platform, profiles in custom_profiles.items():
        for profile in profiles if isinstance(profiles, list) else []:
            node_id = _slug(f"custom_{platform}_{len(seen_nodes)}")
            if node_id in seen_nodes:
                continue
            seen_nodes.add(node_id)

            label = f"{platform}"
            title_parts = [f"<b>{platform.upper()} (Custom API)</b>"]
            if isinstance(profile, dict):
                if profile.get("real_name"):
                    title_parts.append(f"Name: {profile['real_name']}")
                if profile.get("followers") is not None:
                    title_parts.append(f"Followers: {profile['followers']}")

            net.add_node(
                node_id,
                label=label,
                title="\n".join(title_parts),
                color=_platform_color(platform),
                size=16,
                shape="diamond",
            )
            net.add_edge(username, node_id, dashes=True)

    # Recursive usernames
    recursive_data = result.get("recursive", {})
    discovered = recursive_data.get("discovered_usernames", [])
    for disc in discovered:
        rec_username = disc.get("username", "")
        node_id = _slug(f"rec_{rec_username}")
        if node_id in seen_nodes:
            continue
        seen_nodes.add(node_id)

        net.add_node(
            node_id,
            label=f"@{rec_username}",
            title=f"Discovered via {disc.get('source_site', '?')}\nField: {disc.get('source_field', '?')}",
            color="#d2a8ff",
            size=14,
            shape="triangle",
        )
        net.add_edge(username, node_id, dashes=True, color="#d2a8ff")

    net.save_graph(str(output_path))
    return output_path
