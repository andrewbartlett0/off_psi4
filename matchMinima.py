#!/usr/bin/env python

# By: Victoria T. Lim

import os
import sys
import openeye.oechem as oechem
import numpy as np
from numpy import nan
import pickle
import itertools
import matplotlib.pyplot as plt
import matplotlib as mpl
import procTags as pt           # for GetSDList


### ------------------- Functions -------------------



def compare2Mols(rmol, qmol):
    """
    For two identical molecules, with varying conformers,
        make an M by N comparison to match the M minima of
        rmol to the N minima of qmol. Match is declared
        for lowest RMSD between the two conformers and
        if the RMSD is below 0.5 Angstrom.

    Parameters
    ----------
    rmol:       reference OEChem molecule with all its filtered conformers
    qmol:       query OEChem molecule with all its filtered conformers

    """

    automorph = True   # take into acct symmetry related transformations
    heavyOnly = False  # do consider hydrogen atoms for automorphisms
    overlay = True     # find the lowest possible RMSD


    molIndices = []  # 1D list for storing indices of matched qmol confs wrt rmol

    for Rconf in rmol.GetConfs():
        print(">>>> Matching %s conformers to minima: %d <<<<"\
            % (qmol.GetTitle(),Rconf.GetIdx()+1))

        # for this Rconf, calculate/store RMSDs with all of qmol's conformers
        rsublist = []
        for Qconf in qmol.GetConfs():
            rms = oechem.OERMSD(Rconf,Qconf,automorph,heavyOnly,overlay)
            rsublist.append(rms)

        # for this Rconf, get qmol conformer index for minimum RMSD
        thisMin=[i for i, j in enumerate(rsublist) if j == min(rsublist)][0]
        if rsublist[thisMin] <= 0.5:
            molIndices.append(thisMin)
        else:
            print('no match bc rmsd is ',rsublist[thisMin])
            molIndices.append(None)

    return molIndices


def plotMolMinima(molName, minimaE, xticklabels, selected=None,stag=False):
    '''

    '''
    # stagger plots to better see line overlap. works best with few (<4?) numFiles.
    # minimaE for ONE molecule

    refNumConfs = len(minimaE[0])
    refFile = xticklabels[0]
    numFiles = len(minimaE)

    ### Flatten this 2D list into a 1D to find min and max for plot
    flatten = [item for sublist in minimaE for item in sublist]
    floor = min(flatten)
    ceiling = max(flatten)
    if (ceiling - floor) > 4.0:
        ystep = (ceiling - floor)/9 # have 10 increments of y-axis
        ystep = round(ystep * 2) / 2 # round the step to nearest 0.5
    else:
        ystep = (ceiling - floor)

    ### Stagger each of the component files of minimaE for ease of viewing.
    if stag==True:
        tempMinimaE = []
        for i, fileE in enumerate(minimaE):
            tempMinimaE.append([x+i/2. for x in fileE])
        minimaE = tempMinimaE
        ceiling = ceiling + numFiles

    ### Figure labels.
    plttitle="Relative Energies of %s Minima" % (molName)
    plttitle+="\nby Reference File %s" % (refFile)
    ylabel="Relative energy (kcal/mol)"
    figname = "minimaE_%s.png" % (molName)

    ### Set x-axis values and labels. Can either be letter or number.

    # LETTER LABELS
    letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ' # label x-axis by letter
    rpt = int((len(minimaE[0])/26)+1)
    xlabs =[''.join(i) for i in itertools.product(letters, repeat=rpt)][:refNumConfs]
    # OR, NUMBER LABELS
    #xlabs = range(len(minimaE[0]))

    ### Set this up for grid.
    fig = plt.figure(figsize=(20,10))
    ax = fig.gca()
    ax.set_xticks(np.arange(-1,refNumConfs+1,2))

    ### Label figure. Label xticks before plot for better spacing.
    plt.title(plttitle,fontsize=16)
    plt.ylabel(ylabel,fontsize=20)
    plt.xlabel("conformer minimum",fontsize=20)
    plt.xticks(list(range(refNumConfs)),xlabs,fontsize=18)
    plt.yticks(fontsize=18)

    ### Plot the data.
    colors = mpl.cm.rainbow(np.linspace(0, 1, numFiles))
    markers = ["x","^","8","d","o","s","*","p","v","<","D","+",">","."]*10
    #for i in reversed(range(numFiles)):
    for i, FileE in enumerate(minimaE):
        if selected is not None and i not in selected:
            continue
        xi = list(range(refNumConfs))
        #yi = [item[i] for item in minimaE]
        yi = FileE
        plt.plot(xi,yi,color=colors[i],label=xticklabels[i],\
            marker=markers[i],markersize=9)

    ### Add legend and set plot limits.
    plt.legend(bbox_to_anchor=(0.96, 1), loc=2,prop={'size':18})
    plt.xlim(-1,refNumConfs+1)
    # y axis limits: min, max, step
    ax.set_yticks(np.arange(int(round(floor))-2,int(round(ceiling))+2,ystep))
    plt.grid()

    plt.savefig(figname,bbox_inches='tight')
