"""Draw the agreement sample and split the rest of the corpus into one batch per reviewer.

Run from the bundle folder:
    python scripts/draw_sample.py
    python scripts/draw_sample.py --fraction 0.10 --seed 20261016     # a 10% sample instead

Every reviewer screens the agreement sample. The records left over are shuffled and dealt
into one batch per reviewer. The same seed always gives the same sample and batches, so
report the seed and fraction in the methods. Only the Python standard library is used.
"""
import argparse, csv, math, os, random, re

p = argparse.ArgumentParser()
p.add_argument("--corpus", default="corpus/Deduplicated_corpus_662_records.ris")
p.add_argument("--fraction", type=float, default=0.20)
p.add_argument("--seed", type=int, default=20261016)
p.add_argument("--names", default="Nikhil,Tarun,Sameen", help="reviewers R1,R2,R3 in order")
p.add_argument("--out", default=".")
a = p.parse_args()
names = [x.strip() for x in a.names.split(",") if x.strip()]


def read_ris(path):
    """Return a list of (record_text, fields) with record_text kept exactly as written."""
    recs, lines = [], []
    for line in open(path, encoding="utf-8-sig"):
        lines.append(line.rstrip("\r\n"))
        if re.match(r"^ER  -", line):
            text = "\n".join(l for l in lines if l.strip()) + "\n"
            fields = {}
            for l in lines:
                m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", l)
                if m:
                    fields.setdefault(m.group(1), []).append(m.group(2).strip())
            recs.append((text, fields))
            lines = []
    return recs


def first(f, tag):
    return (f.get(tag) or [""])[0]


def found_in(f):
    for n in f.get("N1", []):
        if n.startswith("Found in:"):
            return n.split(":", 1)[1].strip()
    return first(f, "DB")


def write_ris(path, recs):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for text, _ in recs:
            fh.write(text + "\n")


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


recs = read_ris(a.corpus)
ids = [first(f, "ID") for _, f in recs]
assert all(ids) and len(set(ids)) == len(ids), "every record needs a unique ID tag"
n = len(recs)
k = math.ceil(a.fraction * n)

rng = random.Random(a.seed)
sample_idx = rng.sample(range(n), k)                 # random order = screening order
rest_idx = [i for i in range(n) if i not in set(sample_idx)]
rng.shuffle(rest_idx)
batches = [rest_idx[r::len(names)] for r in range(len(names))]

os.makedirs(os.path.join(a.out, "agreement"), exist_ok=True)
os.makedirs(os.path.join(a.out, "screening"), exist_ok=True)
write_ris(os.path.join(a.out, "agreement", f"agreement_sample_{k}.ris"), [recs[i] for i in sample_idx])
write_csv(os.path.join(a.out, "agreement", "agreement_sample.csv"),
          ["order", "id", "title", "year", "found_in"],
          [[o + 1, ids[i], first(recs[i][1], "TI"), first(recs[i][1], "PY"), found_in(recs[i][1])]
           for o, i in enumerate(sample_idx)])
rows = []
for r, b in enumerate(batches, 1):
    write_ris(os.path.join(a.out, "screening", f"screener_{r}.ris"), [recs[i] for i in b])
    rows += [[ids[i], r, names[r - 1], o + 1, first(recs[i][1], "TI"), first(recs[i][1], "PY"), found_in(recs[i][1])]
             for o, i in enumerate(b)]
write_csv(os.path.join(a.out, "screening", "assignment.csv"),
          ["id", "screener", "reviewer", "order", "title", "year", "found_in"], rows)

print(f"corpus: {n} records | seed {a.seed} | fraction {a.fraction:.0%}")
print(f"agreement sample: {k} records (every reviewer screens all of them)")
for r, b in enumerate(batches, 1):
    print(f"screener_{r}.ris: {len(b)} records -> {names[r - 1]} (R{r})")
