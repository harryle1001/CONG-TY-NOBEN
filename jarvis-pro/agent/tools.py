"""The six tools + a no-model router. Every tool returns {say, card}: a short spoken line and on-screen detail."""
import datetime as dt, re
from pathlib import Path

import data, llm, memory
from vault import norm

TASK = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s*(\d{4}-\d{2}-\d{2})?\s*(.+)$", re.M)
MONEY = ["don", "dat them", "bao gia", "cong no", "thanh toan", "gia", "kg", "trieu", "chot", "hop dong",
         "invoice", "order", "quote", "price", "payment", "demo goi"]
SEARCH_MIN_SCORE = 4.0      # no-model routing: below this, a question is treated as conversation

SPECS = [
    {"name": "search_brain", "description": "Find a specific fact in sir's own files (products, clients, prices, notes, technical know-how).",
     "params": {"type": "object", "properties": {"query": {"type": "string", "description": "Keywords, Vietnamese or English"}}, "required": ["query"]}},
    {"name": "research_web", "description": "Look something up on the public web (market prices, competitors, regulations, news).",
     "params": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "read_inbox", "description": "Read sir's inbox (read-only): who wrote, about what, and whether the sender already exists in his files.",
     "params": {"type": "object", "properties": {"unread_only": {"type": "boolean"}, "about": {"type": "string", "description": "Optional keyword filter"}}}},
    {"name": "brief_me", "description": "Today's briefing: calendar, unread mail, and tasks that slipped past their date.",
     "params": {"type": "object", "properties": {}}},
    {"name": "remember", "description": "Store one fact in memory/ as a dated file. Only when sir asks, or for something that will still matter in three months.",
     "params": {"type": "object", "properties": {"fact": {"type": "string"}}, "required": ["fact"]}},
    {"name": "plan_day", "description": "Plan today: at most five items, ordered by what moves money.",
     "params": {"type": "object", "properties": {}}},
]