#    plt.show()
    plt.clf()

def plotAvgTimes(molName, avgTimes, sdTimes, xticklabels):
    plttitle="Conformer-Averaged Wall Times\nfor %s" % (molName)
    plttitle+="\nGeometry Optimization in Psi4"
    ylabel="time (s)"
    figname = "timebars_%s.png" % molName
    x = list(range(len(avgTimes)))

    ### Label figure. Label xticks before plot for better spacing.
    plt.title(plttitle,fontsize=20)
    plt.ylabel(ylabel,fontsize=18)
    plt.xticks(x,xticklabels,fontsize=14,rotation=-30, ha='left')
    plt.yticks(fontsize=14)

    ### Plot the data.
    colors = mpl.cm.rainbow(np.linspace(0, 1, len(x)))
    plt.bar(x, avgTimes, color=colors,align='center',yerr=sdTimes,ecolor='k')
    plt.savefig(figname,bbox_inches='tight')
#    plt.show()
    plt.clf()



def matchMinima(sdfList, thryList):
    """
    For list of SDF files, match the conformer minima to those of the reference
       SDF file. Ex. Conf G of reference file matches with conf R of file3.

    Parameters
    ----------
    sdfList: str list - list of the SDF file names to be analyzed.
          This list should include reference SDF file (sdfRef) as first element.
    thryList: str list - list of levels of theory corresponding to the files
          in sdfList. E.g., ['MP2/def2-TZVP','B3LYP-D3MBJ/6-311++G**']

    Returns
    -------
    molNames: list of molecule names from the reference molecules
    refNumConfs: list of ints representing each reference mol's number of conformers
    allIndices: 2D list representing, for each sdfQuery, the conformer indices
       that match reference conformer.
       [[-1, -1, -1], [-1], [2, 3, 1], [0]] means there are two molecules, one
       with 3 confs, and one with 1 conf. The first two sublists are -1 because
       sdfQuery matched sdfRef. For the second two sublists, sdfQuery's
       mol1 conf2 matches with sdfRef's mol1 conf1.
    elists: 2D list of floats in similar format of allIndices, being energies
       of [[file1 mol1], ..., [file1 molN], [file2 mol1], ... [file2 molN]]
       Note that the mols belonging to one file are not separated in a sublist.

    """
    def loadFile(fname):
        ifs = oechem.oemolistream()
        ifs.SetConfTest( oechem.OEAbsoluteConfTest() )
        if not ifs.open(fname):
            oechem.OEThrow.Fatal("Unable to open %s for reading" % fname)
        mols = ifs.GetOEMols()
        return mols

    sdfRef = sdfList[0]
    numFiles = len(sdfList)
    allIndices = [] # for M mols, N reference minima of each mol, P matching indices for each ref minimia
    elists = [] # 2D list: K mols per file x J numFiles
    tlists = [] # 2D list: K mols per file x J numFiles
    refNumConfs = [] # number of conformers for each mol in reference file
    molNames = [] # name of each molecule. for plotting.

    for i, sdfQuery in enumerate(sdfList):
        qthry = thryList[i]
        qmethod = qthry.split('/')[0].strip()
        qbasis = qthry.split('/')[1].strip()

        print("\n\nOpening reference file %s" % sdfRef)
        molsRef = loadFile(sdfRef)

        print("Opening query file %s, and using [ %s ] energies" % (sdfQuery, qthry))
        molsQuery = loadFile(sdfQuery)

        # loop over each molecule in reference file and in query file
        for rmol in molsRef:
            #qmol = molsQuery.next()
            noMatch = True
            for qmol in molsQuery:
                if rmol.GetTitle() == qmol.GetTitle():
                    noMatch = False
                    break
            if noMatch:
                allIndices.append([-2]*rmol.NumConfs())
                elists.append([nan]*rmol.NumConfs())
                tlists.append([nan]*rmol.NumConfs())
                print("No %s molecule found in %s" % (rmol.GetTitle(), sdfQuery))
                # gotta reset the molsQuery generator
                molsQuery = loadFile(sdfQuery)
                continue

            # get energies for plotting relative energies
            elists.append(list(map(float, pt.GetSDList(qmol, "QM opt energy",'Psi4', qmethod, qbasis)))) # adapt for SPE? === *
            tlists.append(list(map(float, pt.GetSDList(qmol, "opt runtime",'Psi4', qmethod, qbasis))))


            # Skip minmatch if this query file is same as reference file;
            #    before skip, get data for elists, refNumConfs, allIndices.
            if(sdfQuery == sdfRef):
                print("\nSkipping comparison against self.")
                molNames.append(rmol.GetTitle())
                refNumConfs.append(rmol.NumConfs())
                allIndices.append([-1]*rmol.NumConfs())
                continue

            # get indices of qmol conformers that match rmol conformers
            molIndices = compare2Mols(rmol, qmol)
            allIndices.append(molIndices)

    numMols = len(refNumConfs)
    molNames = molNames[:numMols]
    print("\nmolNames\n",molNames)
    print("\nrefNumConfs\n",refNumConfs)
    print("\nallIndices\n",allIndices)
    print("\nelists\n",elists)

    return molNames, refNumConfs, allIndices, elists, tlists

