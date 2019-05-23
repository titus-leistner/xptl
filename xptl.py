import sys
import os
import json
import copy

usage = """
Usage: python xptl.py INPUT [BATCH_CMD] [JOB_FILE]

INPUT       JSON file with command line parameters. Objects inside of objects are interpreted as new experiments and inherit parameters of parent. Each element of an array starts a new experiment. Use '"_exec": false' to prevent a specific object in the inheritence hierarchie from being executed.
        
BATCH_CMD   Command to schedule a job. Default is "sbatch" for SLURM

JOB_FILE    The job script. Default is "job.sh"
"""

def parse_args(data):
    """
    Parse dictionary to extract params for experiments

    :param data: the parameter dictionary
    :type data: dict

    :return list of parameter strings
    """
    excs = []

    # parse dict
    # parse children
    childs = []
    for k, v in data.items():
        if isinstance(v, dict):
            # recursion for child node
            child = copy.deepcopy(v)
            childs.append(k)

            # inherit pairs from parent
            for k, v in data.items():
                if not k in child.keys() and not isinstance(v, dict) and k != '_exec':
                    child[k] = v
            excs += parse_args(child)

    # remove children from dict
    for child in childs:
        del data[child]

    # parse lists
    for k, v in data.items():
        if isinstance(v, list):
            # iterate over list for one parameter
            for e in v:
                child = copy.deepcopy(data)
                child[k] = e
                excs += parse_args(child)
            return excs
    
    # return if current node should not be executed
    if '_exec' in data.keys(): 
        if not data['_exec']:
            return excs
        del data['_exec']
    
    # build string of arguments
    args = ''
    path = ''
    for k, v in data.items():
        if isinstance(v, dict):
            continue
        elif isinstance(v, bool):
            if v:
                args += f' --{k}'
                path += f'_{k}'
        else:
            args += f' --{k}={v}'
            path += f'_{k}={v}'

    path = path[1:]
    args = f'{path} {args}'
    excs.append(args)

    return excs

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
    
    data = None
    try:
        with open(fname) as f:
            data = json.load(f) 
    except IOError as err:
        print('IOError: ', err)
        exit(-1)
    except ValueError as err:
        print('Error while parsing JSON: ', err)
        exit(-1)

    for args in parse_args(data):
        name = args.split()[0]
        cmd = f'{job} {args}'
        
        if batch:
            cmd = f'{batch} -J {name} {cmd}'


        print('>', cmd)
        os.system(cmd)

if __name__ == '__main__':
    main()
