git clone https://github.com/lieuzhenghong/human-compactness
git clone https://github.com/nickeubank/geographically_sensitive_dislocation
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
cd dev/human-compactness/
conda install --channel conda-forge geopandas
conda install --channel conda-forge matplotlib
conda install --channel conda-forge maup
conda install --channel conda-forge gerrychain
conda install --channel conda-forge docopt
conda install --channel conda-forge scipy

