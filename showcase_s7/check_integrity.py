import re, os, sys
base = "/storage/roatienza.github.io/showcase_s7"
html = open(os.path.join(base, "index.html")).read()
refs = sorted(set(re.findall(r'audio/[A-Za-z0-9_.-]+', html)))
missing = [r for r in refs if not os.path.isfile(os.path.join(base, r))]
have = sorted(os.listdir(os.path.join(base, "audio")))
print(f"refs={len(refs)} files_on_disk={len(have)} missing={len(missing)}")
for m in missing:
    print("MISSING:", m)
# orphans: files on disk not referenced
refnames = set(os.path.basename(r) for r in refs)
orphans = [f for f in have if f not in refnames]
print(f"orphans={len(orphans)}")
for o in orphans[:20]:
    print("ORPHAN:", o)
# data-set values
sets = sorted(set(re.findall(r'data-set="([^"]+)"', html)))
print("sets:", sets)
# per-set row counts
for s in sets:
    print(s, html.count(f'data-set="{s}"'))