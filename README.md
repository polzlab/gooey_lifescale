## Peak Caller for LifeScale



### install dependencies

 make sure you have conda installed:

    # in a terminal, type:
    which conda
    # if conda is not found:
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash ./Miniconda3-latest-Linux-x86_64.sh
    # restart your terminal, and then run:
    conda init

Once conda is in order, create an environment with these dependencies:

    conda create --name gooey_lifescale --file requirements.txt


### running this software:

    conda activate gooey_lifescale
    python peak_caller_gui.py
    




