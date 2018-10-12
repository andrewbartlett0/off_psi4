#!/usr/bin/env python

## By: Victoria T. Lim

import re
import os, sys, glob
import openeye.oechem as oechem


### ------------------- Functions -------------------

def get_psi_time(filename):
    """
    Get wall-clock time from Psi4 file. If multiple times are present,
        the average will be taken. Used in CompareTimes(...) function.

    Parameters
    ----------
    filename: string name of the timefile. E.g. "timer.dat"

    Returns
    -------
    time: float of the average wall-clock time of a single timefile

    """
    with open(filename) as fname:
        times = []
        for line in fname:
            if "Wall Time:" in line:
                times.append(float(line.split()[2]))
    time = sum(times) / float(len(times))

    return time


def process_psi_out(filename, properties, calctype='opt'):
    """
    Go through output file and get level of theory (method and basis set),
        number of optimization steps, initial and final energies, and
        optimized coordinates. Returns all this information in a dictionary
        that was passed to this function.

    Parameters
    ----------
    filename: string name of the output file. E.g. "output.dat"
    properties: dictionary where all the data will go. Can be empty or not.
    calctype: string; one of 'opt','spe','hess' for geometry optimization,
        single point energy calculation, or Hessian calculation

    Returns
    -------
    properties: dictionary with summarized data from output file.
        spe keys:  basis, method, finalEnergy
        opt keys:  basis, method, numSteps, initEnergy, finalEnergy, coords
        hess keys: basis, method,

    """
    try:
        f = open(filename,"r")
    except IOError:
        print("No {} file found in directory of {}.".format(filename,os.getcwd()))
        properties['missing'] = True
        return properties

    lines = f.readlines()
    it = iter(lines)

    # process results for single point energy calculation
    if calctype=='spe':
        for line in it:
            if "set basis" in line:
                properties['basis'] = line.split()[2]
            if "energy(" in line:
                properties['method'] = line.split('\'')[1]
            if "Total Energy =" in line:
                properties['finalEnergy'] = float(line.split()[3])
        return properties

    # process results for Hessian calculation
    elif calctype=='hess':
        import math
        import numpy as np
        hess = []
        for line in it:
            if "set basis" in line:
                properties['basis'] = line.split()[2]
            if "=hessian(" in ''.join(line.split()): # remove any spaces around eql
                properties['method'] = line.split('\'')[1]
            if "## Hessian" in line:
                line = next(it) # "Irrep:"
                line = next(it) # blank line
                line = next(it) # column index labels
                line = next(it) # blank line

                # convert the rest of file/iterator to list
                rough = list(it)
                # remove last 5 lines: four blank, one exit message
                rough = rough[:-5]
                # convert strings to floats
                rough = [[float(i) for i in line.split()] for line in rough]
                # find blank sublists
                empty_indices = [i for i,x in enumerate(rough) if not x]
                # blank sublists are organized in groups of three lines:
                # (1) blank (2) column labels (3) blank. empty_ind has (1) and (3)
                # delete in reverse to maintain index consistency
                num_chunks = 1 # how many chunks psi4 printed the Hessian into
                for i in reversed(range(0,len(empty_indices),2)):
                    del rough[empty_indices[i+1]] # (3)
                    del rough[empty_indices[i]+1] # (2)
                    del rough[empty_indices[i]]   # (1)
                    num_chunks += 1
                # now remove first element of every list of row label
                _ = [ l.pop(0) for l in rough ]
                # get dimension of Hessian (3N for 3Nx3N matrix)
                three_n = int(len(rough) / num_chunks)
                # concatenate the chunks
                hess = np.array([]).reshape(three_n,0)
                for i in range(num_chunks):
                    beg_ind = i*three_n
                    end_ind = (i+1)*three_n
                    chunk_i = np.array(rough[beg_ind:end_ind])
                    hess = np.concatenate((hess,chunk_i), axis=1)
                # check that final matrix is symmetric
                if not np.allclose(hess, hess.T, atol=0):
                    print("ERROR: Hessian read from Psi4 output file not symmetric")
                    properties['hessian'] = "Hessian not found in output file"
                    return properties
                properties['hessian'] = hess
            # the Hessian pattern was never found
            else:
                properties['hessian'] = "Hessian not found in output file"

        return properties

    # process results for geometry optimization
    # loop through file to get method, basis set, numSteps, energies, coords
    rough = []
    coords = []
    for line in it:
        if "set basis" in line:
            properties['basis'] = line.split()[2]
        if "optimize(" in line:
            properties['method'] = line.split('\'')[1]
        if "Optimization is complete" in line:
            properties['numSteps'] = line.strip().split(' ')[5]
            for _ in range(8):
                line = next(it)
            properties['initEnergy'] = float(line.split()[1])
        if "Final energy" in line:
            properties['finalEnergy'] = float(line.split()[3])
            line = next(it) # "Final (previous) structure:"
            line = next(it) # "Cartesian Geometry (in Angstrom)"
            line = next(it) # Start of optimized geometry
            while "Saving final" not in line:
                rough.append(line.split()[1:4])
                line = next(it)

    # convert the 2D (3xN) coordinates to 1D list of length 3N (N atoms)
    for atomi in rough:
        coords += [float(i) for i in atomi]
    properties['coords'] = coords
    f.close()
    return properties