def getAllTimes(sdfList, thryList):
    """
    Get times saved in SD tages from files listed in python input file lines. 
       No longer used after edits to matchMinima (07/1/2017).

    Parameters
    ----------
    sdfList: str list - list of the SDF file names to be analyzed.
          This list should include reference SDF file (sdfRef) as first element.
    thryList: str list - list of levels of theory corresponding to the files
          in sdfList. E.g., ['MP2/def2-TZVP','B3LYP-D3MBJ/6-311++G**']

    Returns
    -------
    timelists: 3D list where timelists[i][j][k] is the wall time for optimizing
       for the ith level of theory, jth molecule, kth conformer

    """

    sdfRef = sdfList[0]
    timelists = []
    for i, sdfQuery in enumerate(sdfList):
        qthry = thryList[i]
        qmethod = qthry.split('/')[0].strip()
        qbasis = qthry.split('/')[1].strip()

        print("\n\nOpening reference file %s" % sdfRef)
        ifsRef = oechem.oemolistream()
        ifsRef.SetConfTest( oechem.OEAbsoluteConfTest() )
        if not ifsRef.open(sdfRef):
            oechem.OEThrow.Fatal("Unable to open %s for reading" % sdfRef)
        molsRef = ifsRef.GetOEMols()

        print("Opening query file %s, and using [ %s ] wall times" % (sdfQuery, qthry))
        ifsQuery = oechem.oemolistream()
        ifsQuery.SetConfTest( oechem.OEAbsoluteConfTest() )
        if not ifsQuery.open(sdfQuery):
            oechem.OEThrow.Fatal("Unable to open %s for reading" % sdfQuery)
        molsQuery = ifsQuery.GetOEMols()

        for rmol in molsRef:
            try:
                qmol = next(molsQuery)
                timelists.append(map(float, pt.GetSDList(qmol, "opt runtime",'Psi4', qmethod, qbasis))) # for opt, not spe
            except StopIteration:
                print("No %s molecule found in %s" % (rmol.GetTitle(), sdfQuery))
                timelists.append([nan]*rmol.NumConfs())
                continue

    return timelists

