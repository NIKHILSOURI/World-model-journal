"""Agreement between the three reviewers on the agreement sample.

Run from the bundle folder after all three have exported their agreement JSON:
    python scripts/agreement.py                                   # reads agreement/agreement_R*.json
    python scripts/agreement.py a.json b.json c.json              # or name the files

Writes agreement/agreement_report.md and agreement/records_to_discuss.csv.
The formulas (and the seeded bootstrap) match the Resolve tab of screening_tool.html,
so both report the same numbers. Only the Python standard library is used.
"""
import csv, glob, json, math, os, sys

THRESHOLD = 0.80
BOOT_B, BOOT_SEED = 2000, 20261016
M32 = 0xFFFFFFFF

files = sys.argv[1:] or sorted(glob.glob("agreement/agreement_R*.json"))
if len(files) < 2:
    sys.exit("Need at least two reviewer files (agreement/agreement_R1_xx.json and so on).")


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    rid = d.get("reviewer_id") or os.path.basename(path)
    if d.get("reviewer_slot"):
        rid = f"R{d['reviewer_slot']} {rid}"
    return dict(id=rid, slot=d.get("reviewer_slot") or 9, phase=d.get("phase", ""),
                dec={x["corpus_id"]: x for x in d.get("decisions", d) if x.get("corpus_id") and x.get("decision")})


R = sorted((load(f) for f in files), key=lambda r: r["slot"])
for r in R:
    if r["phase"] and r["phase"] != "agreement":
        print(f"warning: {r['id']} exported in the {r['phase']} phase, not the agreement round")
common = [i for i in R[0]["dec"] if all(i in r["dec"] for r in R)]
if not common:
    sys.exit("The files share no records.")
m, n = len(R), len(common)
units = [[r["dec"][i]["decision"] for r in R] for i in common]
binu = [["exclude" if v == "exclude" else "include" for v in u] for u in units]


def cohen(pairs, labels=("include", "exclude")):
    k = len(pairs)
    obs = {(a, b): 0 for a in labels for b in labels}
    r1 = {a: 0 for a in labels}; r2 = {a: 0 for a in labels}
    for a, b in pairs:
        obs[(a, b)] += 1; r1[a] += 1; r2[b] += 1
    po = sum(obs[(l, l)] for l in labels) / k
    pe = sum((r1[l] / k) * (r2[l] / k) for l in labels)
    if pe >= 1:
        return dict(k=float("nan"), se=float("nan"), po=po)
    return dict(k=(po - pe) / (1 - pe), se=math.sqrt(po * (1 - po) / (k * (1 - pe) ** 2)), po=po)


def fleiss(us):
    N = len(us); mm = len(us[0])
    tot, pbar = {}, 0.0
    for u in us:
        cnt = {}
        for v in u:
            cnt[v] = cnt.get(v, 0) + 1
        s = 0
        for c, x in cnt.items():
            s += x * x; tot[c] = tot.get(c, 0) + x
        pbar += (s - mm) / (mm * (mm - 1))
    pbar /= N
    pe = sum((x / (N * mm)) ** 2 for x in tot.values())
    return (pbar - pe) / (1 - pe) if pe < 1 else float("nan")


def mulberry32(seed):
    """Same generator as the tool, so the bootstrap draws the same resamples."""
    a = seed & M32
    def rnd():
        nonlocal a
        a = (a + 0x6D2B79F5) & M32
        t = ((a ^ (a >> 15)) * (1 | a)) & M32
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & M32)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296
    return rnd


def fleiss_ci(us):
    rnd, N, ks = mulberry32(BOOT_SEED), len(us), []
    for _ in range(BOOT_B):
        s = [us[math.floor(rnd() * N)] for _ in range(N)]
        k = fleiss(s)
        if not math.isnan(k):
            ks.append(k)
    if len(ks) < BOOT_B / 2:
        return None
    ks.sort()
    return ks[math.floor(0.025 * len(ks))], ks[math.ceil(0.975 * len(ks)) - 1]


