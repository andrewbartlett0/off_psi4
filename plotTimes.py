#!/usr/bin/env python

import os
import openeye.oechem as oechem
import numpy as np
import procTags as pt

### ------------------- Functions -------------------




def timeAvg(sdfRef, method, basis, steps=False):
    """

    For an SDF file with all confs of all mols, get the average runtime
       of all conformers for each molecule

    Parameters
    ----------
    sdfRef | str  | path+name of SDF file with times for all confs of all mols
    steps  | Bool | average number of steps instead of runtime seconds

    """
    
    # Open reference file.
    print("Opening SDF file %s" % sdfRef)
    ifsRef = oechem.oemolistream()
    ifsRef.SetConfTest( oechem.OEAbsoluteConfTest() )
    if not ifsRef.open(sdfRef):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % sdfRef)
    molsRef = ifsRef.GetOEMols()

    timeF = open(os.path.join(os.path.dirname(sdfRef),"timeAvgs.txt"), 'a')
    timeF.write("\nAnalyzing file: %s \n" % (sdfRef))
    if not steps: timeF.write("\nAverage runtime (sec) over all confs for each molecule\n")
    else: timeF.write("\nAverage number of steps over all confs for each molecule\n")

    # Grab all the times.
    for rmol in molsRef:
        if not steps:
            tmol = np.array(map(float, pt.GetSDList(rmol, "runtime", method, basis)))
        else:
            tmol = np.array(map(float, pt.GetSDList(rmol, "step", method, basis)))

        # exclude conformers for which job did not finish (nan)
        nanIndices = np.argwhere(np.isnan(tmol))
        for i in reversed(nanIndices): # loop in reverse to delete correctly
            tmol = np.delete(tmol, i)
        timeF.write( "%s\t%d confs\t\t%.3f\n" % (rmol.GetTitle(), tmol.size, np.mean(tmol)) )
    timeF.close()



### ----------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input",
        help="Required argument on name of text file with information on\
              file(s) and levels of theory to process.\
              See README file or examples for more details. TODO")

    args = parser.parse_args()
    opt = vars(args)

    if not os.path.exists(opt['input']):
        raise parser.error("Input file %s does not exist." % opt['filename'])

    # Read input file and store each file's information in an overarching set.
    # http://stackoverflow.com/questions/25924244/creating-2d-dictionary-in-python
    linecount = 0
    wholedict = collections.OrderedDict()
    with open(opt['input']) as f:
        for line in f:
            if line.startswith('#'):
                continue
            dataline = [x.strip() for x in line.split(',')]
            if dataline == ['']:
                continue
            wholedict[linecount] = {'ftheory':dataline[0],'fname':dataline[1], 'fromspe':dataline[2]}
            linecount += 1

    timelist = [] # list of times for each file in input file. mols per file separated via sublists
    steplist = [] # ditto with number of optimization steps
    for i in wholedict:
        qthry = wholedict[i]['ftheory']
        qmethod = qthry.split('/')[0].strip()
        qbasis = qthry.split('/')[1].strip()

        itime, isteps = timeAvg(wholedict[i]['fname'], qmethod, qbasis, steps=True)
        timelist.append(itime)
        steplist.append(isteps)

    plttitle="Average Wall-Clock Times for %s" % (basename)
    plttitle+="\nGeometry Optimization in Psi4"
    ylabel="time (s)"
    figname = os.path.join(wdir,"times_%s.png" % (basename))
    x = range(len(timeplot))

    ### Label figure. Label xticks before plot for better spacing.
    plt.title(plttitle,fontsize=20)
    plt.ylabel(ylabel,fontsize=18)
    plt.xticks(x,xticklabels,fontsize=14,rotation=30, ha='left')
    plt.yticks(fontsize=14)

    ### Plot the data.
    colors = mpl.cm.rainbow(np.linspace(0, 1, len(x)))
    plt.bar(x, timeplot, color=colors,align='center',yerr=sdtimes,ecolor='k')
