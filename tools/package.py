#!/usr/bin/env python3
"""
package.py <package_dir> <output_zip>
Validates the FOMOD XML files and creates the final distribution zip archive.
"""

import os
import sys
import zipfile
from xml.dom import minidom

def main():
    if len(sys.argv) < 3:
        print("Usage: package.py <package_dir> <output_zip>", file=sys.stderr)
        sys.exit(1)

    pkg_dir, out_zip = sys.argv[1:3]

    for xml_file in ("info.xml", "ModuleConfig.xml"):
        path = os.path.join(pkg_dir, "fomod", xml_file)
        if not os.path.isfile(path):
            print(f"ERROR: Missing FOMOD file: {path}", file=sys.stderr)
            sys.exit(1)
        minidom.parse(path)

    os.makedirs(os.path.dirname(os.path.abspath(out_zip)), exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(pkg_dir):
            for f in sorted(files):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, pkg_dir).replace(os.sep, "/")
                z.write(full_path, rel_path)

    print(f"Built archive: {out_zip}")
    with zipfile.ZipFile(out_zip, "r") as z:
        for i in z.infolist():
            print(f"  {i.file_size:>8} bytes  {i.filename}")

if __name__ == "__main__":
    main()
