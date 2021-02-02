# Is there a trade-off between compactness and homogeneity?

## Introduction

This GitHub repo contains all the data and code for my undergraduate political
science thesis.

It requires some data in a shared repo I have with Prof. Nick Eubank,
[geographically_sensitive_dislocation](https://github.com/nickeubank/geographically_sensitive_dislocation),
because I don't want to duplicate the data files. I'll have to find a better
way to store this data.

My political science thesis is entitled "Is there a trade-off between
compactness and homogeneity?". You can find it in the `40_docs` folder. Here is
the introduction:

> Research shows that districts that consist of more homogeneous groups of voters
achieve better representation on several dimensions. And many statutes require
that districts be "reasonably compact". However, some have argued that
requiring compactness may come at the cost of district homogeneity by drawing
districts without regard for communities of interest, which has deletrious
effects on democratic outcomes like representation and responsiveness. Are
compactness and homogeneity fundamentally conflicting goals? Are some measures
of compactness more consistent with homogeneity than others? 
> 
> I make two contributions in this work. First, I develop a new compactness
metric (*human compactness*) that improves upon previous measures by
incorporating a notion of travel times. Second, I use a Markov Chain Monte
Carlo (MCMC) approach to generate a large sample of districting plans and
consider empirically how compactness and homogeneity trade off with one
another. I find no trade-off between compactness and homogeneity across all
four compactness measures I examine. I further find that my human compactness
measure consistently produces more homogeneous districts, suggesting that a
judicious choice of compactness metric can in fact encourage better electoral
outcomes.

The results (mostly plots) are all available in `30_results`, and as a
robustness check I also run the results with a different aggregation function,
in `31_results_rc`.

## How to set up    

On a new environment:

```bash
git clone https://github.com/lieuzhenghong/human-compactness
# setup conda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -u
cd human-compactness/
conda config --add channels conda-forge
conda config --set pip_interop_enabled True
# Create conda environment from file
conda env create -f new_environment.yml
# Activate the conda environment
conda activate hc-env
# We need some files 
git lfs install
git lfs pull
# Now run the tests and make sure everything passes
PROJ_NETWORK=OFF python -m test_process_ensembles.py -vv -s
```