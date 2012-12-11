### Job Name
#PBS -N test_pbs_mpich
### submits the job to the small queue
#PBS -q small 
### requests 3 nodes
#PBS -l nodes=3
### Output files
#PBS -o test_pbs_mpich.log
#PBS -e test_pbs_mpich.err
### Declare job non-rerunable
#PBS -r n

# Print the name of the node on which this script has started and the time.
echo "###################################################################"
echo "Starting on `hostname` at `date`"

# The environment variable $PBS_NODEFILE lists the name of a file containe
# a list of the nodes that are available to this job.
# The mpirun command will use $PBS_NODEFILE for its machinefile.
# See the mpirun man page for details.
if [ -n "${PBS_NODEFILE}" ]; then
  if [ -f ${PBS_NODEFILE} ]; then
    # print the nodenames.
    echo 
    echo "Nodes used for this job:"
    echo "------------------------"

    cat ${PBS_NODEFILE}
    # Count the number of lines in $PBS_NODEFILE so that we can get the 
    # number of available processors. Put this in the $NP variable.
    # Unfortunately, PBS doesn't give us this information automagically.
    set -- `wc -l ${PBS_NODEFILE}`
    NP=$1
  fi
fi

# Change to a subdirectory if necessary
# cd ${PBS_WORK_DIR}
echo ""
echo "Output of ended jobs"
echo "--------------------"
if [ -x test_mpi.mpich ]; then
mpirun -machinefile ${PBS_NODEFILE} -np ${NP} ./test_mpi.mpich
else
echo "test_mpi.mpich script not available !"
fi

# print end time
echo 
echo "Job Ended at `date`"
echo "###################################################################"
# Exit
exit 0
