#!/usr/bin/env python

import openeye.oechem as oechem
import openeye.oedepict as oedepict
import numpy as np
from math import degrees


def genHBIndexGuide(inpmol):
    """
    For each mol, generate depiction of molecule with labeled
      indices as read in by oechem. Saved as   _____
    """
    mol = oechem.OEGraphMol(inpmol)
    dopt = oedepict.OEPrepareDepictionOptions()
    dopt.SetDepictOrientation( oedepict.OEDepictOrientation_Horizontal)
    oedepict.OEPrepareDepiction(mol, dopt)
    opts = oedepict.OE2DMolDisplayOptions(width, height, oedepict.OEScale_AutoScale)
    opts.SetAtomPropertyFunctor(oedepict.OEDisplayAtomIdx())
    oedepict.OERenderMolecule(outfn,mol)



def findIntraHB(mol):
    """
    WORDS
    
    Parameters
    ----------
    mol
    
    Returns
    -------
    Hbond_list: 2D list. Each sublist is a unique possible intra HB pair.
       Sublist is ordered by donor atom index, H atom index, acceptor index,
       Hbond distance in Angstroms, Hbond angle in degrees (sublist length 5).
    
    """
    def getAtomCoords(mol,idx):
        atom = mol.GetAtom(oechem.OEHasAtomIdx(idx)) 
        xyz = oechem.OEFloatArray(3)
        mol.GetCoords(atom, xyz)
        return np.array([xyz[0],xyz[1],xyz[2]]) 

    # .........!!!!!!!!!!!!!!!!!!!!
    # definitions of donor acceptor: 
    # https://docs.eyesopen.com/toolkits/python/molproptk/molprops_sub.html
    # how to match to donor atom
    # https://docs.eyesopen.com/toolkits/python/oechemtk/genericdata.html
    # match to atom that's N or O with at least one H attached
    IsDonorAtom = oechem.OEMatchAtom("[!H0;#7,#8]")
    IsAcceptorAtom = oechem.OEMatchAtom("[#7,#8]")

    # defaults from SetMaxHBondDistance and SetMaxDonorAngle
    # https://docs.eyesopen.com/toolkits/python/oechemtk/OEBioClasses/OEPerceiveInteractionOptions.html
    Hbond_angle_cutoff = 50.0
    Hbond_dist_cutoff = 3.2

    # Make list of H atoms, their donor atoms and possible Acceptor atoms 
    HD_atom_idx_list=[]; A_atom_idx_list=[]; HD_D_idx_dict={}   # HD means H atom bonded to Donor atom (D), A=acceptor 

    for atom in mol.GetAtoms(): 
        idx=atom.GetIdx() 
        if atom.GetAtomicNum()==1:                 # hydrogen atoms 
            for nn_atom in atom.GetAtoms():        # nn_atom=nearest neighbour atom 
                if IsDonorAtom(nn_atom):
                    HD_atom_idx_list.append(idx)        # list of H atoms bonded to D atoms 
                    HD_D_idx_dict[idx]=nn_atom.GetIdx() # dictionary of H atom idx and its D atom idx 
        if IsAcceptorAtom(atom): 
            A_atom_idx_list.append(idx)                 # list of A atoms 

    # Check distance and angle between HD and A atoms and make list of H bonds (atoms involved, angle and distance) 
    Hbond_list=[] 
    for HD_atom_idx in HD_atom_idx_list: 
        HD_atom=mol.GetAtom(oechem.OEHasAtomIdx(HD_atom_idx)) 
        D_atom_idx=HD_D_idx_dict[HD_atom_idx] 
        D_atom = mol.GetAtom(oechem.OEHasAtomIdx(D_atom_idx))
        HD_atom_coords=getAtomCoords(mol, D_atom_idx) 

        for A_atom_idx in A_atom_idx_list: 
            if A_atom_idx == D_atom_idx:        # don't consider the H atom's D atom as A atom 
                pass 
            else: 
                A_atom_coords=getAtomCoords(mol,A_atom_idx)
                A_atom = mol.GetAtom(oechem.OEHasAtomIdx(A_atom_idx))
                Hbond_angle=degrees(oechem.OEGetAngle(mol, D_atom, HD_atom, A_atom))
                Hbond_dist=np.linalg.norm(HD_atom_coords-A_atom_coords) 
                if Hbond_angle > Hbond_angle_cutoff and Hbond_dist < Hbond_dist_cutoff: 
                    Hbond_list.append([D_atom_idx, HD_atom_idx, A_atom_idx, Hbond_dist, Hbond_angle]) 

    return Hbond_list
