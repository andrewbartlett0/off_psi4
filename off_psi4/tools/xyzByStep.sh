#!/bin/bash
# usage: ./xyzByStep.sh 5 infile.dat outfile.xyz [replace 5 with numAtoms]

grep -i -A $1 'Cartesian Geometry' $2 | sed -e '/Geometry/d' -e 's/^[ \t]*//' -e "s/--/$1\n/"  > $3
sed -i "1i$1\n" $3
