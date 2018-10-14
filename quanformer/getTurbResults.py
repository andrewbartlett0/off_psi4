#!/usr/bin/env python

## Description: Summarize results from Turbomole set of calculations into single SDF file.
## !! Must manually set cosmo=True to get these values (!!) If set to True but is actually false is ok, just wastes time.

## TODO: make cosmo boolean a command line arg?
## TODO: get SPE results

import os
import argparse
import datetime
import openeye.oechem as oechem
import subprocess as sp
import procTags as pt

### ------------------- Functions -------------------


def GetTime():
    """
    Subtract time from beginning of job.start and job.last files.

    Returns
    -------
    time: float of wall-clock time in seconds

    """
    if not (os.path.exists("job.start") and os.path.exists("job.last")):
        print("job.start or job.last file missing. Appending -1.")
        return -1.
    fp = open("job.start")
    for i, line in enumerate(fp):
        if i == 1:
            init = line.strip()
        elif i > 1:
            break
    fp.close()

    fp = open("job.last")
    for i, line in enumerate(fp):
        if i == 2:
            final = line.strip()
        elif i > 2:
            break
    fp.close()

    d1 = datetime.datetime.strptime(init, "%a %b %d %H:%M:%S %Z %Y")
    d2 = datetime.datetime.strptime(final, "%a %b %d %H:%M:%S %Z %Y")
    dtime = (d2-d1).total_seconds()
    return dtime

def process_turb_out(Props, spe, cosmo):
    """

    TO BE UPDATED

    Go through output file and get level of theory (method and basis set),
        number of optimization steps, initial and final energies, and
        optimized coordinates. Returns all this information in a dictionary
        that was passed to this function.

    Relevant Turbomole output files:
     * GEO_OPT_CONVERGED or GEO_OPT_FAILED
     * job.last

    Parameters
    ----------
    Props: dictionary where all the data will go. Can be empty or not.
    spe: Boolean - are the Psi4 results of a single point energy calcn?

    Returns
    -------
    Props: dictionary with summarized data from output file.
           keys are: basis, method, numSteps, initEnergy, finalEnergy, coords
           ocEnergy is included if cosmo=True for implicit solvent calculation

    """
    if os.path.exists('GEO_OPT_FAILED'):
        print("Optimization failed, not gathering results")
        return Props

    try:
        f = open("energy","r")
    except IOError:
        print("No 'energy' file found in directory of %s" % os.getcwd() )
        return Props


    rough = []
    coords = []
    lines = f.readlines()

    initEnergy = lines[1].split()[1]
    finalEnergy = lines[-2].split()[1]
    numSteps = len(lines)-2
    Props['initEnergy'] = initEnergy
    Props['finalEnergy'] = finalEnergy
    Props['numSteps'] = numSteps
    f.close()

    if not cosmo:
        return Props

    # check if there's an outlying charge corrected value in job.last for COSMO
    try:
        f = open("job.last","r")
    except IOError:
        print("No 'job.last' file found in directory of %s" % os.getcwd() )
        return Props
    # reading in whole file not is not the most efficient
    for line in reversed(list(f)):
        if "Total energy + OC corr." in line:
            Props['ocEnergy'] = line.split()[-1]
    f.close()

    return Props


### ------------------- Script -------------------

def getTurbResults(origsdf, theory, finsdf, spe=False):
    """

    """
    wdir = os.getcwd()
    p = sp.call('module load turbomole/7.1/intel', shell=True)

    method = theory.split('/')[0]
    basisset = theory.split('/')[1]

    ### Read in .sdf file and distinguish each molecule's conformers
    ifs = oechem.oemolistream()
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    if not ifs.open(origsdf):
        oechem.OEThrow.Warning("Unable to open %s for reading" % origsdf)
        return

    ### Open outstream file.
    writeout = os.path.join(wdir,finsdf)
    write_ofs = oechem.oemolostream()
    if os.path.exists(writeout):
        print("File already exists: %s. Skip getting results.\n" % (finsdf))
        return (None, None)
    if not write_ofs.open(writeout):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % writeout)

    for mol in ifs.GetOEMols():
        print("===== %s =====" % (mol.GetTitle()))
        for i, conf in enumerate( mol.GetConfs()):
            props = {} # dictionary of data for this conformer
            props['package'] = "Turbomole"
            props['method'] = method
            props['basis'] = basisset

            # change into subdirectory
            subdir = os.path.join(wdir,"%s/%s" % (mol.GetTitle(), i+1))
            if not os.path.isdir(subdir):
                sys.exit("No subdirectories found, are you in the right dir?")
            os.chdir(subdir)

            # get time and final coordinates
            props['time'] = GetTime()
            if not os.path.exists('coord'):
                print("Error: the 'coord' file does not exist!")
                continue
            p=sp.Popen('t2x -c > final.xyz',shell=True)
            p.wait()

            # read in xyz file into another mol and transfer coords
            xfs = oechem.oemolistream()
            xfs.SetConfTest( oechem.OEAbsoluteConfTest() )
            if xfs.open('final.xyz'):
                xmol = next(xfs.GetOEMols())
                conf.SetCoords(xmol.GetCoords())
            else:
                oechem.OEThrow.Warning("Unable to open 'final.xyz' for reading")
            xfs.close()

            # process output and get dictionary results
            props = process_turb_out(props, spe, cosmo)
            pt.SetSDTags(conf, props, spe)
            oechem.OEWriteConstMolecule(write_ofs, conf)
    ifs.close()

    write_ofs.close()

    try:
        return props['method'], props['basis']
    except KeyError:
        return None, None

    ifs.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script takes an input \
 SDF file and updates details after Turbomole optimizations. Data supported \
 includes optimized geometry and final energy (Hartree). TODO: wall time.')

    parser.add_argument('-i','--infile', help='Input file with mols and confs\
 for each mol. Include the full path with filename.')

    parser.add_argument('-t','--theory', help='Level of theory used for all\
 calculations for mols/confs in this file. Form of method/basisset,\
 e.g., HF/6-31G*.')

    parser.add_argument('-o','--outfile', help='Output file with mols and confs\
 for each mol. Include the full path with filename.')

    args = parser.parse_args()
    getTurbResults(args.infile, args.theory, args.outfile)
