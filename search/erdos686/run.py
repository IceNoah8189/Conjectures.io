#!/usr/bin/env python3
"""Resumable parallel driver for the Erdős 686 (ratio 25) witness search.

Plan: small k (most plausible) searched furthest. Work is split into chunks;
finished chunks are recorded in done.txt so the run can be restarted safely.
Every HIT is verified exactly; verified witnesses go to WITNESSES.txt.
"""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from math import prod

HERE = os.path.dirname(os.path.abspath(__file__))
R = 25
WORKERS = int(os.environ.get("WORKERS", "6"))
CHUNK = 1_000_000_000

# (k range, n bound)
PLAN = [((3, 3), 300_000_000_000),
        ((4, 6), 100_000_000_000),
        ((7, 20), 10_000_000_000),
        ((21, 100), 1_000_000_000)]

done_path = os.path.join(HERE, "done.txt")
wit_path = os.path.join(HERE, "WITNESSES.txt")
log_path = os.path.join(HERE, "hits.log")


def jobs():
    out = []
    for (k0, k1), bound in PLAN:
        for k in range(k0, k1 + 1):
            for a in range(0, bound, CHUNK):
                out.append((k, a, min(a + CHUNK - 1, bound)))
    # interleave so every k gets coverage early: order by start, then k
    out.sort(key=lambda j: (j[1], j[0]))
    return out


def verify(k, n, m):
    return k >= 2 and m >= n + k and \
        prod(m + i for i in range(1, k + 1)) == R * prod(n + i for i in range(1, k + 1))


def run(job):
    k, a, b = job
    p = subprocess.run([os.path.join(HERE, "search"), str(R), str(k), str(a), str(b)],
                       capture_output=True, text=True)
    if p.returncode != 0 or "DONE" not in p.stderr:
        raise RuntimeError(f"job {job} failed: {p.stderr[-300:]}")
    hits = []
    for line in p.stdout.splitlines():
        parts = line.split()
        if parts and parts[0] == "HIT":
            _, _, kk, n, m = map(int, parts)
            hits.append((kk, n, m, verify(kk, n, m)))
    return job, hits


def main():
    done = set()
    if os.path.exists(done_path):
        done = {tuple(map(int, l.split())) for l in open(done_path) if l.strip()}
    todo = [j for j in jobs() if j not in done]
    total = len(jobs())
    print(f"Erdős 686, ratio {R}: {len(done)}/{total} chunks already done, {len(todo)} to go, {WORKERS} workers.")
    print("Searching for (m+1)...(m+k) = 25*(n+1)...(n+k) with k>=2, m>=n+k.\n", flush=True)
    t0 = time.time()
    finished = 0
    with ThreadPoolExecutor(WORKERS) as ex:
        futs = [ex.submit(run, j) for j in todo]
        for f in as_completed(futs):
            (k, a, b), hits = f.result()
            for kk, n, m, ok in hits:
                with open(log_path, "a") as fh:
                    fh.write(f"{'VERIFIED' if ok else 'false-positive'} k={kk} n={n} m={m}\n")
                if ok:
                    with open(wit_path, "a") as fh:
                        fh.write(f"k={kk} n={n} m={m}\n")
                    print("\n" + "!" * 70 + f"\n  WITNESS FOUND: k={kk} n={n} m={m}\n" + "!" * 70 + "\n", flush=True)
            with open(done_path, "a") as fh:
                fh.write(f"{k} {a} {b}\n")
            finished += 1
            el = time.time() - t0
            eta = el / finished * (len(todo) - finished)
            print(f"[{time.strftime('%H:%M')}] k={k:3d} n={a:,}..{b:,} done  "
                  f"({len(done) + finished}/{total}, ~{eta / 3600:.1f} h left)", flush=True)
    print("\nSearch plan complete.", "Witnesses: see WITNESSES.txt" if os.path.exists(wit_path) else "No witness found.")


if __name__ == "__main__":
    main()
