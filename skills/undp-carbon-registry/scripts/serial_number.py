#!/usr/bin/env python3
"""Serial number arithmetic for the UNDP carbon registry (6/CMA.4 para 17 format).

Usage:
  serial_number.py parse SERIAL
  serial_number.py split SERIAL AMOUNT        # partial transfer or retirement
  serial_number.py next SERIAL AMOUNT VINTAGE  # next issuance batch after SERIAL
  serial_number.py deduct TOTAL [--omge 2] [--sop 5] [--no-auto]
  serial_number.py --selftest
Output is JSON. Standard library only.
"""
import json, re, sys, argparse

PAT = re.compile(r"^(?P<project>.+)-(?P<start>\d+)-(?P<end>\d+)-(?P<vintage>\d{4})$")

def parse(serial):
    m = PAT.match(serial.strip())
    if not m:
        raise ValueError("not a registry serial: " + serial)
    s, e = int(m["start"]), int(m["end"])
    if s < 1 or e < s:
        raise ValueError("invalid range %d-%d" % (s, e))
    return {"project": m["project"], "start": s, "end": e, "vintage": m["vintage"], "amount": e - s + 1}

def fmt(p, s, e, v):
    return "%s-%d-%d-%s" % (p, s, e, v)

def split(serial, amount):
    b = parse(serial)
    if amount < 1 or amount > b["amount"]:
        raise ValueError("amount must be 1..%d" % b["amount"])
    if amount == b["amount"]:
        return {"full_block": True, "owner_keeps": None, "counterparty_gets": serial}
    cut = b["end"] - amount
    return {"full_block": False,
            "owner_keeps": fmt(b["project"], b["start"], cut, b["vintage"]),
            "counterparty_gets": fmt(b["project"], cut + 1, b["end"], b["vintage"])}

def next_batch(serial, amount, vintage):
    b = parse(serial)
    return fmt(b["project"], b["end"] + 1, b["end"] + amount, vintage)

def deduct(total, omge=2.0, sop=5.0, auto=True):
    if not auto:
        return {"net": total, "omge": 0, "sop": 0}
    o = int(total * omge // 100)
    s = int(total * sop // 100)
    return {"net": total - o - s, "omge": o, "sop": s, "omge_account": "CancellationOMGE", "sop_account": "CancellationSOP"}

def selftest():
    S = "CA0004-VU-CH-356-1-3000-2023"
    checks = [
        parse(S)["amount"] == 3000,
        parse(S)["project"] == "CA0004-VU-CH-356",
        split(S, 1000) == {"full_block": False, "owner_keeps": "CA0004-VU-CH-356-1-2000-2023", "counterparty_gets": "CA0004-VU-CH-356-2001-3000-2023"},
        split(S, 3000)["full_block"] is True,
        next_batch(S, 2000, "2024") == "CA0004-VU-CH-356-3001-5000-2024",
        deduct(1000) == {"net": 930, "omge": 20, "sop": 50, "omge_account": "CancellationOMGE", "sop_account": "CancellationSOP"},
        deduct(99)["omge"] == 1 and deduct(99)["sop"] == 4,
        deduct(500, auto=False)["net"] == 500,
    ]
    for bad in (lambda: split(S, 0), lambda: split(S, 3001), lambda: parse("CA-5-2-2023")):
        try:
            bad(); checks.append(False)
        except ValueError:
            checks.append(True)
    ok = all(checks)
    print(json.dumps({"selftest": "pass" if ok else "fail", "checks": len(checks), "failed": [i for i, c in enumerate(checks) if not c]}))
    return 0 if ok else 1

def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("parse").add_argument("serial")
    p = sub.add_parser("split"); p.add_argument("serial"); p.add_argument("amount", type=int)
    p = sub.add_parser("next"); p.add_argument("serial"); p.add_argument("amount", type=int); p.add_argument("vintage")
    p = sub.add_parser("deduct"); p.add_argument("total", type=int); p.add_argument("--omge", type=float, default=2.0); p.add_argument("--sop", type=float, default=5.0); p.add_argument("--no-auto", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "parse": out = parse(a.serial)
        elif a.cmd == "split": out = split(a.serial, a.amount)
        elif a.cmd == "next": out = {"serial": next_batch(a.serial, a.amount, a.vintage)}
        else: out = deduct(a.total, a.omge, a.sop, not a.no_auto)
    except ValueError as e:
        print(json.dumps({"error": str(e)})); return 2
    print(json.dumps(out)); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
