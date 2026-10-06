#!/usr/bin/env python3
"""Детерминированная проверка кода C1/C2 исполнением + сверка R3/U3 с эталоном."""
import json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")

def get(task, model):
    with open(os.path.join(RES, f"{task}__{model}.json"), encoding="utf-8") as f:
        return json.load(f)["response"]

MODELS = ["qwen3.5-32k_latest", "gpt-oss_20b", "qwen3-coder_30b"]

print("== C1 flatten ==")
for m in MODELS:
    code = re.search(r"```python(.*?)```", get("C1", m), re.S).group(1)
    ns = {}
    exec(code, ns)
    f = ns["flatten"]
    assert f([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]
    assert f([]) == []
    assert f([[], [[]]]) == []
    assert f([1, 2, 3]) == [1, 2, 3]
    print(m, "PASS")

print("== C2 sum_first_n ==")
for m in MODELS:
    code = re.search(r"```python(.*?)```", get("C2", m), re.S).group(1)
    ns = {}
    exec(code, ns)
    f = ns["sum_first_n"]
    assert (f(1), f(5), f(100)) == (1, 15, 5050)
    print(m, "PASS")

print("== R3 exact JSON ==")
for m in MODELS:
    assert get("R3", m).strip() == '{"a":1,"b":[2,3]}', m
    print(m, "PASS")

print("== U3 expected text ==")
exp = "Он надел пальто и вышел на улицу. Чтобы не опоздать, он решил поторопиться. В свободное время он любил играть в футбол."
for m in MODELS:
    got = get("U3", m).strip().replace("\u0301", "")
    mark = "PASS" if got == exp else "FAIL -> " + repr(got[:120])
    print(m, mark)
