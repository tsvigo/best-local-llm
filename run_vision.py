#!/usr/bin/env python3
"""Прогон vision-моделей: картинка base64 + промпт через Ollama API."""
import json, time, urllib.request, os, sys, base64

BASE = "http://127.0.0.1:11434/api/generate"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)

with open(os.path.join(HERE, "vision_tasks.json"), encoding="utf-8") as f:
    cfg = json.load(f)

def img_b64(path):
    with open(os.path.join(HERE, path), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

only = sys.argv[1:]
summary = []
for model in cfg["models"]:
    for t in cfg["tasks"]:
        if only and t["id"] not in only:
            continue
        print(f"[{model}] {t['id']} ...", flush=True)
        payload = json.dumps({
            "model": model, "prompt": t["prompt"], "stream": False,
            "images": [img_b64(t["image"])], "options": cfg["options"]
        }).encode("utf-8")
        req = urllib.request.Request(BASE, data=payload,
                                     headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                raw = json.loads(r.read().decode("utf-8"))
            resp, think, dt = raw.get("response", ""), raw.get("thinking", ""), time.time() - t0
            eval_ms = raw.get("eval_duration", 0) / 1e6
            ec = raw.get("eval_count", 0)
            tps = (ec / eval_ms * 1000) if eval_ms > 0 else 0
        except Exception as e:
            resp, think, dt, tps = f"<ERROR: {e}>", "", -1, 0
        safe = model.replace(":", "_").replace("/", "_")
        rec = {"model": model, "task": t["id"], "image": t["image"],
               "prompt": t["prompt"], "response": resp, "thinking": think,
               "wall_s": round(dt, 1), "tok_per_s": round(tps, 1)}
        with open(os.path.join(OUT, f"{t['id']}__{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        summary.append((model, t["id"], dt, tps))
        print(f"  ok {dt:.0f}s {tps:.1f} tok/s", flush=True)

print("\n=== SUMMARY ===")
for m, tid, dt, tps in summary:
    print(f"{m[:40]:40s} {tid}  {dt:6.1f}s  {tps:5.1f} tok/s")