def calcRMSError(trimE, zeroes):
    """
    From relative energies with respect to some conformer from calcRelEne,
       calculate the root mean square error with respect to the relative
       conformer energies of the first (reference) file.

    Parameters
    ----------
    trimE: 3D list of energies, where trimE[i][j][k] represents the
      ith molecule, jth file, kth conformer rel energy
    zeroes: a 1D list of index of the reference conformer per each mol

    Returns
    -------
    relByFile: a 1D list of RMS errors for each file with reference to
      first input file

    """
    relByFile = []
    for i, molist in enumerate(trimE):
        molEnes = []
        for j, filelist in enumerate(molist):
            errs = np.asarray(filelist) - np.asarray(molist[0]) # subtract ref file
            sqrs = errs**2. # squared
            sqrs = np.delete(sqrs,zeroes[i]) # delete reference conformer (zero rel ene)
            sqrs = sqrs[~np.isnan(sqrs)] # delete nan values to get an rmse********
            mse = np.mean(sqrs)
            rmse = np.sqrt(mse)
            molEnes.append(rmse)
        relByFile.append(molEnes)

    return relByFile


def getRatioTimes(allMolTimes, zeroes):
    """
    From all molecule times, calculate relative time ratios for matched minima.
       If a conf has nan or is not matched, that time is not considered.
       After dividing by reference time, the matched conformer files are
       averaged for a particular file opt.

    Parameters
    ----------
    allMolTimes: 3D list of times, where allMolTimes[i][j][k] represents the
      ith molecule, jth file, kth conformer time (sec)

    Returns
    -------
    relByFile: a 1D list of times ratios for each file with reference to
      first input file
    sdByFile: a 1D list of standard deviation of conformer-averaged times
      relative to first input file

    """

    relByFile = []
    sdByFile = []
    for i, molist in enumerate(allMolTimes):
        molTimes = []
        molStds = []
        for j, filelist in enumerate(molist):
            rels = np.asarray(filelist)/np.asarray(molist[0])
            rels = rels[~np.isnan(rels)] # delete nan values to get avg********
            avg = np.mean(rels)
            sd = np.std(rels)
            molTimes.append(avg)
            molStds.append(sd)
        relByFile.append(molTimes)
        sdByFile.append(molStds)
    return relByFile, sdByFile

def calcRelEne(minimaE):
    """
    Calculate the relative energy. For each file, take conformer energy
       relative to minimum X. The conformer minimum is chosen from
       the first conformer for which all files have an energy value.
       Note that relative energies are taken with a file's conformers,
       not subtracting one file from another (see calcRMSError).

    Parameters
    ----------
    minimaE: 3D list of energies, where minimaE[i][j][k] represents the
      ith molecule, jth file, kth minima of that ith molecule

    Returns
    -------
    trimE: 3D list of energies as above except with relative energies
      in kcal/mol (instead of absolute energies in Hartrees). For mols
      with a single conformer it doesn't make sense to calculate rel
      energies. These mols are deleted from minimaE.
    zeroes: a 1D list of index of the reference conformer per each mol

    """

    zeroes = []
    mols2del = []
    for i, molist in enumerate(minimaE): # loop over ith molecule
        refCount = len(molist[0]) # number of confs in ref file

        # find first conformer with least nan's.
        nanCnt = []
        for j in range(refCount): # loop over confs of ref file
            nanCnt.append(sum(np.isnan([item[j] for item in molist])))
        print("mol {} nanCnt: {}".format(i,nanCnt))

        # get indices of confs with least nan's. no argmin bc want all idx
        where0 = np.empty(0)
        counter = 0
        while where0.size == 0 and counter < refCount:
            where0 = np.where(np.asarray(nanCnt) == counter)[0]
            counter += 1
        if where0.size > 0: # if there ARE confs with 0 nan's, find min E
            leastNanEs = np.take(molist[0],where0) # energies of the where0s
            winningconfIdx = where0[np.argmin(leastNanEs)] # idx of lowest E
            zeroes.append(winningconfIdx)
        else:
            zeroes.append(nanCnt.index(min(nanCnt)))