def kripp(us):
    o, nc, total = {}, {}, 0.0
    for vals in us:
        mm = len(vals)
        if mm < 2:
            continue
        for i in range(mm):
            for j in range(mm):
                if i != j:
                    key = (vals[i], vals[j])
                    o[key] = o.get(key, 0) + 1 / (mm - 1)
                    total += 1 / (mm - 1)
    if not total:
        return None
    for (c, _), v in o.items():
        nc[c] = nc.get(c, 0) + v
    Do = sum(v for (c, d), v in o.items() if c != d)
    De = sum(nc[c] * nc[d] / (total - 1) for c in nc for d in nc if c != d)
    return 1 - Do / De if De > 0 else None


def band(k):
    if k is None or math.isnan(k): return "not computable"
    return ("almost perfect" if k >= .9 else "strong" if k >= .8 else "moderate" if k >= .6 else
            "weak" if k >= .4 else "minimal" if k >= .21 else "none" if k >= 0 else "worse than chance")


f3 = lambda x: "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"
pct = lambda x: f"{100 * x:.1f}%"

pairs = []
for i in range(m):
    for j in range(i + 1, m):
        pairs.append((R[i]["id"], R[j]["id"], cohen([(u[i], u[j]) for u in binu])))
if m >= 3:
    gname, gval = "Fleiss' kappa", fleiss(binu)
    ci = fleiss_ci(binu) if not math.isnan(gval) else None
    ci_txt = f"{f3(ci[0])} to {f3(ci[1])} (bootstrap, {BOOT_B} resamples, seed {BOOT_SEED})" if ci else "n/a"
else:
    gname, c = "Cohen's kappa", pairs[0][2]
    gval = c["k"]
    ci_txt = f"{f3(gval - 1.96 * c['se'])} to {f3(min(1, gval + 1.96 * c['se']))}"
all_agree = sum(len(set(u)) == 1 for u in binu) / n
keep_rate = sum(v == "include" for u in binu for v in u) / (n * m)
alpha_b, alpha_3 = kripp(binu), kripp(units)
passed = not math.isnan(gval) and gval >= THRESHOLD
split = {k: sum(1 for u in binu if u.count("include") == k) for k in range(m, -1, -1)}

lines = [
    "# Agreement report", "",
    f"Reviewers: {', '.join(r['id'] for r in R)}  ", f"Records screened by all: {n}", "",
    "| Measure | Value |", "|---|---|",
    f"| All reviewers agree (keep/discard, maybe = keep) | {pct(all_agree)} |",
    f"| **{gname}, binary** | **{f3(gval)}** ({band(gval)}) |",
    f"| 95% CI | {ci_txt} |",
    f"| Krippendorff's alpha, binary | {f3(alpha_b)} |",
    f"| Krippendorff's alpha, keep/maybe/discard | {f3(alpha_3)} |",
    *[f"| Cohen's kappa, {a} vs {b} | {f3(c['k'])} (agree {pct(c['po'])}) |" for a, b, c in pairs],
    f"| Keep rate (maybe = keep) | {pct(keep_rate)} |",
    f"| Pass mark {THRESHOLD:.2f} | {'met' if passed else 'NOT met'} |", "",
    "## How the votes split", "", "| Keep votes | Records |", "|---|---|",
    *[f"| {k} of {m} | {v} |" for k, v in split.items()], "",
    "## Each reviewer", "", "| Reviewer | Keep | Maybe | Discard |", "|---|---|---|---|",
    *[f"| {r['id']} | " + " | ".join(str(sum(r['dec'][i]['decision'] == d for i in common))
                                      for d in ("include", "maybe", "exclude")) + " |" for r in R], "",
]
os.makedirs("agreement", exist_ok=True)
open("agreement/agreement_report.md", "w", encoding="utf-8").write("\n".join(lines))

disc = [i for i, u in zip(common, units) if len(set(u)) > 1 or "maybe" in u]
with open("agreement/records_to_discuss.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["corpus_id", "title"] + [f"{r['id']} decision" for r in R] + [f"{r['id']} codes" for r in R]
               + [f"{r['id']} reason" for r in R])
    for i in disc:
        ds = [r["dec"][i] for r in R]
        w.writerow([i, ds[0].get("title", "")] + [d["decision"] for d in ds]
                   + [" ".join(d.get("codes") or []) for d in ds] + [d.get("reason", "") for d in ds])

print("\n".join(lines))
print(f"records to discuss: {len(disc)}  ->  agreement/records_to_discuss.csv")
print("report  ->  agreement/agreement_report.md")