### ------------------- Script -------------------

def getPsiResults(origsdf, finsdf, spe=False, psiout="output.dat", timeout="timer.dat"):
    import procTags as pt # VTL temp move bc travis fails to import

    """
    Read in OEMols (and each of their conformers) in origsdf file,
        get results from Psi4 calculations in the same directory as origsdf,
        and write out results into finsdf file.
    Directory layout is .../maindir/molName/confNumber/outputfiles .

    Parameters
    ----------
    origsdf:  string - PATH+full name of orig pre-opt SDF file.
        Path should contain (1) all confs' jobs, (2) orig sdf file.
        This path will house soon-generated final output sdf file.
    finsdf:   string - full name of final SDF file with optimized results.
    spe:     Boolean - are the Psi4 results of a single point energy calcn?
    psiout:   string - name of the Psi4 output files. Default is "output.dat"
    timeout: string - name of the Psi4 timer files. Default is "timer.dat"

    Returns
    -------
    method: string - QM method from Psi4 calculations
    basisset: string - QM basis set from Psi4 calculations

    None is returned if the function returns early (e.g., if output file
       already exists) or if there is KeyError from processing last
       iteration of output file (last conf of last mol).

    """

    hdir, fname = os.path.split(origsdf)
    wdir = os.getcwd()

    # Read in .sdf file and distinguish each molecule's conformers
    ifs = oechem.oemolistream()
    ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
    if not ifs.open(origsdf):
        oechem.OEThrow.Warning("Unable to open %s for reading" % origsdf)
        quit()
    molecules = ifs.GetOEMols()

    # Open outstream file.
    writeout = os.path.join(wdir,finsdf)
    write_ofs = oechem.oemolostream()
    if os.path.exists(writeout):
        print("File already exists: %s. Skip getting results.\n" % (finsdf))
        return (None, None)
    if not write_ofs.open(writeout):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % writeout)

    # For each conformer, process output file and write new data to SDF file
    for mol in molecules:
        print("===== %s =====" % (mol.GetTitle()))
        for j, conf in enumerate( mol.GetConfs()):

            # GET DETAILS FOR SD TAGS
            props = {} # dictionary of data for this conformer
            props['package'] = "Psi4"
            props['missing'] = False
            # check whether output files exist
            outf = os.path.join(hdir,"%s/%s/%s" % (mol.GetTitle(),j+1,psiout))
            timef = os.path.join(hdir,"%s/%s/%s" % (mol.GetTitle(),j+1,timeout))
            if not (os.path.isfile(outf) and os.path.isfile(timef)):
                print("*** ERROR: Output (or timer) file not found: {} ***".format(outf))
                continue
            # Get wall clock time of the job
            try:
                props['time'] = get_psi_time(timef)
            except IOError:
                props['time'] = "Timer output file not found"
                pass
            # process output and get dictionary results
            props = process_psi_out(outf, props, spe)
            # if output was missing, move on
            if props['missing']:
                continue
            try:
                props['numSteps']
                props['finalEnergy']
                props['coords']
            except KeyError:
                sys.exit("ERROR: Psi4 job was incomplete for {}".format(outf))

            # BRIEF ANALYSIS OF STRUCTURE, INTRA HBONDS
            # Set last coordinates from optimization. skip if missing.
            if 'coords' in props and len(props['coords']) != 0 :
                conf.SetCoords(oechem.OEFloatArray(props['coords']))
            # _____________________

            # SET DETAILS TO WRITE MOLECULE
            # Set SD tags for this molecule
            pt.SetOptSDTags(conf, props, spe)
            # Write output file
            oechem.OEWriteConstMolecule(write_ofs, conf)
    ifs.close()
    write_ofs.close()
    try:
        return props['method'], props['basis']
    except KeyError:
        return None, None


