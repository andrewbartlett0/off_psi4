#!/usr/bin/env python

## By: Victoria T. Lim

## This script parses output of Psi4 calculations and writes data in SD tags.
## Usage: import procTags as pt, then call pt.SetOptSDTags(args)

import openeye.oechem as oechem
import sys


def GetSDList(mol, prop, Package='Psi4', Method=None, Basisset=None):
    """
    Get list of specified SD tag for all confs in mol.

    Parameters
    ----------
    mol:        OEChem molecule with all of its conformers
    prop:       string description of property of interest
        options implemented: "QM opt energy" "MM opt energy"
    Package:    software package used for QM calculation. Psi4 or Turbomole.
    Method:     string, for specific properties. e.g. 'mp2'
    Basisset:   string, for specific properties. e.g. '6-31+G(d)'

    Returns
    -------
    sdlist: A 1D N-length list for N conformers with property from SDTag.
    """

    if prop=="QM opt energy":
        taglabel = "QM %s Final Opt. Energy (Har) %s/%s" % (Package, Method, Basisset)

    if prop=="QM opt energy initial":
        taglabel = "QM %s Initial Opt. Energy (Har) %s/%s" % (Package, Method, Basisset)

    if prop=="QM spe":
        taglabel = "QM %s Single Pt. Energy (Har) %s/%s" % (Package, Method, Basisset)

    if prop=="MM opt energy":
        taglabel = "MM Szybki Newton Energy"

    if prop=="original index":
        taglabel = "Original omega conformer number"

    if prop=="opt runtime":
        taglabel = "QM %s Opt. Runtime (sec) %s/%s" % (Package, Method, Basisset)

    if prop=="spe runtime":
        taglabel = "QM %s Single Pt. Runtime (sec) %s/%s" % (Package, Method, Basisset)

    if prop=="opt step":
        taglabel = "QM %s Opt. Steps %s/%s" % (Package, Method, Basisset)

    try: taglabel
    except UnboundLocalError as e: sys.exit("Error in input tag of extracting SD data.")

    SDList = []
    for j, conf in enumerate( mol.GetConfs() ):
        for x in oechem.OEGetSDDataPairs(conf):
            #dir(x) yields ['GetTag', 'GetValue', 'SetTag', 'SetValue', '__class__', '__del__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__swig_destroy__', '__weakref__', '_itr', 'this', 'thisown']

            # Case: opt did not finish --> append nan
            if "Note on opt." in x.GetTag() and "DID NOT FINISH" in x.GetValue():
                SDList.append('nan')
                break
            # Case: want energy value
            # Case: want original index number
            elif taglabel.lower() in x.GetTag().lower():
                SDList.append(x.GetValue())
                break
    return SDList


def SetOptSDTags(Conf, Props, spe=False):
    """
    For one particular conformer, set all available SD tags based on data
        in Props dictionary.
    TODO: what happens if the tag already exists? Is it bypassed? Overwritten?

    Parameters
    ----------
    Conf:       Single conformer from OEChem molecule
    Props:      Dictionary output from ProcessOutput function.
                Should contain the keys: basis, method, numSteps,
                initEnergy, finalEnergy, coords, time, pkg
    spe:        Boolean - are the results of a single point energy calcn?

    """

    # get level of theory for setting SD tags
    method = Props['method']
    basisset = Props['basis']
    pkg = Props['package']

    # check that finalEnergy is there. if not, opt probably did not finish
    # make a note of that in SD tag
    if not 'finalEnergy' in Props:
        if not spe: oechem.OEAddSDData(Conf, "Note on opt. %s/%s" \
 % (method, basisset), "JOB DID NOT FINISH")
        else: oechem.OEAddSDData(Conf, "Note on SPE %s/%s"\
 % (method, basisset), "JOB DID NOT FINISH")
        return

    # Set new SD tag for conformer's final energy
    if not spe: taglabel = "QM %s Final Opt. Energy (Har) %s/%s" % (pkg, method, basisset)
    else: taglabel = "QM %s Single Pt. Energy (Har) %s/%s" % (pkg, method, basisset)
    oechem.OEAddSDData(Conf, taglabel, str(Props['finalEnergy']))

    # Set new SD tag for wall-clock time
    if not spe: taglabel = "QM %s Opt. Runtime (sec) %s/%s" % (pkg, method, basisset)
    else: taglabel = "QM %s Single Pt. Runtime (sec) %s/%s" % (pkg, method, basisset)
    oechem.OEAddSDData(Conf, taglabel, str(Props['time']))

    if spe: return # stop here if SPE

    # Set new SD tag for original conformer number
    # !! Opt2 files should ALREADY have this !! Opt2 index is NOT orig index!
    taglabel = "Original omega conformer number"
    if not oechem.OEHasSDData(Conf, taglabel): # add new tag if not existing
        try:
            oechem.OEAddSDData(Conf, taglabel, str(Conf.GetIdx()+1))
        except AttributeError as err:
            pass  # if not working with confs, will have no GetIdx
    else: # if tag exists, append to it
        try:
            oldid = oechem.OEGetSDData(Conf, taglabel)
            newid = str(Conf.GetIdx()+1)
            totid = "{}, {}".format(oldid,newid)
            oechem.OESetSDData(Conf, taglabel, totid)
        except AttributeError as err:
            pass  # if not working with confs, will have no GetIdx

    # Set new SD tag for numSteps of geom. opt.
    taglabel = "QM %s Opt. Steps %s/%s" % (pkg, method, basisset)
    oechem.OEAddSDData(Conf, taglabel, str(Props['numSteps']))

    # Set new SD tag for conformer's initial energy
    taglabel = "QM %s Initial Opt. Energy (Har) %s/%s" % (pkg, method, basisset)
    oechem.OEAddSDData(Conf, taglabel, str(Props['initEnergy']))


def DeleteTag(mol,tag):
    """
    Delete specified SD tag from all conformers of mol.

    Parameters
    ----------
    mol:        OEChem molecule with all of its conformers
    tag:        exact string label of the data to delete

    """
    for j, conf in enumerate( mol.GetConfs() ):
        oechem.OEDeleteSDData(conf, tag)
