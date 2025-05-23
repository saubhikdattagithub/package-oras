#!/usr/bin/env python3
import subprocess
import re
import sys
from pathlib import Path
import os
from datetime import datetime
import shutil

PREPARE_SOURCE = Path("prepare_source")
PKGNAME='oras'
DATE=datetime.now()
NOW=DATE.strftime("%a, %d %b %Y %H:%M:%S +0000")


def run_uscan_report():
    try:
        output_path=(f"debian/changelog")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        text = f"""{PKGNAME} ({current_version}) unstable; urgency=medium

  * Initial release.

 -- Garden Linux <gardenlinux@example.com>  Thu, 22 May 2025 12:00:00 +0000
            """
        with open(output_path, "w") as f:
            f.write(text)
        result = subprocess.run(
            ["uscan", "--report", "--watch", "watch"],
            capture_output=True,
            text=True,
            check=True
        )
        shutil.rmtree("debian")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("uscan failed:", e.stderr, file=sys.stderr)
        sys.exit(1)

def extract_new_version(report):
    match = re.search(r"Newest version of oras on remote site is ([\d\.]+)", report)
    if match:
        return match.group(1)
    return None

def read_current_version():
    with open(PREPARE_SOURCE) as f:
        for line in f:
            if line.startswith("version_orig="):
                return line.strip().split("=")[1].split("-")[0].strip('"')


def update_prepare_source(file_path: Path, old :str , new: str):
    content = file_path.read_text()
    updated_content = content.replace(old, new)
    file_path.write_text(updated_content)
    #print(f"Replaced all occurrences of '{old}' with '{new}' in {file_path}")


def main():
    global current_version 
    current_version = read_current_version()
    report = run_uscan_report()
    #print(f"Output of uscan", report)
    new_version = extract_new_version(report)
    if not new_version:
        print("No new version found.")
        sys.exit(0)

    if current_version == new_version:
        print(f"No update needed: version is already {current_version}")
        sys.exit(0)

    #print(f"Updating version from {current_version} to {new_version}")
    update_prepare_source(PREPARE_SOURCE, current_version , new_version)
    print(new_version)
#update_prepare_source(new_version)

if __name__ == "__main__":
    main()
