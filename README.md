# CQGym-mec: Joint Scheduling of MEC and HPC tasks

## Background 
Multi-access Edge Computing (MEC) and High Performance Computing (HPC) tasks are jointly scheduled on supercomputers. This repository utilizes Reinforcement Learning (LR) to jointly schedule these tasks.

## CQGym-mec
CQGym-mec is developed based on [CQGym](https://github.com/SPEAR-UIC/CQGym). 

## Features
TBD

## Modules
TBD

## Usages
The first train episode
```
python cqsim.py -j train.swf -n train.swf -R 1500 --is_training 1 --output_weight_file pg0 --rl_alg PG
```
The second train episode
```
python cqsim.py -j train.swf -n train.swf -r 1501 -R 1500 --is_training 1 --input_weight_file pg0 --output_weight_file pg1 --rl_alg PG
```

Validation using the first episode output
```
python cqsim.py -j validate.swf -n validate.swf -R 5000 --is_training 0 --input_weight_file pg0 --rl_alg PG
```

Validation using the second episode output
```
python cqsim.py -j validate.swf -n validate.swf -R 5000 --is_training 0 --input_weight_file pg1 --rl_alg PG
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