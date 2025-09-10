#!/usr/bin/env python3
#-
# Copyright (c) 2025, David Kalliecharan <david@goosegrid.ca>
# All rights reserved. 
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are 
# met: 
# 
#  * Redistributions of source code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer. 
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.  

"""
Read a MAX3D *.gpol file (2‑D pole figure) and return a NumPy array.
"""

import re
import numpy as np
from pathlib import Path

HEADER_BLOCK_SIZE = 512  # bytes per block (fixed for MAX3D)


def _parse_key_value(line: str):
    """
    Turn a line like "NROWS  :512" into ("nrows", "512").
    """
    # Remove leading/trailing whitespace and split on colon
    parts = line.strip().split(":")
    if len(parts) < 2:
        return None, None
    key = parts[0].strip().lower()
    # Some lines have extra spaces before the value; collapse them
    value = ":".join(parts[1:]).strip()
    return key, value


def split_header_blob(blob: str) -> dict:
    """
    Convert the single‑string header (blob) into a dict.
    All keys are lower‑cased, values are stripped of surrounding whitespace.

    This is necessary because the `meta['format']` tag is one giant string blob.
    """
    # Pattern:
    #   (\w+)          – the key (letters, numbers, underscore)
    #   \s*:\s*        – optional spaces, a colon, optional spaces
    #   ([^:]+?)       – the value (everything up to the next colon)
    #   (?=\s*\w+\s*:|$) – look‑ahead for the next “KEY :” or end‑of‑string
    token_pat = re.compile(r"(\w+)\s*:\s*([^:]+?)(?=\s*\w+\s*:|$)")

    meta = {}
    for m in token_pat.finditer(blob):
        key   = m.group(1).lower()
        value = m.group(2).strip()
        meta[key] = value
    return meta


def read_gpol_header(fp):
    """
    Reads the ASCII header (up to HDRBLKS*512 bytes) and returns a dict.
    """
    # Peek at the first block to locate the HDRBLKS field (it’s early in the file)
    first_block = fp.read(HEADER_BLOCK_SIZE).decode("ascii", errors="ignore")
    hdrblks_match = re.search(r"HDRBLKS\s*:\s*(\d+)", first_block)
    if not hdrblks_match:
        raise RuntimeError("Could not find HDRBLKS in the header.")
    hdrblks = int(hdrblks_match.group(1))

    # Go back to start and read the full header
    fp.seek(0)
    header_bytes = fp.read(hdrblks * HEADER_BLOCK_SIZE)
    header_text = header_bytes.decode("ascii", errors="ignore")

    meta = {}
    for line in header_text.splitlines():
        key, val = _parse_key_value(line)
        if key:
            meta[key] = val
    meta = split_header_blob(meta['format'])
    meta["hdrblks"] = hdrblks
    
    return meta


def load_gpol(filepath: str):
    """
    Returns (image_array, metadata_dict).
    """
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(p)

    with p.open("rb") as f:
        meta = read_gpol_header(f)

        # Pull out the essential numeric fields
        nrows = int(meta.get("nrows"))
        ncols = int(meta.get("ncols"))
        nbytes_per_pixel = int(meta.get("npixelb"))   # 2 or 4
        wordord = int(meta.get("wordord", 0))        # 0 = little‑endian
        longord = int(meta.get("longord", 0))        # rarely needed

        # Determine dtype & endianness
        if nbytes_per_pixel == 2:
            dtype = np.dtype("<u2") if wordord == 0 else np.dtype(">u2")
        elif nbytes_per_pixel == 4:
            dtype = np.dtype("<f4") if wordord == 0 else np.dtype(">f4")
        else:
            raise RuntimeError(f"Unsupported pixel size: {nbytes_per_pixel}")

        # Jump to the start of the binary image data
        offset = meta["hdrblks"] * HEADER_BLOCK_SIZE
        f.seek(offset)

        # Read the raw bytes and reshape
        count = nrows * ncols
        raw = np.frombuffer(f.read(count * nbytes_per_pixel), dtype=dtype)
        img = raw.reshape((nrows, ncols))   # rows first (Y), then columns (X)

    return img, meta


# View plot
def main():
    from argparse import ArgumentParser
    import matplotlib.pyplot as plt
    import sys

    parser = ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="G-POL 2D X-ray file (*.gpol)")
    args = parser.parse_args()

    def func(filepath: str):
        img, meta = load_gpol(filepath)
        print("Metadata of interest:")
        for k in ["nrows", "ncols", "npixelb", "wordord", "hdrblks"]:
            print(f"  {k.upper():<8}: {meta.get(k)}")

        plt.figure(figsize=(5, 5))
        plt.imshow(img, cmap="viridis", origin="lower")
        plt.title("MAX3D pole‑figure (gpol)")
        plt.xlabel("Pixel X")
        plt.ylabel("Pixel Y")
        plt.colorbar(label="Counts")
        plt.tight_layout()
        plt.show()


    if args.file:
        func(args.file)
    else:
        from tkinter import Tk
        from tkinter.filedialog import askopenfilename

        def ask_gpol_file(parent: Tk):
            parent.withdraw()
            chosen = askopenfilename(
                parent=parent,
                title="Select G-Pol file",
                filetypes=[("G-Pol files", "*.gpol")],
            )
            parent.destroy()

            if not chosen:
                print("No file selected, exiting...", file=sys.stderr)
                sys.exit(0)

            func(chosen)

        root = Tk()
        ask_gpol_file(root)


if __name__ == "__main__":
    main()
