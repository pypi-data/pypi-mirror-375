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
This file parses the ASCII output of the Diffractometer 500 XRD and saves either
an .xy or .txt file
"""

from numpy import array, concatenate, ones, savetxt

from argparse import ArgumentParser
import os.path as path
from re import findall, match, search, sub
from sys import exit


def convert(ifile, zero_bg=False, cps=False):
    """Converts ASC file to XY file
    zero_bg: zeros background
    cps    : if true, returns counts/sec, otherwise counts
    """
    asc = open(ifile, 'r')
    asc = asc.readlines()

    expr_value = r'\d+\.\d+|\d+'
    expr = {'dwell' : r'TIME=(\d+\.\d+)',
            'data'  : r'\s+',
            'end'   : r'@END',
    }

    dwell = -1
    x = []
    y = []
    counts = []
    for line in asc:
        result = {}
        for k, v in expr.items():
            result[k] = match(expr[k], line)
        if ((result['dwell'] is None)
            and (result['data'] is None)
            and (result['end'] is None)):
            continue
        elif result['dwell'] is not None:
            t = search(r'\d+.\d+', line)
            new_dwell = float(t.group(0))
            if dwell <= 0:
                dwell = new_dwell
                continue
        elif result['data'] is not None:
            a, b = findall(expr_value, line)
            x.append(float(a))
            counts.append(int(b))
            continue
        counts = array(counts)
        if (cps == True) and (dwell > 0):
            counts = counts/dwell
        y.append(counts)
        counts = []
        dwell = new_dwell

    x = array(x)
    xy = array([x, concatenate(y)])

    # Zero the background, offset by 1 for rietveld refinements
    if zero_bg == True:
        xy[1] -= min(xy[1])
        xy[1] += 1

    return xy.transpose()


def main():
    import sys

    parser = ArgumentParser()
    parser.add_argument('-f', '--file', type=str,
                         help='Ascii file to be parsed to xy',)
    parser.add_argument('-s', '--strip-date', action="store_false", default=True,
                         help="Strip date out of files")
    args = parser.parse_args()

    # If no file is passed use the Tk GUI file selector
    def func(f_list, strip_date=False):
        for filename in f_list:
            dirname = path.dirname(filename)
            basename = path.basename(filename)

            xy = convert(filename, zero_bg=True, cps=True)
            fname, ext = path.splitext(basename)
            if strip_date == True:
                #yyyy-mm-dd HH.MM.SSAM (or PM)
                expr_date = r'\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2}(AM|PM)'
                fname = sub(expr_date, '', fname)
            ofile = path.join(dirname, fname + ".xy")
            print('Writing ', ofile)
            savetxt(ofile, xy, fmt='%.5e',
                              delimiter=' ', newline='\r\n')

        print("Finished.")

    if args.file:
        func([args.file], args.strip_date)
    else:
        from tkinter import Tk
        from tkinter.filedialog import askopenfilename

        def ask_asc_files(parent: Tk, strip_date=False):
            parent.withdraw()
            chosen = askopenfilename(
                parent=parent,
                title="Select G-Pol file",
                filetypes=[("Ascii files", "*.asc")],
            )
            parent.destroy()

            if not chosen:
                print("No file selected, exiting...", file=sys.stderr)
                sys.exit(0)

            func(chosen, strip_date)

        root = Tk()
        ask_asc_files(root, strip_date=args.strip_date)


if __name__ == "__main__":
    main()
