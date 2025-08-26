# helpers/renderers.py
from typing import Any

def render_resources(res: Any, *, include_money=True, include_moradinium=True, include_downtime=False) -> str:
    if not res:
        return "*No relevant resources.*"
    parts = []

    if include_money:
        money = []
        pp = getattr(res, "platinum", 0) or 0
        gp = getattr(res, "gold", 0) or 0
        sp = getattr(res, "silver", 0) or 0
        cp = getattr(res, "copper", 0) or 0
        if pp: money.append(f"{pp}pp")
        if gp: money.append(f"{gp}gp")
        if sp: money.append(f"{sp}sp")
        if cp: money.append(f"{cp}cp")
        if money:
            parts.append("**Money:** " + ", ".join(money))

    if include_moradinium and getattr(res, "moradinium", None) is not None:
        parts.append(f"**Moradinium:** {getattr(res, 'moradinium', 0)}")

    if include_downtime and getattr(res, "downtime", None) is not None:
        parts.append(f"**Downtime:** {getattr(res, 'downtime', 0)} days")

    return "\n".join(parts) if parts else "*No relevant resources.*"

def render_lifestyle(ls: Any) -> str:
    if not ls:
        return "**Lifestyle:** —"
    lt = (getattr(ls, "lifestyle_type", "") or "modest").capitalize()
    weeks = getattr(ls, "living_weeks", 0) or 0
    return f"**Lifestyle:** {lt} (Weeks open: {weeks})"

def render_bastion(b: Any) -> str:
    if not b or int(getattr(b, "bastion_flag", 0) or 0) == 0:
        return "**Bastion:** None"
    weeks = getattr(b, "weeks_of_maintenance", 0) or 0
    turn  = bool(getattr(b, "turn_available_flag", 0))
    return (f"**Bastion:** Owned\n"
            f"**Maintenance weeks open:** {weeks}\n"
            f"**Turn available:** {turn}")

def render_item(it: Any) -> str:
    if not it:
        return "**Item:** —"
    name = getattr(it, "name", "") or "—"
    desc = getattr(it, "description", "") or "—"
    ben  = getattr(it, "benefits", "") or "—"
    link = getattr(it, "link", "") or "—"
    return (f"**Item:** {name}\n"
            f"**Description:** {str(desc)}\n"
            f"**Benefits:** {str(ben)}\n"
            f"**Link:** {str(link)}")

def render_skills(sk: Any) -> str:
    if not sk:
        return "**Crafting Reputation:** —"
    crp = getattr(sk, "crp", 0) or 0
    return f"**Crafting Reputation:** {crp}"

def render_actor_summary(actor: Any) -> str:
    parts = [
        f"**Name:** {getattr(actor, 'name', '—')}",
        f"**Level:** {getattr(actor, 'level', '—')}",
        f"**Badge:** {getattr(actor, 'badge', '—')}",
    ]
    ls = getattr(actor, "lifestyle", None)
    if ls:
        parts.append(render_lifestyle(ls))
        b = getattr(ls, "bastion", None)
        if b:
            parts.append(render_bastion(b))
    res = getattr(actor, "resources", None)
    if res:
        parts.append(render_resources(res, include_money=True, include_moradinium=True, include_downtime=True))
    # skills/items könntest du hier ebenfalls ergänzen
    return "\n".join(parts)