#    # delete cases with just one conformer
#    print("ATTN: these (zero-indexed) mols were removed from analysis due to "
#         +"single conformer or no conformer matches in at least one file: ",
#         mols2del)
#    trimE = np.delete(np.asarray(minimaE),mols2del,axis=0)
#    if len(trimE) != len(zeroes):
#        print len(trimE), zeroes
#        sys.exit("Error in determining reference confs for molecules.")

    # calc relative energies, and convert Hartrees to kcal/mol.
    mintemp = []  # not sure why this is needed but writeRelEne kicks fuss without it
    for z, molE in zip(zeroes, minimaE):
    #for z, molE in zip(zeroes, trimE):
        temp = [] # temp list for this mol's relative energies
        for fileE in molE:
            temp.append([627.5095*(fileE[i]-fileE[z]) for i in range(len(fileE))])
        mintemp.append(temp)
    trimE = mintemp

    return trimE, zeroes

def writeRelEne(molName, rmse, relEnes, zero, thryList, prefix='relene'):
    """

    """

    compF = open(prefix+'_'+molName+'.dat','w')
    compF.write("# Molecule %s\n" % molName)
    compF.write("# Energies (kcal/mol) for each matched conformer relative to "+
                "conformer " + str(zero)+" across each column.\n")
    compF.write("# Rows represent conformers of this molecule; columns " +
                "represent some calculations from a particular file.\n")
    compF.write("# Columns are ordered by conformer index, then the "+
                "following levels of theory:")

    # write methods, RMSEs, integer column header
    rmsheader = "\n# "
    colheader = "\n\n# "
    for i, t in enumerate(thryList):
        compF.write("\n# %d %s" % ((i+1),t))
        rmsheader += '\t%.4f' % rmse[i]
        colheader += '\t' + str(i+1)

    compF.write("\n\n# RMS errors by level of theory, with respect to the "+
                "first level of theory listed:")
    compF.write(rmsheader)
    compF.write(colheader)

    # write each opt's relative energies
    for i in range(len(relEnes[0])):
        compF.write('\n'+str(i)+'\t')
        thisline = [x[i] for x in relEnes]
        thisline = [ '%.4f' % elem for elem in thisline ]
        thisline = '\t'.join(map(str,thisline))
        compF.write(thisline)
    compF.close()

def reorganizeSublists(theArray,allMolIndices):
    """
    theArray should be a three-dimensional list, in which theArray[i][j][k]
        represents the ith molecule, jth opt file, kth conformer.
    allMolIndices should be the exact same shape.

    Instead of grouping by files then by molecule,
        reorder to group by molecules then by file.
    Something like this:
       [[[file1 mol1] [file1 mol2]] ... [[file2 mol1] [file2 mol2]]]
    Goes to this:
       [[[file1 mol1] [file2 mol1]] ... [[file1 molN] [file2 molN]]]

    This function checks if minima is matched, using allMolIndices. If not, the
       value in theArray is NOT used, and nan is used instead.

    """
    # get list lengths for debugging
