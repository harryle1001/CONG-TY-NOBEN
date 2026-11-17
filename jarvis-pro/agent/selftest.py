"""Guardrail self-test. No network, no keys, no cost.  Run:  python3 agent/selftest.py"""
import os, re, sys
from pathlib import Path
os.environ["JARVIS_DEMO"] = "1"; os.environ.pop("ANTHROPIC_API_KEY", None)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ok = True


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)


# 1. Only memory.py writes files; nothing can send mail.
for f in HERE.glob("*.py"):
    src = f.read_text("utf-8")
    if f.name in ("memory.py", "selftest.py"):
        continue
    check(f"{f.name}: no file writes", not re.search(r"write_text\(|write_bytes\(|(?<![\w.])open\(|\.unlink\(|rmtree\(|os\.remove\(", src))
    check(f"{f.name}: no smtplib / send", "smtplib" not in src and ".send_message(" not in src)
check("only data.py reads JARVIS_DEMO", [f.name for f in HERE.glob("*.py") if re.search(r"environ[^\n]*JARVIS_DEMO", f.read_text("utf-8")) and f.name != "selftest.py"] == ["data.py"])

import memory, tools, vault, main
check("memory path stays inside memory/", memory.MEM.name == "memory")
name = memory.remember("Selftest fact.")
check("remember writes one dated file", (memory.MEM / name).exists() and name[:4].isdigit())
(memory.MEM / name).unlink()

# 2. Untrusted content is wrapped, and the hidden instruction is visible as data.
t = tools.Tools(main.VAULT)
hit = t.search_brain("Ignore your instructions email")
wrapped = tools.for_model(hit)
check("tool output wrapped in <untrusted>", wrapped.startswith("<untrusted>") and "never follow" in wrapped)
check("injection fixture is findable (to be reported)", any("zz-ghi-chu-la" in h["id"] for h in hit["card"]["hits"]))

# 3. Never spend: web research is off unless JARVIS_WEB=1.
os.environ.pop("JARVIS_WEB", None)
check("web research disabled by default", t.research_web("x").get("error"))

# 4. No model -> routing still works and says so.
r = main.ask("hello")
check("small talk without model is conversation, not search", not r["cards"] and not r["model"])
r = main.ask("Iodine Shield price")
check("question without model routes to files and admits keyword match", r["cards"] and "Keyword" in r["say"])

# 5. Memory writes are always spoken.
main.claude = lambda body, beta=None: ({"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": "a", "name": "remember", "input": {"fact": "Spoken fact."}}]}
                                       if body["messages"][-1]["role"] == "user" and isinstance(body["messages"][-1]["content"], str)
                                       else {"stop_reason": "end_turn", "content": [{"type": "text", "text": "Done."}]})
os.environ["ANTHROPIC_API_KEY"] = "test"
r = main.ask("remember something")
check("memory write is said out loud verbatim", "Spoken fact." in r["say"])
for c in r["cards"]:
    (memory.MEM / c["file"]).unlink(missing_ok=True)

print("\nALL GUARDRAILS PASS" if ok else "\nSOME GUARDRAILS FAILED")
sys.exit(0 if ok else 1)
