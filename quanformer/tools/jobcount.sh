#!/bin/bash

# Purpose: This bash script can be used to calculate the number of jobs.

# examples of searching in particular paths
#ALL_JOBS=$(find ./ -mindepth 2 -maxdepth 2 -type d -not -path "*/testmol1/*")
#ALL_JOBS=$(find ./ -mindepth 2 -path "*/chains/AlkEthOH_c1178/*" -path "*mp2*" -path "*def2-tzvp*" -type f -name "timer.dat")

ALL_JOBS=$(find ./ -mindepth 2 -maxdepth 2 -type d)
ALL_JOBS_ARRAY=($ALL_JOBS)

REM_JOBS=$(find ./ -mindepth 2 -type d '!' -exec test -e "{}/timer.dat" ';' -print)
REM_JOBS_ARRAY=($REM_JOBS)

printf "\n\nTOTAL DIRECTORY SIZE: ${#ALL_JOBS_ARRAY[@]}"
printf "\nTOTAL NUMBER OF JOBS FOUND: ${#REM_JOBS_ARRAY[@]}\n\n"

# print list of all jobs
echo ${ALL_JOBS_ARRAY[@]}

# print first job in array
echo ${ALL_JOBS_ARRAY[0]}

# print Nth job in array
echo ${ALL_JOBS_ARRAY[417]}

