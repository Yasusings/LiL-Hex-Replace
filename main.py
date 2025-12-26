import re
import sys
import pathlib
import argparse

# Thank you Selebus for making all the hex blobs spaced out so it's easier to pattern match
HEX_PATTERN = re.compile(r'"(?=\s*[^#])\s*([0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2}){1,})\s*"')

def get_rpy_files(root: pathlib.Path):
    return (p for p in root.rglob("*.rpy") if p.is_file())

def hex_to_text(raw_hex: str, encoding: str = "utf-8") -> str:
    cleaned = "".join(raw_hex.split())

    if len(cleaned) % 2 != 0:
        return ""
    try:
        raw_bytes = bytes.fromhex(cleaned)
        decoded = raw_bytes.decode(encoding, errors="replace")
    except ValueError:
        return ""

    spaced_decoded = " ".join(list(decoded))
    return spaced_decoded

def replace(match: re.Match) -> str:
        raw_hex = match.group(1)
        translated = hex_to_text(raw_hex)

        return f'"{translated}"'

def process_rpy_file(file_path: pathlib.Path) -> None:
    try:
        original_text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"Could not read {file_path}: {exc}", file=sys.stderr)
        return
    
    new_text, count = HEX_PATTERN.subn(replace, original_text)
    if count == 0:
        return

    try:
        file_path.write_text(new_text, encoding="utf-8")
        print(f"Updated {file_path} ({count} replacement{'s' if count != 1 else ''})")
    except OSError as exc:
        print(f"Could not write {file_path}: {exc}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=pathlib.Path, help="LiL game directory path")
    args = parser.parse_args()

    if not args.directory.is_dir():
        parser.error(f"Argument 'directory' '{args.directory}' is not a directory.")

    for rpy_file in get_rpy_files(args.directory):
        process_rpy_file(rpy_file)

    return 0

if __name__ == "__main__":
    sys.exit(main())
