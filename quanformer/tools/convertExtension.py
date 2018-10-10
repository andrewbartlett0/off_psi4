#!/usr/bin/env python
"""
Purpose: Convert one molecule file format into another using OpenEye tools.

Usage:   python convertExtension.py -i [file.sdf] -o [file.mol2]

By:      Victoria T. Lim
Version: Oct 10 2018

"""

import openeye.oechem as oechem

def main(**kwargs):

    # open input molecule
    ifs = oechem.oemolistream()
    if not ifs.open(args.infile):
        oechem.OEThrow.Warning("Unable to open %s for reading" % args.infile)
        return
    imol = next(ifs.GetOEMols())

    # write to output
    ofs = oechem.oemolostream()
    if not ofs.open(args.outfile):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args.outfile)
    oechem.OEWriteConstMolecule(ofs, imol)
    ifs.close()
    ofs.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--infile",
            help="Input molecule file")
    parser.add_argument("-o", "--outfile",
            help="Output molecule file")

    args = parser.parse_args()
    opt = vars(args)

    main(**opt)

