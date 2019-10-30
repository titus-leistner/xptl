import sys
import string
import os
import configparser
import copy

usage = """
Usage: xptl INPUT [BATCH_CMD] [JOB_FILE]

INPUT       An ini-style config file with commandline parameters. The config file can inherit from other config files by setting the parent=relative/path/to/parent.ini in the [meta]-section. See https://github.com/titus-leistner/xptl for examples.
        
BATCH_CMD   Command to schedule a job. Default is "sbatch" for SLURM

JOB_FILE    The job script. Default is "job.sh"
"""

META = 'meta'
PARENT = 'parent'
PREFIX = 'prefix'
EXECUTE = 'execute'
SPLIT = '%'


def parse_ini(fname):
    """
    Load a tree of ini files and build up dictionary tree

    :param fname: filename of an ini file
    :type data: str

    :return dict of arguments
    """
    # read config file
    try:
        config = configparser.ConfigParser()
        config.read(fname)
    except configparser.Error as err:
        print(f'Error: Cannot parse {fname}: {err}')
        return None

    if len(config.sections()) < 1:
        print(f'Error: {fname} is empty or does not exist.')
        return None

    data = {}
    for section in config.sections():
        for key in config[section]:
            data[f'{section}_{key}'] = config[section][key]

    if not f'{META}_{EXECUTE}' in data.keys():
        data[f'{META}_{EXECUTE}'] = 'yes'

    # load parent if necessary
    if META in config.sections():
        if PARENT in config[META].keys():
            parent_fname = config[META][PARENT]
            parent_fname = os.path.join(os.path.dirname(fname), parent_fname)

            # recursively update parent args with child args
            parent_data = parse_ini(parent_fname)
            if parent_data is None:
                return None

            parent_data.update(data)
            data = parent_data

    return data


def parse_args(data):
    """
    Parse dictionary to extract params for experiments

    :param data: the parameter dictionary
    :type data: dict

    :return parameters as string
    """
    # build string of arguments
    args = ''
    path = ''
    for k, v in data.items():
        if k.startswith(f'{META}_'):
            continue
        if isinstance(v, bool):
            if v:
                args += f' --{k}'
                path += f';{k}'
        elif True in [c in v for c in string.whitespace]:
            args += f' --{k}="{v}"'
            path += f'{SPLIT}{k}={"_".join(v.split())}'
        else:
            args += f' --{k}={v}'
            path += f'{SPLIT}{k}={v}'

    # format path, omit path seperators

    path = path[1:]
    path = '-'.join(path.split(os.sep))

    prefix = data.get(f'{META}_{PREFIX}', '')
    if prefix:
        path = f'{prefix}{SPLIT}{path}'

    args = f'{path} {args}'

    return args


def run_job(fname, batch, job):
    """
    Load parameters from ini-style config file and run the job

    :param fname: path to ini
    :type fname: str

    :param batch: batch command
    :type batch: str

    :param job: path to jobfile
    :type job: str
    """
    data = parse_ini(fname)
    if data is None:
        return

    if data[f'{META}_{EXECUTE}'] == 'no':
        return

    args = parse_args(data)

    name = args.split()[0]
    cmd = f'{job} {args}'

    if batch:
        cmd = f'{batch} -J {name} {cmd}'

    print('>', cmd)
    os.system(cmd)


def main():
    # parse arguments
    batch = 'sbatch'
    job = 'job.sh'

    if len(sys.argv) < 2:
        print(usage)
        exit()
    if len(sys.argv) > 2:
        batch = sys.argv[2]
    if len(sys.argv) > 3:
        job = sys.argv[3]

    fname = sys.argv[1]

    fnames = [fname]
    if os.path.isdir(fname):
        fnames = os.listdir(fname)
        fnames = [os.path.join(fname, f) for f in fnames]
        fnames = [f for f in fnames if f.endswith(
            '.ini') or f.endswith('.cfg') or f.endswith('.conf')]

    for fname in fnames:
        run_job(fname, batch, job)


if __name__ == '__main__':
    main()
