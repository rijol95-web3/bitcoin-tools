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
