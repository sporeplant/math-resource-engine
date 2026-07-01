import pathlib
import re
import shutil

md = pathlib.Path("outputs/g8-reviews/review-10_课件.md")
text = md.read_text(encoding="utf-8")
links = re.findall(r"!\[[^\]]*\]\((images/[^)]+)\)", text)
unique = list(dict.fromkeys(links))
print("links_count", len(unique))

src = pathlib.Path("knowledge/reviews/images")
dest_dir = pathlib.Path("outputs/g8-reviews/images")
dest_dir.mkdir(parents=True, exist_ok=True)

found = []
missing = []
for link in unique:
    name = pathlib.Path(link).name
    src_file = src / name
    dest_file = dest_dir / name
    if src_file.exists():
        if not dest_file.exists():
            shutil.copy2(src_file, dest_file)
        found.append(link)
    else:
        missing.append(link)

print("found", len(found))
print("missing", len(missing))
print("---found---")
for l in found:
    print(l)
print("---missing---")
for l in missing:
    print(l)
