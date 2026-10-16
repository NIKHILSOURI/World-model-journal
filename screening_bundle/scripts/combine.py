"""Combine all title and abstract decisions into the list that goes to full-text screening.

Run from the bundle folder when the agreement round is settled and all three batches are screened:
    python scripts/combine.py

Reads   agreement/adjudicated_agreement_sample.json   (Resolve tab export)
        screening/screened_batch*_*.json               (one per reviewer, Screening phase)
        screening/assignment.csv, corpus/Deduplicated_corpus_662_records.ris
Writes  fulltext/title_abstract_decisions.csv          (every record, its final decision and who decided)
        fulltext/fulltext_candidates_<n>.ris           (the records kept, for full-text screening)
Only the Python standard library is used.
"""
import csv, glob, json, os, re, sys

CORPUS = "corpus/Deduplicated_corpus_662_records.ris"


def read_ris(path):
    recs, lines = {}, []
    for line in open(path, encoding="utf-8-sig"):
        lines.append(line.rstrip("\r\n"))
        if re.match(r"^ER  -", line):
            text = "\n".join(l for l in lines if l.strip()) + "\n"
            rid = next((l[6:].strip() for l in lines if l.startswith("ID  -")), "")
            ti = next((l[6:].strip() for l in lines if l.startswith("TI  -")), "")
            py = next((l[6:].strip() for l in lines if l.startswith("PY  -")), "")
            recs[rid] = dict(text=text, title=ti, year=py)
            lines = []
    return recs


corpus = read_ris(CORPUS)
assign = {r["id"]: int(r["screener"]) for r in csv.DictReader(open("screening/assignment.csv", encoding="utf-8"))}
sample_ids = [r["id"] for r in csv.DictReader(open("agreement/agreement_sample.csv", encoding="utf-8"))]
problems = []

# ---- agreement sample: settled decisions
final, how = {}, {}
adj_path = "agreement/adjudicated_agreement_sample.json"
if not os.path.exists(adj_path):
    sys.exit(f"Missing {adj_path}. Export it from the Resolve tab first.")
adj = json.load(open(adj_path, encoding="utf-8"))
for x in adj.get("agreed", []):
    final[x["corpus_id"]], how[x["corpus_id"]] = x["final"], "agreement round: all agreed"
for x in adj.get("records", []):
    final[x["corpus_id"]], how[x["corpus_id"]] = x["final"], "agreement round: settled by discussion"
missing = [i for i in sample_ids if i not in final]
if missing:
    problems.append(f"{len(missing)} agreement-sample record(s) have no settled decision: {', '.join(missing[:8])}")

# ---- batches: one reviewer each
seen_batches = {}
for path in sorted(glob.glob("screening/screened_batch*_*.json")):
    d = json.load(open(path, encoding="utf-8"))
    slot = d.get("reviewer_slot")
    if slot in seen_batches:
        problems.append(f"two files for batch {slot}: {seen_batches[slot]} and {path}")
    seen_batches[slot] = path
    for x in d.get("decisions", []):
        i = x["corpus_id"]
        if assign.get(i) != slot:
            problems.append(f"{i} in {os.path.basename(path)} is not in batch {slot}")
            continue
        dec = "exclude" if x["decision"] == "exclude" else "include"   # a stray maybe goes on to full text
        final[i], how[i] = dec, f"batch {slot}: {d.get('reviewer_id', '')}"
for s in (1, 2, 3):
    if s not in seen_batches:
        problems.append(f"no screening file for batch {s} (screening/screened_batch{s}_<initials>.json)")
undecided = [i for i in corpus if i not in final]
if undecided:
    problems.append(f"{len(undecided)} record(s) still have no decision, e.g. {', '.join(undecided[:8])}")

# ---- write
os.makedirs("fulltext", exist_ok=True)
with open("fulltext/title_abstract_decisions.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["corpus_id", "title", "year", "stage", "final_decision", "decided_by"])
    for i, r in corpus.items():
        stage = "agreement sample" if i in set(sample_ids) else f"batch {assign.get(i, '?')}"
        w.writerow([i, r["title"], r["year"], stage, final.get(i, "MISSING"), how.get(i, "")])
keep = [i for i in corpus if final.get(i) == "include"]
out = f"fulltext/fulltext_candidates_{len(keep)}.ris"
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    for i in keep:
        fh.write(corpus[i]["text"] + "\n")

screened = sum(1 for i in corpus if i in final)
print(f"records screened on title and abstract: {screened} of {len(corpus)}")
print(f"excluded at title and abstract:         {sum(1 for i in corpus if final.get(i) == 'exclude')}")
print(f"kept for full-text screening:           {len(keep)}  ->  {out}")
print("all decisions                          ->  fulltext/title_abstract_decisions.csv")
if problems:
    print("\nCHECK BEFORE REPORTING:")
    for p in problems:
        print("  -", p)
