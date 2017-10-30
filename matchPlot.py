#!/usr/bin/env python

import os
import sys
import numpy as np
from numpy import nan
import itertools
import matplotlib.pyplot as plt
import matplotlib as mpl

'''
Generate heat plots, scatter plots, and 3D plots from output of matchMinima.py.
This extends results from matchMinima.py which only plots 
simple bar plots and line plots.

'''

def shiftArray(rmsArray):
    """
    Place the first element of array in diagonal spot.
    Order of everything before and everything after is retained.
    Example,
      0 4 6                0 4 6
      0 2 7  --becomes-->  2 0 7
      0 1 3                1 3 0

    """
    for i, sublist in enumerate(rmsArray):
        sublist.insert(i,sublist.pop(0))
    return rmsArray

def plotHeatRMSE(molName, rmsArray, ticklabels,ptitle='RMS error (kcal/mol)',fprefix='rmse', colors='PRGn_r'):
    plttitle="%s\n%s" % (ptitle,molName)
    figname = "%s_%s.png" % (fprefix, molName)
    x = list(range(len(rmsArray)))
    y = list(range(len(rmsArray)))

    plt.figure(figsize=(10,5))

    ### Tranpose and plot data - imshow swaps x and y
    plt.imshow(np.asarray(rmsArray).T, cmap=colors, origin='lower')
    cbar = plt.colorbar()

    ### Label figure. Label xticks before plot for better spacing.
#    plt.title(plttitle,fontsize=20)
    plt.xticks(x,ticklabels,fontsize=12,rotation=-30, ha='left')
    plt.yticks(y,ticklabels,fontsize=14)
    plt.xlabel("reference",fontsize=14)
    plt.ylabel("compared",fontsize=16)
    cbar.ax.tick_params(labelsize=14)

    ### Save/show plot.
    plt.savefig(figname,bbox_inches='tight')
#    plt.show()
    plt.clf()



def plotET(molName, eneArray, timeArray, ticklabels,fprefix='scatter'):
    plttitle="RMS error vs. log ratio of wall time\n%s" % molName
    figname = "%s_%s.png" % (fprefix, molName)
    colors = mpl.cm.rainbow(np.linspace(0, 1, len(eneArray)))
    markers = ["x","^","8","d","o","s","*","p","v","<","D","+",">","."]*10

    # use plt.plot instead of scatter to label each point
    for i, (x,y) in enumerate(zip(eneArray,timeArray)):
        plt.scatter(x,y,c=colors[i],marker=markers[i],label=ticklabels[i])

    ### Label figure. Label xticks before plot for better spacing.
    plt.title(plttitle,fontsize=20)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
    #plt.xticks(x,ticklabels,fontsize=12,rotation=-20, ha='left')
    #plt.yticks(y,ticklabels,fontsize=12)
    plt.xlabel("RMS error (kcal/mol)",fontsize=14)
    plt.ylabel("log ratio of wall time",fontsize=14)

    ### Edit legend colors. All is one color since each sublist
    # colored by spectrum.
    ax = plt.gca()
    leg = ax.get_legend()
    for i in range(len(eneArray)):
        leg.legendHandles[i].set_color(colors[i])

    ### Save/show plot.
    plt.gcf().set_size_inches(8,6)
    plt.savefig(figname,bbox_inches='tight')
#    plt.show()
    plt.clf()



### ------------------- Parser -------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input",
        help="Required input text file with info on dat files and associated \
              levels of theory to process. Number of entries in input file \
              MUST match number of columns in each of the dat files.\
              Input file should be analogous to input file for minima matching\
              except the files should point to the relative energies .dat file.")

    parser.add_argument("--eheatplot", default=None,
        help="Specify molecule title and generate heat map of RMS errors. \
              RMS error line is pulled from each file for plotting.")

    parser.add_argument("--theatplot", default=None,
        help="Specify molecule title and generate heat map of relative opt times.\
              Data with relative times are pulled from each file for plotting.")

    parser.add_argument("--etscatter", default=None,
        help="Specify molecule title and generate heat map of relative opt times.")


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


    # ========================================================================= 
    if opt['eheatplot'] is not None:
        rmsArray = []
        for infile in sdfList:
            with open(infile) as f:
                for line in f:
                    if "RMS error" in line:
                        rmse = next(itertools.islice(f,1))
                        rmse = [float(s) for s in rmse.split()[1:]]
                        rmsArray.append(rmse)
                        break
        rmsArray = shiftArray(rmsArray)
        plotHeatRMSE(opt['eheatplot'],rmsArray,thryList)

    if opt['theatplot'] is not None:
        rmsArray = []
        for infile in sdfList:
            with open(infile) as f:
                for line in f:
                    if "avg time" in line:
                        ravgs = itertools.islice(f,3) # ratio line via iterator 
                        for j in ravgs:            # get last item of iterator
                            pass
                        ravgs = [float(s) for s in j.split()[1:]]
                        rmsArray.append(ravgs)
                        break
        rmsArray = shiftArray(rmsArray)
#        rmsArray = [item[:-1] for item in rmsArray] # ================== * REMOVE last element from all
        plotHeatRMSE(opt['theatplot'],np.log10(rmsArray),thryList, ptitle='Log ratio of wall times',fprefix='times',colors='seismic')
#        plotHeatRMSE(opt['theatplot'],rmsArray,thryList, ptitle='ratio of wall times',fprefix='times')

    if opt['etscatter'] is not None:
        eArray = []
        tArray = []
        for infile in sdfList:
            with open(infile) as f:
                for line in f:
                    if "RMS error" in line:
                        rmse = next(itertools.islice(f,1))
                        rmse = [float(s) for s in rmse.split()[1:]]
                        eArray.append(rmse)
                    if "avg time" in line:
                        ravgs = itertools.islice(f,3) # ratio line via iterator 
                        for j in ravgs:            # get last item of iterator
                            pass
                        ravgs = [float(s) for s in j.split()[1:]]
                        tArray.append(ravgs)
                        break
        eArray = shiftArray(eArray)
        tArray = shiftArray(tArray)
#        eArray = [item[:-1] for item in eArray] # ================== * REMOVE last element from all
#        tArray = [item[:-1] for item in tArray] # ================== * REMOVE last element from all
        for i in range(len(sdfList)):
#            if i<13: continue
            plotET(opt['etscatter'],eArray[i],np.log10(tArray[i]),thryList,fprefix='scatter'+str(i+1))
