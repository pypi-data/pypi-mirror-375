# neofind

Discover and analyze neoantigens using RNA, Ribo, and WES/WGS sequence data.
<!-- TOC -->

- [neofind](#neofind)
- [Overview](#overview)
- [Requirements](#requirements)
- [neofind modules](#neofind-modules)
    - [neofind gene](#neofind-gene)
    - [Usage](#usage)
- [Docker](#docker)
- [Conda Environment](#conda-environment)
- [Cite neofind](#cite-neofind)

<!-- /TOC -->

# Overview

neofind is a pipeline for discovering and analyzing neoantigens using RNA, Ribo, and WES/WGS sequence data. 

It is recommended to use the docker or conda environment to run the pipeline.

# Requirements

1. Python 3.10+
2. Python modules:
    - pandas
    - numpy
    - scipy
    - sklearn
    - matplotlib
    - seaborn
    - pysam
3. minimap2
4. samtools
5. bedtools

# neofind modules

The main module of neofind, which includes the following sub-modules:
- gene
- count
- ployA
- matrix
- detectMod
- nascentRNA

## neofind gene

## Usage

`neofind gene -i ../input/{}/pass.fq.gz -r ../reference/fasta/genome.fa -o ./{}_gene.sam --parms '--secondary=no --cs -a --sam-hit-only'`


# Docker

If the user has docker installed, the following command can be used to run the pipeline in a docker container:

```
docker run -v /path/to/data:/data -it neofind/neofind:latest /bin/bash
```

# Conda Environment

If the user has conda installed, the following command can be used to create a conda environment for neofind:

1. Install conda
2. Create a new conda environment: `conda create -n neofind python=3.12`
3. Activate the environment: `conda activate neofind`
4. Install the required packages: `conda install -c bioconda minimap2 samtools bedtools`
5. Install the required python packages: `pip install pandas numpy scipy sklearn matplotlib seaborn pysam`
6. Clone the neofind repository: `git clone https://github.com/LegendZDY/neofind.git`

# Cite neofind

If you use neofind in your research, please cite the following paper: