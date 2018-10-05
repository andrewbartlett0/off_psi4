#!/usr/bin/env python
"""

Purpose: This script addresses the following problem -- You have a single molecule
with two different geometries in two separate files. However, structural alignment
is difficult since their atom indices do not correspond, i.e., the C4 of one file
is labeled as C5 in the other file.

This code reads in both geometries and aligns the second geometry to the first based
on MCS (maximum common substrcture). The second atoms in the second geometry are
reordered by referencing the corresponding atoms to the first geometry.

Reference: This code was based off the following OpenEye script-
https://docs.eyesopen.com/toolkits/python/_downloads/mcs3dalign.py

Modifications:
- Do not write out reference molecule in output file
- Generate only one single best match in alignment
- Suppress hydrogens in MCSAlign instead of in main (in order to create fit2refmol)
- Reassign indices

Caveat (and TODO):
This script is NOT a finished product. Most of the heavy atom indices do get
matched up well, but please double check as symmetry can affect the results.
The hydrogen atoms are NOT rigorously assigned--their indices are reassigned
based on their parent atoms but two hydrogens on the same *adjusted* parent atom
may not have the same ordering as the two hydrogens on the *reference* parent atom.

Version:     Oct 5 2018
Changes by:  Victoria T. Lim

"""
# (C) 2017 OpenEye Scientific Software Inc. All rights reserved.
#
# TERMS FOR USE OF SAMPLE CODE The software below ("Sample Code") is
# provided to current licensees or subscribers of OpenEye products or
# SaaS offerings (each a "Customer").
# Customer is hereby permitted to use, copy, and modify the Sample Code,
# subject to these terms. OpenEye claims no rights to Customer's
# modifications. Modification of Sample Code is at Customer's sole and
# exclusive risk. Sample Code may require Customer to have a then
# current license or subscription to the applicable OpenEye offering.
# THE SAMPLE CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED.  OPENEYE DISCLAIMS ALL WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. In no event shall OpenEye be
# liable for any damages or liability in connection with the Sample Code
# or its use.

#############################################################################
# Align two compounds based on the maximum common substructure
#############################################################################
import sys
from openeye import oechem


def MCSAlign(refmol, fitmol, ofs):

    # generate a copy of refmol bc we want refmol's indices with fitmol's coordinates
    fit2refmol = oechem.OEMol(refmol)
    # set match based on heavy atoms
    oechem.OESuppressHydrogens(refmol)

    atomexpr = oechem.OEExprOpts_AtomicNumber | oechem.OEExprOpts_Aromaticity
    bondexpr = 0
    mcss = oechem.OEMCSSearch(oechem.OEMCSType_Exhaustive)
    mcss.Init(refmol, atomexpr, bondexpr)
    mcss.SetMCSFunc(oechem.OEMCSMaxBondsCompleteCycles())
    mcss.SetMaxMatches(1)

    rmat = oechem.OEDoubleArray(9)
    trans = oechem.OEDoubleArray(3)
    unique = True
    overlay = True


    for match in mcss.Match(fitmol, unique): ## This should be a loop of one but when I call match.next() I get a segfault later on
        rms = oechem.OERMSD(mcss.GetPattern(), fitmol, match, overlay, rmat, trans)
        if rms < 0.0:
            oechem.OEThrow.Warning("RMS overlay failure")
            return
        oechem.OERotate(fitmol, rmat)
        oechem.OETranslate(fitmol, trans)

        print("pattern atoms:", end=" ")
        for ma in match.GetAtoms():
            print(ma.pattern.GetIdx(), end=" ")

        print("target atoms:", end=" ")
        for ma in match.GetAtoms():
            print(ma.target.GetIdx(), end=" ")

        # set fitmol's coords into fit2refmol
        for ma in match.GetAtoms():
            # get indices
            ref_idx = ma.pattern.GetIdx()
            tar_idx = ma.target.GetIdx()
            # get atoms
            f2r_atom = fit2refmol.GetAtom(oechem.OEHasAtomIdx(ref_idx))
            tar_atom = fitmol.GetAtom(oechem.OEHasAtomIdx(tar_idx))
            # get coords from fitmol and set on fit2refmol
            tar_crds = fitmol.GetCoords(tar_atom)
            fit2refmol.SetCoords(f2r_atom, tar_crds)
            # reassign hydrogens
            tar_hyds = list(tar_atom.GetAtoms(oechem.OEHasAtomicNum(oechem.OEElemNo_H)))
            for i, nn_atom in enumerate(f2r_atom.GetAtoms(oechem.OEHasAtomicNum(oechem.OEElemNo_H))):
                # get hydrogen coords from fitmol and set on fit2refmol
                tar_crds = fitmol.GetCoords(tar_hyds[i])
                fit2refmol.SetCoords(nn_atom, tar_crds)

        oechem.OEWriteMolecule(ofs, fit2refmol)


def main(argv=[__name__]):
    if len(argv) != 4:
        oechem.OEThrow.Usage("%s <refmol> <fitmol> <outfile>" % argv[0])

    reffs = oechem.oemolistream()
    if not reffs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    if not oechem.OEIs3DFormat(reffs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid input format: need 3D coordinates")
    refmol = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(reffs, refmol):
        oechem.OEThrow.Fatal("Unable to read molecule in %s" % argv[1])
    if not refmol.GetDimension() == 3:
        oechem.OEThrow.Fatal("%s doesn't have 3D coordinates" % refmol.GetTitle())

    fitfs = oechem.oemolistream()
    if not fitfs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])
    if not oechem.OEIs3DFormat(fitfs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid input format: need 3D coordinates")

    ofs = oechem.oemolostream()
    if not ofs.open(argv[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % argv[3])
    if not oechem.OEIs3DFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid output format: need 3D coordinates")

#    oechem.OEWriteConstMolecule(ofs, refmol)

    for fitmol in fitfs.GetOEGraphMols():
        if not fitmol.GetDimension() == 3:
            oechem.OEThrow.Warning("%s doesn't have 3D coordinates" % fitmol.GetTitle())
            continue
        MCSAlign(refmol, fitmol, ofs)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
