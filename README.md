# xptl
Experiment Tool for Hyper Parameter Searches

## Requirements
* Python 3.6

## Installation
You can install the package directly from GitHub using pip:
```sh
pip install git+https://github.com/titus-leistner/xptl.git
```

## Usage
To define your command line arguments, create one or several ini-files. Here is an example:
```ini
# inis/config1.ini

[meta]
execute=no

[training]
learning_rate=0.01
batch_size=128
```
The `batch_size` is defined in our "parent" ini-file, therefore it is the same for all experiments in this example.
However, we want to try two different loss functions. We therefore create two additional files:
```ini
# inis/config2.ini

[meta]
parent=config1.ini
prefix=L1 Experiment

[training]
loss=L1
```
and
```ini
# inis/config3.ini

[meta]
parent=config1.ini
prefix=MSE Experiment

[training]
loss=MSE
learning_rate=0.0001
```
Note, that we include `parent=config1.ini` to inherit all arguments from our first file.
Both children inherit the `batch_size`, but define a different `loss` parameter.
For the MSE loss we notice that our learning rate is way too high, we therefore override the inherited `learning_rate` and try a lower number.

Now we can either execute one experiment by calling e.g. `xptl inis/config3` or all experiments at once with `xptl inis/`.
As our "parent" ini-file should not execute an experiment, we add `execute=no`.


To run your experiments, use the following syntax:
```sh
xptl INPUT [BATCH_CMD] [JOB_FILE]
```
INPUT is the path to your ini-file or a directory containing ini-files. BATCH_CMD is the command that queues a job for your scheduler. Default is `sbatch` for SLURM. JOB_FILE is your job script. Default is `job.sh`.

Using the script on our exemplary directory of ini-files runs the following commands:
```sh
sbatch -J L1_Experiment-training_learning_rate=0.01-training_batch_size=128-training_loss=L1 job.sh L1_Experiment-training_learning_rate=0.01-training_batch_size=128-training_loss=L1  --training_learning_rate=0.01 --training_batch_size=128 --training_loss=L1

sbatch -J MSE_Experiment-training_learning_rate=0.0001-training_batch_size=128-training_loss=MSE job.sh MSE_Experiment-training_learning_rate=0.0001-training_batch_size=128-training_loss=MSE  --training_learning_rate=0.0001 --training_batch_size=128 --training_loss=MSE
```
The script generates a job name, either defined as `name` in the `[meta]` section, or containing all parameters without spaces. Optionally a prefix to this jobname can be defined as `prefix` in the `[meta]` section. The `-J` argument passes this name to your scheduler.
It is also passed to your job script as a first argument followed by all other hyperparameters as additional arguments.

An exemplary job file could look like this:
```sh
#!/bin/bash

# Some parametes for the scheduler:
# SBATCH --time=120:00:00
# ...
 
# Create output directory for your experiment
mkdir output/$1

# Start your experiment passing all your parameters to a python script using $@
python experiment.py --output_dir=output/$@

echo exiting

exit 0
```
Note that in this example, the job name gets passed to the experiment as a path for output files in order to keep an organized structure.
