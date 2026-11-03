#!/usr/bin/env python3
"""Probe a UNDP carbon registry checkout.

Usage:
  registry_probe.py ROOT           # summary: modules, docs, enum drift count
  registry_probe.py ROOT --drift   # full backend vs frontend enum value drift
Read only. Standard library only. Output is JSON.
"""
import json, os, re, sys

VAL = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*[\"']([^\"']+)[\"']", re.M)
CASE = re.compile(r"case\s+[\"']([a-z0-9-]+)[\"']\s*:")

def norm(name):
    n = name.lower()
    for suf in (".enum.ts", ".ts", "enum"):
        if n.endswith(suf):
            n = n[: -len(suf)]
    return re.sub(r"[^a-z0-9]", "", n)

def enum_values(folder):
    out = {}
    if not os.path.isdir(folder):
        return out
    for f in sorted(os.listdir(folder)):
        if f.endswith(".ts"):
            with open(os.path.join(folder, f), encoding="utf-8", errors="replace") as h:
                out[norm(f)] = (f, set(VAL.findall(h.read())))
    return out

def drift(root):
    be = enum_values(os.path.join(root, "backend/services/libs/shared/src/enum"))
    casl = os.path.join(root, "backend/services/libs/shared/src/casl/role.enum.ts")
    if os.path.isfile(casl):
        be["role"] = ("casl/role.enum.ts", set(VAL.findall(open(casl, encoding="utf-8").read())))
    fe = enum_values(os.path.join(root, "web/src/Definitions/Enums"))
    rows = []
    for k in sorted(set(be) & set(fe)):
        (bf, bv), (ff, fv) = be[k], fe[k]
        if bv and fv and bv != fv:
            rows.append({"backend": bf, "frontend": ff,
                         "only_backend": sorted(bv - fv), "only_frontend": sorted(fv - bv)})
    return {"paired": len(set(be) & set(fe)), "backend_only_files": len(set(be) - set(fe)), "drifting": rows}

def main(argv):
    if not argv:
        print(__doc__); return 2
    root = os.path.abspath(argv[0])
    main_ts = os.path.join(root, "backend/services/src/main.ts")
    if not os.path.isfile(main_ts):
        print(json.dumps({"error": "not a registry checkout", "root": root})); return 1
    d = drift(root)
    if "--drift" in argv:
        print(json.dumps(d, indent=1)); return 0
    docs = []
    for sub in ("docs/business", "docs/testing"):
        p = os.path.join(root, sub)
        if os.path.isdir(p):
            docs += [sub + "/" + f for f in sorted(os.listdir(p)) if f.endswith(".md")]
    specs_dir = os.path.join(root, "tests/e2e/article6")
    specs = sorted(f for f in os.listdir(specs_dir) if f.endswith(".spec.ts")) if os.path.isdir(specs_dir) else []
    agents_dir = os.path.join(root, ".claude/agents")
    agents = sorted(f[:-3] for f in os.listdir(agents_dir)) if os.path.isdir(agents_dir) else []
    print(json.dumps({
        "root": root,
        "modules": CASE.findall(open(main_ts, encoding="utf-8").read()),
        "docs": docs, "e2e_specs": specs, "agents": agents,
        "enum_pairs": d["paired"], "enum_pairs_drifting": len(d["drifting"]),
    }, indent=1))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