def getPsiOne(infile, outfile, spe=False, psiout="output.dat", timeout="timer.dat"):
    import procTags as pt # VTL temp move bc travis fails to import

    """
    Write out Psi4 optimized geometry details into a new OEMol.

    Parameters
    ----------
    infile : string
        Name of input geometry file THAT WAS USED TO WRITE THE PSI INPUT.
        To ensure that the atom orderings remain constant.
    outfile : string
        Name of output geometry file with optimized results.
    spe : Boolean
        Are the Psi4 results of a single point energy calcn?
    psiout : string
        Name of the Psi4 output files. Default is "output.dat"
    timeout : string
        Name of the Psi4 timer files. Default is "timer.dat"

    Returns
    -------
    method: string - QM method from Psi4 calculations
    basisset: string - QM basis set from Psi4 calculations

    None is returned if the function returns early (e.g., if output file
       already exists)

    """

    # Read in SINGLE MOLECULE .sdf file
    ifs = oechem.oemolistream()
    mol = oechem.OEGraphMol()
    if not ifs.open(infile):
        oechem.OEThrow.Warning("Unable to open %s for reading" % origsdf)
        quit()
    oechem.OEReadMolecule(ifs,mol)

    # Get details for SD tags
    props = {} # dictionary of data for this mol
    props['package'] = "Psi4"
    props['missing'] = False

    # Get wall clock time of the job
    try:
        props['time'] = get_psi_time(timeout)
    except IOError:
        props['time'] = "Timer output file not found"
        pass

    # process output and get dictionary results
    props = process_psi_out(psiout, props, spe)
    if props['missing']:
        sys.exit("ERROR: Psi4 output file not found")
    try:
        props['numSteps']
        props['finalEnergy']
        props['coords']
    except KeyError:
        sys.exit("ERROR: Psi4 job was incomplete.")

    # Set last coordinates from optimization. skip if missing.
    if 'coords' in props and len(props['coords']) != 0 :
        mol.SetCoords(oechem.OEFloatArray(props['coords']))

    # Set SD tags for this molecule
    pt.SetOptSDTags(mol, props, spe)

    # Check if mol has title and set one on filename if not existing
    extract_fname = os.path.splitext(os.path.basename(infile))[0]
    if mol.GetTitle() == "":
        mol.SetTitle(extract_fname)

    # Open outstream file.
    write_ofs = oechem.oemolostream()
    if os.path.exists(outfile):
        print("File already exists: %s. Skip getting results.\n" % (outfile))
        return (None, None)
    if not write_ofs.open(outfile):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outfile)

    # Write output file
    oechem.OEWriteConstMolecule(write_ofs, mol)
    write_ofs.close()

    try:
        return props['method'], props['basis']
    except KeyError:
        return None, None


if __name__ == "__main__":
    getPsiResults(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

