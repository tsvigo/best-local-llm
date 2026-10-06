#!/usr/bin/env python3
"""Прогон топ-3 моделей через Ollama API. Только чтение весов, запись — в results/."""
import json, time, urllib.request, os, sys

BASE = "http://127.0.0.1:11434/api/generate"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)

with open(os.path.join(HERE, "tasks.json"), encoding="utf-8") as f:
    cfg = json.load(f)

def gen(model, prompt, options):
    payload = json.dumps({
        "model": model, "prompt": prompt, "stream": False, "options": options
    }).encode("utf-8")
    req = urllib.request.Request(BASE, data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read().decode("utf-8"))
    dt = time.time() - t0
    return data.get("response", ""), data.get("thinking", ""), dt, data

only = sys.argv[1:]  # можно передать id задач для быстрого теста, напр. R1
summary = []
for model in cfg["models"]:
    for t in cfg["tasks"]:
        if only and t["id"] not in only:
            continue
        print(f"[{model}] {t['id']} ...", flush=True)
        try:
            resp, think, dt, raw = gen(model, t["prompt"], cfg["options"])
            eval_ms = raw.get("eval_duration", 0) / 1e6
            eval_count = raw.get("eval_count", 0)
            tps = (eval_count / eval_ms * 1000) if eval_ms > 0 else 0
        except Exception as e:
            resp, think, dt, tps, raw = f"<ERROR: {e}>", "", -1, 0, {"error": str(e)}
        rec = {"model": model, "task": t["id"], "cat": t["cat"],
               "prompt": t["prompt"], "response": resp, "thinking": think,
               "wall_s": round(dt, 1), "tok_per_s": round(tps, 1)}
        fn = os.path.join(OUT, f"{t['id']}__{model.replace(':','_').replace('/','_')}.json")
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        summary.append((model, t["id"], dt, tps))
        print(f"  ok {dt:.0f}s {tps:.1f} tok/s -> {os.path.basename(fn)}", flush=True)

print("\n=== SUMMARY ===")
for m, tid, dt, tps in summary:
    print(f"{m:25s} {tid}  {dt:6.1f}s  {tps:5.1f} tok/s")