class Tools:
    def __init__(self, vault):
        self.v = vault

    def run(self, name, args):
        """Returns (result_dict, is_error). result = {say, card, data?}; data goes to the model only."""
        fn = getattr(self, "t_" + name, None)
        if not fn:
            return {"say": f"I have no tool called {name}."}, True
        try:
            return fn(**(args or {})), False
        except llm.ModelError as e:
            return {"say": "The web is out of reach right now, sir.", "card": _card("Web unavailable", note=str(e))}, True
        except Exception as e:
            return {"say": f"{name} failed: {e}", "card": _card(name, note=f"Error: {e}")}, True

    # ---------- tools ----------
    def t_search_brain(self, query=""):
        hits = self.v.search(query, 5)
        if not hits:
            return {"say": "Nothing in your files matches that, sir.", "card": _card("Search · " + query, note="No matching file.")}
        top = hits[0]["score"]
        hits = [h for h in hits if h["score"] >= top * 0.35]
        files = [h["title"] for h in hits[:3]]
        items = [{"title": h["title"], "sub": h["snippet"], "id": h["id"]} for h in hits]
        excerpts = [{"file": h["id"], "text": self.v.text[h["id"]][:1500]} for h in hits[:3]]
        say = f"From {files[0]}." if len(files) == 1 else f"From {len(files)} files: {', '.join(files)}."
        return {"say": say, "card": _card("Search · " + query, items), "data": {"untrusted_file_excerpts": excerpts}}

    def t_research_web(self, query=""):
        text, sources = llm.web(query)
        return {"say": "Here is what the web says, sir.",
                "card": _card("Web · " + query, [{"title": s["title"], "sub": s["url"], "url": s["url"]} for s in sources], note=text[:900]),
                "data": {"untrusted_web_answer": text, "sources": sources}}

    def t_read_inbox(self, unread_only=False, about=""):
        mails = data.inbox()
        if mails is None:
            return {"say": "No inbox is connected, sir.", "card": _card("Inbox", note="Set JARVIS_INBOX to a Maildir or .eml folder.")}
        if unread_only: mails = [m for m in mails if m["unread"]]
        if about: mails = [m for m in mails if norm(about) in norm(m["subject"] + " " + m["body"] + " " + m["from"])]
        items, known = [], 0
        for m in mails[:12]:
            hit = self.known(m)
            known += bool(hit)
            items.append({"title": f"{'● ' if m['unread'] else ''}{m['from']} — {m['subject']}",
                          "sub": (f"In your files: {self.v.by_id[hit]['title']}" if hit else "Not in your files") + " · " + m["date"][:16].replace("T", " "),
                          "id": hit})
        unread = sum(m["unread"] for m in mails)
        say = f"{len(mails)} messages, {unread} unread; {known} from people already in your files."
        return {"say": say, "card": _card("Inbox", items),
                "data": {"untrusted_emails": [{k: m[k] for k in ("from", "subject", "date", "unread", "body")} for m in mails[:12]]}}

    def t_brief_me(self):
        cal = data.calendar(1) or []
        mails = [m for m in (data.inbox() or []) if m["unread"]]
        slipped = [t for t in self.tasks() if t["due"] and t["due"] < data.today()]
        items = [{"title": e["start"][11:16] + "  " + e["title"], "sub": "Calendar"} for e in cal]
        items += [{"title": f"● {m['from']} — {m['subject']}", "sub": "Unread", "id": self.known(m)} for m in mails[:5]]
        items += [{"title": t["text"], "sub": f"Slipped · due {t['due']} · {self.v.by_id[t['file']]['title']}", "id": t["file"]} for t in slipped]
        first = f"First up at {cal[0]['start'][11:16]}: {cal[0]['title']}. " if cal else "Nothing on the calendar. "
        say = first + f"{len(mails)} unread, {len(slipped)} slipped."
        note = None if data.calendar_file() else "No calendar connected (JARVIS_CALENDAR)."
        return {"say": say, "card": _card(f"Brief · {data.today().isoformat()}", items, note=note)}

    def t_remember(self, fact=""):
        path = memory.write(fact)
        return {"say": f"Noted, sir. I wrote “{fact}” to {path}.", "card": _card("Memory", [{"title": fact, "sub": path}])}

    def t_plan_day(self):
        cand = []
        for e in data.calendar(1) or []:
            cand.append({"text": e["start"][11:16] + " " + e["title"], "why": "on the calendar", "base": 1})
        for m in data.inbox() or []:
            if m["unread"]:
                cand.append({"text": f"Reply to {m['from']}: {m['subject']}", "why": "unread", "base": 0, "id": self.known(m)})
        for t in self.tasks():
            if t["due"] and t["due"] <= data.today() + dt.timedelta(days=1):
                late = t["due"] < data.today()
                cand.append({"text": t["text"], "why": f"overdue since {t['due']}" if late else f"due {t['due']}", "base": 2 if late else 1, "id": t["file"]})
        for c in cand:
            c["money"] = sum(k in norm(c["text"]) for k in MONEY)
        cand.sort(key=lambda c: (-min(c["money"], 2), -c["base"], c["text"]))
        top = cand[:5]
        items = [{"title": f"{i + 1}. {c['text']}", "sub": c["why"] + (" · moves money" if c["money"] else ""), "id": c.get("id")}
                 for i, c in enumerate(top)]
        say = f"{len(top)} things, sir. Start with: {top[0]['text']}." if top else "Nothing pressing today, sir."
        return {"say": say, "card": _card("Plan · " + data.today().isoformat(), items,
                                          note="Order: money-related first (orders, quotes, debts, payments), then overdue, then the rest.")}

    # ---------- helpers ----------
    def known(self, mail):
        """Node id of a file that mentions this sender (by name, address or domain), else None."""
        keys = [k for k in {norm(mail["from"]), norm(mail["addr"].split("@")[0])} if len(k) >= 5]
        for n in sorted(self.v.nodes, key=lambda n: -n["degree"]):
            if n["type"] == "folder": continue
            if any(k in norm(n["title"]) or norm(n["title"]) in k for k in keys if len(norm(n["title"])) >= 5):
                return n["id"]
        return None

    def tasks(self):
        out = []
        for nid, text in self.v.text.items():
            for done, due, body in TASK.findall(text):
                if done == " ":
                    out.append({"text": body.strip(), "due": dt.date.fromisoformat(due) if due else None, "file": nid})
        return out

    # ---------- no-model routing ----------
    def route(self, text):
        """Decide without a model. Returns (tool_name|None, args, reply_if_conversation)."""
        q = norm(text).strip(" ?!.")
        words = set(re.findall(r"\w+", q))
        if re.search(r"\b(brief|tom tat|hom nay co gi|briefing)\b", q): return "brief_me", {}, None
        if re.search(r"\b(plan|ke hoach|len lich|lam gi truoc)\b", q): return "plan_day", {}, None
        if re.search(r"\b(inbox|email|mail|hop thu|thu moi)\b", q): return "read_inbox", {}, None
        if re.match(r"^(remember|ghi nho|nho giup|nho rang|note that)\b", q):
            fact = re.sub(r"^\s*(remember|ghi nhớ|nhớ giúp|nhớ rằng|note that)\s*[:,]?\s*", "", text, flags=re.I)
            return "remember", {"fact": fact}, None
        if re.search(r"\b(research|tra cuu web|search the web|tren mang)\b", q):
            return None, {}, "I'd need the model to search the web, sir, and it isn't connected."
        greeting = re.match(r"^(hello|hi|hey|alo|chao|xin chao|good (morning|afternoon|evening)|jarvis)\b", q)
        chat = re.search(r"\b(can you hear|nghe (anh|toi|ro)?\s*khong|how are you|khoe khong|thank|cam on|what do you think|ban nghi sao)\b", q)
        followup = re.match(r"^(why|tai sao|vi sao|sao vay|and|con|what about|the (first|second|third))\b", q)
        if followup:
            return None, {}, "Follow-ups need the model, sir, and it's offline. Ask me the full question and I'll search your files."
        if greeting or chat or len(words) <= 2 and not self.v.search(text, 1):
            return None, {}, "At your service, sir. The model is offline: I can search your files, brief you or plan the day, but not converse."
        hits = self.v.search(text, 1)
        if hits and hits[0]["score"] >= SEARCH_MIN_SCORE:
            return "search_brain", {"query": text}, None
        return None, {}, "The model is offline, sir, and nothing in your files matches that closely."


def _card(title, items=None, note=None):
    c = {"title": title, "items": items or []}
    if note: c["note"] = note
    return c


def load_prompt():
    t = (Path(__file__).resolve().parent / "prompt.md").read_text("utf-8")
    return t.replace("{today}", data.today().strftime("%A %d %B %Y")).replace("{mode}", data.mode())
