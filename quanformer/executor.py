#!/usr/bin/env python

import os, sys
import argparse

import smi2confs
import filterConfs
import confs2psi
import getPsiResults


def main(**kwargs):
    _, extension = os.path.splitext(opt['filename'])
    adir, fname = os.path.split(opt['filename'])
    hdir = os.getcwd()
    if adir == '' or adir is None or adir == '.':
        fullname = os.path.join(hdir,opt['filename'])
    else:
        fullname = opt['filename']
    base = fname.replace('-', '.').split('.')[0]

    if opt['setup']:

        # MM opt and filter
        if extension == '.smi':
            print("\nGenerating and filtering conformers for %s" % opt['filename'])
            msdf = base + '.sdf'
            smi2confs.smi2confs(os.path.join(hdir,opt['filename']))
            filterConfs.filterConfs(os.path.join(hdir, msdf), "MM Szybki SD Energy", suffix='200')
            msdf = base+'-200.sdf'
        else:
            msdf = fullname

        # generate Psi4 inputs
        print("\nCreating Psi4 input files for %s..." % base)
        confs2psi.confs2psi(msdf,opt['method'],opt['basisset'],opt['calctype'],opt['mem'])


    else:  # ========== AFTER QM =========== #

        # specify output file name
        if "220" not in fname:
            osdf = os.path.join(hdir,base + '-210.sdf')
            suffix = '220'
        else:
            osdf = os.path.join(hdir,base + '-221.sdf')
            suffix = '222'

        # get psi4 results
        print("Getting Psi4 results for %s ..." %(fname))
        method, basisset = getPsiResults.getPsiResults(fullname, osdf, calctype=opt['calctype'])

        # only filter structures after optimization calculations
        # spe/hess should not change geometries
        if opt['calctype'] == 'opt':

            # if didn't go through getPsiResults (e.g., output file already exists
            # then look for method from command line call for filtering
            if None in [method, basisset]:
                if None in [opt['method'], opt['basisset']]:
                    print("\nERROR: no results obtained and no conformers filtered. "
                          "If you want to filter an already-existing output file, "
                          "specify method and basis set in command line call with "
                          "-m [method] -b [basis]\n")
                    return
                else:
                    method = opt['method']
                    basisset = opt['basisset']

            tag = "QM Psi4 Final Opt. Energy (Har) %s/%s" % (method, basisset)
            print("Filtering Psi4 results for %s ..." %(osdf))
            filterConfs.filterConfs(osdf, tag, suffix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    req = parser.add_argument_group('required arguments')

    req.add_argument("-f", "--filename",
        help="SDF file (with FULL path) to be set up or processed.")

    # setup calculations or process results for specified calctype
    parser.add_argument("--setup", action="store_true", default=False,
        help=("If True (default=False), generate and filter conformers (if "
              "starting from *.smi), then generate Psi4 input files."))
    parser.add_argument("--results", action="store_true", default=False,
        help=("If True (default=False), process Psi4 output files and filter "
              "conformers."))
    parser.add_argument("-t", "--calctype", default="opt",
        help=("Specify either 'opt' for geometry optimizations, 'spe' for "
             "single point energy calculations, or 'hess' for Hessian "
             "calculations. Default is 'opt'."))

    # qm job detail
    req.add_argument("-m", "--method",
        help="Name of QM method. Put this in 'quotes'.")
    req.add_argument("-b", "--basisset",
        help="Name of QM basis set. Put this in 'quotes'.")
    parser.add_argument("--mem", default="5.0 Gb",
        help="Memory specification for each Psi4 calculation.")

    args = parser.parse_args()
    opt = vars(args)


    # check that both 'setup' and 'spe' are not both true or both false
    if opt['setup'] == opt['results']:
        raise parser.error("Specify exactly one of either --setup or --results.")

    # check that input file exists
    if not os.path.exists(opt['filename']):
        raise parser.error("Input file %s does not exist. Try again." % opt['filename'])

    # check that specified calctype is valid
    if opt['calctype'] not in {'opt','spe','hess'}:
        raise parser.error("Specify a valid calculation type.")

    main(**opt)

