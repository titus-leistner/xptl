# xptl
Experiment Tool for Hyper Parameter Searches

## Requirements
* Python 3

## Usage
To define your command line arguments, create a JSON file. Here is an example:
```json
{
    "lr": [0.1, 0.01],
    "bs": 128,
    "_exec": false,
    "L1 Experiment":{
        "loss": "L1"
    },
    "MSE Experiment":{
        "loss": "MSE",
        "lr": [0.001, 0.0001, 0.00001]
    }
}
```
The batch size is in the root object, therefore it is the same for all experiments in this example.
However, we want to try two different learning rates. We define `"lr"` as an array, which means that one experiment per element should be launched.
As we also want to try two different loss functions, we define two child objects. Both inherit the `"bs"` parameter, but define a different `"loss"` parameter. For the MSE loss we notice that our learning rate is way too high, we therefore override the inherited `"lr"` parameter and try three different values.
As the root object should not execute an experiment, we add `"_exec": false`.

To run your experiments, use the following syntax:
```sh
python xptl.py INPUT [BATCH_CMD] [JOB_FILE]
```
INPUT is the path to your JSON file. BATCH_CMD is the command that queues a job for your scheduler. Default is `sbatch` for SLURM. JOB_FILE is your job script. Default is `job.sh`.

Using the script on our exemplary JSON file runs the following commands:
```sh
sbatch -J loss=L1_lr=0.1_bs=128 job.sh loss=L1_lr=0.1_bs=128  --loss=L1 --lr=0.1 --bs=128

sbatch -J loss=L1_lr=0.01_bs=128 job.sh loss=L1_lr=0.01_bs=128  --loss=L1 --lr=0.01 --bs=128

sbatch -J loss=MSE_lr=0.001_bs=128 job.sh loss=MSE_lr=0.001_bs=128  --loss=MSE --lr=0.001 --bs=128

sbatch -J loss=MSE_lr=0.0001_bs=128 job.sh loss=MSE_lr=0.0001_bs=128  --loss=MSE --lr=0.0001 --bs=128

sbatch -J loss=MSE_lr=1e-05_bs=128 job.sh loss=MSE_lr=1e-05_bs=128  --loss=MSE --lr=1e-05 --bs=128
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
