# DockCoV2
The current state of the COVID-19 pandemic is a global health crisis. To fight the novel coronavirus, one of the best-known ways is to block enzymes essential for virus replication. Currently, we know that the SARS-CoV-2 virus encodes about 29 proteins such as spike protein, 3C-like protease (3CLpro), RNA-dependent RNA polymerase (RdRp), Papain-like protease (PLpro), and nucleocapsid (N) protein. SARS-CoV-2 uses human angiotensin-converting enzyme 2 (ACE2) for viral entry and transmembrane serine protease family member II (TMPRSS2) for the spike protein priming. Thus in order to speed up the discovery of therapeutic agents, we develop DockCoV2, a drug database for SARS-CoV2. DockCoV2 focuses on predicting the binding affinity of FDA-approved and Taiwan National Health Insurance (NHI) drugs with the seven proteins mentioned above. This database contains a total of 3,109 drugs. DockCoV2 is easy to use and search against, is well cross-linked to external databases, and provides state-of-the-art prediction results in one site. Users can download their drug-protein docking data of interest and examine additional drug-related information on DockCoV2. Furthermore, DockCoV2 provides validation information to help users understand which drugs have already been reported to be effective against MERS or SARS-CoV.

<img src="https://github.com/ailabstw/DockCoV2/blob/master/DockCoV2.png" width="100%" height="100%">

Figure. The overview of the database content. In addition to the docking scores, DockCoV2 designed a joint panel section to provide the following related information: Docking structure, Ligand information, and Experimental data

## Dependencies
Here is the dependency list for running the proposed pipeline in DockCoV2. Due to license issue, please download all of the 3rd-party packages for your own. For the docker user, please refer the [Dockerfile](https://github.com/ailabstw/DockCoV2/blob/master/script/Dockerfile) in this repo to setup the environment.

* [Openbabel 3.0.0](https://github.com/openbabel/openbabel/releases/tag/openbabel-3-0-0)
* [AutodockTool 1.5.7](https://anaconda.org/InsiliChem/autodocktools-prepare/files)
* [AutoDock Vina 1.1.2](http://vina.scripps.edu/download.html)
* [SDF Downloader](https://github.com/ailabstw/DockCoV2/blob/master/script/download_sdf.py)

## Usage Example
```
python path_to/FindDock.py 
    -r path_to/receptor.pdb \ 
    -l path_to/ligand_list.txt \
    -o path/output_folder \
    -d path_to/dowenload_sdf.py \
    -b path_to/bin/obabel \
    -a path_to/AutoDockTools/ \
    -v path_to/bin/vina
```

The content in ligand list can be multipe drugs in interest, and one drug per line. For example:
```
Dactinomycin
Irinotecan
Gramicidin
```

For checking all the optional arguments, please use --help:
```
python path_to/FindDock.py -h
```

You will obtain the following argument list:
```
usage: FindDock [-h] -r R [-s S] (-l L | -k K) -o O [-n N] [-t T] -d D -b B -a A -v V

FindDock is a batch AutoDock Vina runner for the candidate drugs or a keyword developed by Yu-Chuan (Chester) Chang & all member of the Genomics Team at AILabs in Taiwan.

optional arguments:
  -h, --help  show this help message and exit
  -r R        the filename of receptor's .pdb file
  -s S        the filename of the active site list
  -l L        the filename of the ligand list
  -k K        the filename of the keyword
  -o O        the output filepath
  -n N        the number of replicates
  -t T        the number of threads
  -d D        the path of the script for downloading
  -b B        the path of openbabel
  -a A        the path of autodock tool
  -v V        the path of autodock vina
```

## Citing
Please considering cite the following paper if you use DockCoV2 in a scientific publication:

[1] Ting-Fu Chen<sup>†</sup>, Yu-Chuan Chang<sup>†</sup>, Yi Hsiao<sup>†</sup>, Ko-Han Lee<sup>†</sup>, Yu-Chun Hsiao, Yu-Hsiang Lin, Yi-Chin Ethan Tu, Hsuan-Cheng Huang, Chien-Yu Chen<sup>``*``</sup>, Hsueh-Fen Juan<sup>``*``</sup>., DockCoV2: a drug database against SARS-CoV-2, Nucleic Acids Research (2020), gkaa861, https://doi.org/10.1093/nar/gkaa861