#    for i in range(len(theArray)):
#        for l in range(len(theArray[0])):
#            print(len(allMolIndices), len(allMolIndices[i]), len(allMolIndices[i][l]))
#            print(len(theArray), len(theArray[i]), len(theArray[i][l]))

    minimaE = []
    for i, molIndices in enumerate(allMolIndices):
        molE = [] # all conf energies from ith mol in all files
        for j, fileIndices in enumerate(molIndices):
            fileE = []  # all conf energies from ith mol in jth file
            for k, confNum in enumerate(fileIndices):
                if confNum == None:
                    print("No matching conformer within 0.5 A RMSD for {}th\
 conf of {}th mol in {}th file.".format(k, i, j))
                    fileE.append(nan)
                elif confNum==-2:
                    # only print this warning message once per mol
                    if k==0: print("!!!! The entire {}th mol is not found in {}th\
 file. !!!!".format(i, j))
                    fileE.append(nan)
                elif len(theArray[i][j])==0:
                    print("!!!! Mol {} was found and confs were matched by RMSD but\
 there are no energies of {}th method. !!!!".format(i, j))
                    fileE.append(nan)
                elif confNum == -1:   # -1 signifies reference theory
                    fileE.append(float(theArray[i][j][k]))
                else:
                    #print(theArray[i][j])
                    fileE.append(float(theArray[i][j][confNum]))
            molE.append(fileE)
        minimaE.append(molE)
    return minimaE



### ------------------- Parser -------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input",
        help="Required argument on name of text file with information on\
              file(s) and levels of theory to process.\
              See README file or examples for more details. TODO")

    parser.add_argument("--readpickle", action="store_true", default=False,
        help="If specified, read in data from pickle files from each \
              directory. Input file can be same as for heat plot inputs, \
              and pickle files will be read from same directory as \
              specified output files.")

    parser.add_argument("--verbose", action="store_true", default=False,
        help="If specified, write out relative energies in kcal/mol for \
              all conformers of all mols for all files. If in doubt, \
              do specify this option.")

    parser.add_argument("--eplot",action="store_true", default=False,
        help="Generate line plots for every molecule with relative energies.")

    parser.add_argument("--tplot", action="store_true", default=False,
        help="Generate bar plots of conformer-averaged time per each \
              optimization. One plot generated per molecule.")

    args = parser.parse_args()
    opt = vars(args)
    if not os.path.exists(opt['input']):
        raise parser.error("Input file %s does not exist." % opt['filename'])
    sys.stdout.flush()


    # Read input file and store each file's information in two lists.
    sdfList = []
    thryList = []
    with open(opt['input']) as f:
        for line in f:
            if line.startswith('#'):
                continue
            dataline = [x.strip() for x in line.split(',')]
            if dataline == ['']:
                continue
            thryList.append(dataline[0])
            sdfList.append(dataline[1])

    # Check that each file exists before starting -_-
    while True:
        list1 = []
        for f in sdfList:
            list1.append(os.path.isfile(f))
    
        if all(list1):
            # All elements are True. Therefore all the files exist. Run %run commands
            break
        else:
            raise parser.error("One or more input files are missing!!")

    # =========================================================================
    if not opt['readpickle']:
        molNames, refNumConfs, allIndices, elists, tlists = matchMinima(sdfList, thryList)
        pickle.dump([molNames, refNumConfs,allIndices,elists,tlists], open('match.pickle', 'wb'))
    else:
        molNames, refNumConfs, allIndices, elists, tlists = pickle.load(open('match.pickle', 'rb'))
    # =========================================================================

    numMols = len(refNumConfs)
    # Separate molecules by sublist, 2D --> 3D
    allMolIndices = [allIndices[i::numMols] for i in range(numMols)]
    elists = [elists[i::numMols] for i in range(numMols)]
    # Reorder indices and energies lists by molecules instead of by files.
    #   [[[file1 mol1] [file2 mol1]] ... [[file1 molN] [file2 molN]]]
    minimaE = reorganizeSublists(elists, allMolIndices)

    # =========================================================================
    trimE, zeroes = calcRelEne(minimaE)
    rmselist = calcRMSError(trimE, zeroes)

    # =========================================================================

    if opt['verbose']:
        for i, mn in enumerate(molNames):
            try:
                writeRelEne(mn, rmselist[i],trimE[i],zeroes[i],thryList)
            except IndexError:
                zeroes.append(nan)
                writeRelEne(mn, [nan]*len(thryList),elists[i],zeroes[i],thryList)


    if opt['tplot']:
