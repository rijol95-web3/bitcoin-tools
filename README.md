# Bitcoin Address Dataset

A high-quality collection of Bitcoin addresses split into multiple **24 MB chunks** for easier downloading, cloning, and storage.

## Dataset Information

| Property | Value |
|----------|-------|
| Network | Bitcoin (BTC) |
| Format | Plain Text (`.txt`) |
| Encoding | UTF-8 |
| One address per line | ✅ |
| Chunk Size | Maximum 24 MB |
| Total Addresses | **56,701,876** |
| Chunk Naming | `btc_addresses1.txt`, `btc_addresses2.txt`, `btc_addresses3.txt`, ... |

---

# Why is the dataset split?

GitHub works much better with smaller files than with a single multi-gigabyte file.

Instead of one very large file, this repository stores the dataset as multiple 24 MB chunks.

Advantages:

- Faster downloads
- Easier cloning
- Better Git compatibility
- Lower risk of upload failures
- Simple reconstruction into a single file

---

# Rebuild the Original File

All chunk files can be merged back into a single text file.

The script below automatically:

- reads every chunk in order
- merges them correctly
- creates one output file
- preserves every address exactly as stored

Save the script as:

```
merge_chunks.py
```

```python
from pathlib import Path
import re

INPUT_DIRECTORY = Path("btc addresses")
OUTPUT_FILE = Path("btc_addresses.txt")

BUFFER_SIZE = 1024 * 1024

number_regex = re.compile(r"(\d+)")

def natural_key(path: Path):
    m = number_regex.search(path.stem)
    return int(m.group(1)) if m else 0

files = sorted(
    INPUT_DIRECTORY.glob("btc_addresses*.txt"),
    key=natural_key,
)

with OUTPUT_FILE.open("wb") as output:
    for file in files:
        print("Merging:", file.name)

        with file.open("rb") as source:
            while True:
                chunk = source.read(BUFFER_SIZE)

                if not chunk:
                    break

                output.write(chunk)

print()
print("Done!")
print("Output:", OUTPUT_FILE.resolve())
```

---

# Folder Structure

```
Repository
│
├── btc addresses
│   ├── btc_addresses1.txt
│   ├── btc_addresses2.txt
│   ├── btc_addresses3.txt
│   └── ...
│
└── merge_chunks.py
```

---

# Usage

Run:

```bash
python merge_chunks.py
```

After completion:

```
btc_addresses.txt
```

will contain the complete dataset.

---

# Dataset Format

Each line contains exactly one Bitcoin address.

Example:

```
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy
bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080
bc1p5cyxnuxmeuwuvkwfem96l0j0r0x8n6m7n6k7r9m6h0w3xw5m4u5s4y6k8g
```

---

# Notes

- Addresses are stored exactly as collected.
- One address per line.
- No additional metadata.
- Chunk order must be preserved when rebuilding the dataset.
- The merge process is lossless.

---

# License

This repository is provided for research, educational, and blockchain analysis purposes.
