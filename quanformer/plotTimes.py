#!/usr/bin/env python

import os
import openeye.oechem as oechem
import numpy as np
import proc_tags as pt
import collections
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import stats # for mode

### ------------------- Functions -------------------




def timeAvg(titles, sdfRef, method, basis, tag):
    """

    For an SDF file with all confs of all mols, get the average runtime
       of all conformers for each molecule

    Parameters
    ----------
    titles: dictionary (empty or not). keys = molTitles.
        values = [[qm1_avg, qm1_std], [qm2_avg, qm2_std] ... ]
    sdfRef | str  | path+name of SDF file with times for all confs of all mols

    TODO

    """

    # Open reference file.
    print("Opening SDF file %s" % sdfRef)
    ifsRef = oechem.oemolistream()
    ifsRef.SetConfTest( oechem.OEAbsoluteConfTest() )
    if not ifsRef.open(sdfRef):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % sdfRef)
    molsRef = ifsRef.GetOEMols()

    timeF = open("timeAvgs.txt", 'a')
    timeF.write("\nFile: {}\n".format(sdfRef))
    timeF.write("Average [{}/{}] [{}s] over all confs for each molecule\n".format(method, basis, tag))

    # Grab all the times.
#    titles = {}
#    timelist = []
#    stdlist = []
    for rmol in molsRef:
        tmol = np.fromiter(pt.get_sd_list(rmol, tag, 'Psi4',method, basis), dtype=np.float64)

        # exclude conformers for which job did not finish (nan)
        nanIndices = np.argwhere(np.isnan(tmol))
        for i in reversed(nanIndices): # loop in reverse to delete correctly
            tmol = np.delete(tmol, i)
        meantime = np.mean(tmol)
        stdtime = np.std(tmol)
        timeF.write("%s\t%d confs\t\t%.3f +- %.3f\n" % (rmol.GetTitle(), tmol.size, meantime, stdtime ))

        name = rmol.GetTitle()
        if name not in titles: titles[name] = []
        titles[name].append([meantime, stdtime])
#        titles.append(rmol.GetTitle())
#        timelist.append(meantime)
#        stdlist.append(stdtime)
    timeF.close()
#    return titles, timelist, stdlist
    return titles



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

    # Read input file and store each file's information in an ordered dictionary.
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
            wholedict[linecount] = {'ftheory':dataline[0],'fname':dataline[1], 'qtag':dataline[2]}
            linecount += 1

    titles = {}
    timeplot = [] # list of times for each file in input file. mols per file separated via sublists
    stdplot = [] # ditto with number of optimization steps
    for i in wholedict:
        qthry = wholedict[i]['ftheory']
        qmethod = qthry.split('/')[0].strip()
        qbasis = qthry.split('/')[1].strip()
        qtag = wholedict[i]['qtag'].strip()

        #ititle, itime, istd = timeAvg(wholedict[i]['fname'], qmethod, qbasis, qtag)
        newtitles = timeAvg(titles, wholedict[i]['fname'], qmethod, qbasis, qtag)
#        titles.append(ititle)
#        timeplot.append(itime)
#        stdplot.append(istd)

    # dictionary to arrays
    for item in titles.values():
        timeplot.append([k[0] for k in item]) # timeplot[i][j] == time of mol i, file j
        stdplot.append([k[1] for k in item])

    # delete mols with missing data. asarray must have uniform length sublists.
    lens = [len(x) for x in timeplot]
    m = stats.mode(lens)[0][0] # ModeResult(mode=array([2]), count=array([40]))
    tracker = [] # indices of which sublists to remove
    for i, t in enumerate(timeplot):
        if len(t) != m:
            tracker.append(i)
    for index in sorted(tracker, reverse=True):
        del timeplot[index]
        del stdplot[index]
    timeplot = np.asarray(timeplot).T # timeplot[i][j] == time of file i, mol j
    stdplot = np.asarray(stdplot).T

    ### PLOTTING
    # horizonal range
#    x = np.arange(len(timeplot[0]))
    x = np.arange(len(titles)-len(tracker))
    width = 1./(len(x))
    # loop over all the SDF files
    coeff = 0
    for y, s in zip(timeplot, stdplot):
        plt.bar(x+coeff*width, y, yerr=s, alpha=1-0.5*coeff) # alpha:opacity
        print(1-0.5*coeff)
        coeff += 1

    ### Label figure. Label xticks before plot for better spacing.
#    plttitle="Average Wall-Clock Times for %s" % (basename)
#    plttitle+="\nGeometry Optimization in Psi4"
#    plt.title(plttitle,fontsize=20)
#    plt.ylabel("time (s)",fontsize=18)
#    plt.xticks(x,xticklabels,fontsize=14,rotation=30, ha='left')
#    plt.yticks(fontsize=14)
    plt.legend(['without FastOpt','with FastOpt'])

    ### Plot the data.
    colors = mpl.cm.rainbow(np.linspace(0, 1, len(x)))
#    plt.bar(x, timeplot, color=colors,align='center',yerr=sdtimes,ecolor='k')
#    plt.bar(x, timeplot[0], color=colors,align='center',ecolor='k')
    plt.savefig('rename_me.png',bbox_inches='tight')
    plt.show()
