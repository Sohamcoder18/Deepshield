import re

with open("d:\\hackethon\\mismatches_output.txt", "rb") as f:
    content = f.read().decode("utf-16").splitlines()

mismatches = []
for line in content:
    if "size mismatch" in line or "torch.Size" in line:
        mismatches.append(line.strip())

with open("d:\\hackethon\\mismatches_summary.txt", "w") as f:
    for m in mismatches:
        f.write(m + "\n")

print(f"Extracted {len(mismatches)} mismatch lines.")
