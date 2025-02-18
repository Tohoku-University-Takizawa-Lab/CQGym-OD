# CQGym-OD: Joint Scheduling of on-demand and rigid jobs in HPC systems

## Background 
Recently, on-demand and rigid jobs are jointly scheduled in High Performance Computing (HPC) systems. This repository utilizes Reinforcement Learning (LR) to jointly schedule these jobs.

## CQGym-OD
CQGym-OD is developed based on [CQGym](https://github.com/SPEAR-UIC/CQGym). 

## Features
The scheduling result is evaluated.

## Modules
- Evaluate.py (Newly Designed)
  - Evaluate the scheduling results.

## Usages
train DQL model `dql0` using the first 1,500 traces of SDSC-SP2-1998-4-2-cln.swf 
```
python cqsim.py -j SDSC-SP2-1998-4-2-cln.swf -n SDSC-SP2-1998-4-2-cln.swf -R 1500 --is_training 1 --output_weight_file dql0 --rl_alg DQL 
```
train DQL model `dql1` based `dql0` using trace 1501~3000 of SDSC-SP2-1998-4-2-cln.swf 
```
python cqsim.py -j SDSC-SP2-1998-4-2-cln.swf -n SDSC-SP2-1998-4-2-cln.swf -r 1501 -R 1500 --is_training 1 --input_weight_file dql0 --output_weight_file dql1 --rl_alg DQL
```
test the performance of `dql0` using trace 3001~8000 of SDSC-SP2-1998-4-2-cln.swf 
```
python cqsim.py -j SDSC-SP2-1998-4-2-cln.swf -n SDSC-SP2-1998-4-2-cln.swf -r 3001 -R 5000 --is_training 0 --input_weight_file dql0 --rl_alg DQL
```
test the performance of `dql1` using trace 3001~8000 of SDSC-SP2-1998-4-2-cln.swf 
```
python cqsim.py -j SDSC-SP2-1998-4-2-cln.swf -n SDSC-SP2-1998-4-2-cln.swf -r 3001 -R 5000 --is_training 0 --input_weight_file dql1 --rl_alg DQL
```

## Environments

Hardware & OS.
|Environment|version|
|--|--|
|MBP14, M1 Pro|2021|
|OS X Sonoma|14.1|
|X Code|15.1|

Python package.
|Environments|version|
|--|--|
|Python | 3.9.6 |
|Packages| [link](./packages.md)|