#        allMolTimes = getAllTimes(sdfList, thryList) # ordered by file, mol, conf
#        allMolTimes = tlists

#        # match conformer times using indices from matchMinima then get stats
#        allFileTimes = [[] for i in range(numMols)]
#        allFileStds = [[] for i in range(numMols)]
#        for i in range(len(sdfList)*numMols):
#            timeSuc = 0     # running sum of successfully matched minima times
#            numSuc = 0      # running number of successful minima
#            numconfs = refNumConfs[i%numMols]  # i%numMols gets some mol
#            fileTimes = []  # collect successful times for stdevs
#            for k in range(numconfs):
#                thisIndex = allIndices[i][k]
#                if thisIndex == -1:
#                    timeSuc += allMolTimes[i][k]
#                    numSuc += 1
#                    fileTimes.append(allMolTimes[i][k])
#                elif thisIndex > -1:
#                    timeSuc += allMolTimes[i][thisIndex]
#                    numSuc += 1
#                    fileTimes.append(allMolTimes[i][thisIndex])
#            try:
#                fTimeAvg = float(timeSuc)/numSuc
#            except ZeroDivisionError:
#                fTimeAvg = nan
#            allFileTimes[i%numMols].append(fTimeAvg)
#            allFileStds[i%numMols].append(np.std(np.array(fileTimes)))
#            #print 'average ',fTimeAvg,' over ',numSuc," samples"

        # separately, go from allMolTimes and calculate relative speeds
        #   [[[file1 mol1] [file2 mol1]] ... [[file1 molN] [file2 molN]]]
        allMolTimes = [tlists[i::numMols] for i in range(numMols)]
        timesByMol = reorganizeSublists(allMolTimes, allMolIndices)
        relTimes, sdTimes = getRatioTimes(timesByMol, zeroes)

        allFileTimes = [[] for i in range(numMols)]
        allFileStds = [[] for i in range(numMols)]
            
        for i, molTimes in enumerate(timesByMol):
            # loop by each file to remove nans
            for j, molFileList in enumerate(molTimes):
                shortmf = np.asarray(molFileList)
                shortmf = shortmf[~np.isnan(shortmf)]
                allFileTimes[i].append(np.mean(shortmf))
                allFileStds[i].append(np.std(shortmf))

        # bar plot of average times with stdevs
        for name, fileTimes, stdevs in zip(molNames, allFileTimes, allFileStds):
            to_exclude = {} # declare empty set if want to use all levels of thry
            fileTimes_i = [element for i, element in enumerate(fileTimes) if i not in to_exclude]
            stdevs_i = [element for i, element in enumerate(stdevs) if i not in to_exclude]
            thryList_i = [element for i, element in enumerate(thryList) if i not in to_exclude]
            plotAvgTimes(name, fileTimes_i, stdevs_i, thryList_i)

        if opt['verbose']: # append time to relative energies file
            for i, name in enumerate(molNames):
#            for name, fileTimes, stdevs in zip(molNames, allFileTimes, allFileStds, relTimes, sdTimes):
                compF = open('relene_'+name+'.dat','a')
                compF.write("\n\n# Four rows: (1) avg times, (2) time stdevs,\
 (3) avg time ratios wrt ref method, (4) stdevs of time ratios:")
                avgline = "\n# "
                stdline = "\n# "
                a2line =  "\n# "
                s2line =  "\n# "
                for j, t in enumerate(thryList):
                    avgline += ' %.4f' % allFileTimes[i][j]
                    stdline += ' %.4f' % allFileStds[i][j]
                    a2line += ' %.4f' % relTimes[i][j]
                    s2line += ' %.4f' % sdTimes[i][j]

                compF.write(avgline)
                compF.write(stdline)
                compF.write(a2line)
                compF.write(s2line)
                compF.close()


    if opt['eplot']:
        for name, minE in zip(molNames, trimE):
            #if name != 'AlkEthOH_c1178': continue
            plotMolMinima(name, minE, thryList)
            #plotMolMinima(name, minE, thryList, selected=[0,7,12]) # zero based index

