# xptl
Experiment Tool for Hyper Parameter Searches

## Requirements
* Python 3

## Usage
To run your experiments, use the following syntax:
```sh
python xptl.py INPUT [BATCH_CMD] [JOB_FILE]
```
INPUT is the path to your ini-file or a directory containing ini-files. BATCH_CMD is the command that queues a job for your scheduler. Default is `sbatch` for SLURM. JOB_FILE is your job script. Default is `job.sh`.

Using the script on our exemplary ini-files runs the following commands:
```sh
```
The script generates a job name, containing all parametes without spaces. The `-J` argument passes this name to your scheduler.
It is also passed to your job script as a first argument followed by all other hyperparameters as additional arguments.

An exemplary job file could look like this:
```sh
#!/bin/bash

# Some parametes for the scheduler:
# SBATCH --time=120:00:00
# ...
 
# Some initialization
mkdir output/$1

# Start your experiment passing all your parameters to a python script using $@
python experiment.py --output_dir=output/$@

echo exiting

exit 0
```
Note that in this example, the job name gets passed to the experiment as a path for output files in order to keep an organized structure.
