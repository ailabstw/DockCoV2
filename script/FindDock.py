# -*- coding: utf-8 -*-
"""
Created on Feb 2020

@author: Chester (Yu-Chuan Chang)
"""

""""""""""""""""""""""""""""""
# import libraries
""""""""""""""""""""""""""""""
import argparse
import os
import sys
import subprocess
from threading import Timer
import collections
import itertools
import ipywidgets
import nglview

""""""""""""""""""""""""""""""
# define class and function
""""""""""""""""""""""""""""""
def ArgumentsParser():
    ### define arguments
    str_description = ''
    str_description += 'FindDock is a batch AutoDock Vina runner for the candidate drugs or a keyword '
    str_description += 'developed by Yu-Chuan (Chester) Chang & all member of the Genomics Team at AILabs in Taiwan. '
    parser = argparse.ArgumentParser(prog='FindDock', description=str_description)
    
    ### define arguments for I/O
    parser.add_argument("-r", required=True, help="the filename of receptor's .pdb file")
    parser.add_argument("-s", required=False, help="the filename of the active site list")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", required=False, help="the filename of the ligand list")
    group.add_argument("-k", required=False, help="the filename of the keyword")
    parser.add_argument("-o", required=True, help="the output filepath")
    
    ### define docking parameters
    parser.add_argument("-n", required=False, help="the number of replicates", default=1)
    parser.add_argument("-t", required=False, help="the number of threads", default=1)
    
    ### define arguments for 3rd-party tools
    parser.add_argument("-d", required=True, help="the path of the script for downloading")
    # https://github.com/openbabel/openbabel/releases/tag/openbabel-3-0-0
    parser.add_argument("-b", required=True, help="the path of openbabel")
    # https://anaconda.org/InsiliChem/autodocktools-prepare/files
    parser.add_argument("-a", required=True, help="the path of autodock tool")
    # http://vina.scripps.edu/download.html
    parser.add_argument("-v", required=True, help="the path of autodock vina")
    
    return parser

class Point:
    ### define a point on protein 3D struture space
    def __init__(self, x, y, z):
        self.chain = ""
        self.position = ""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        
    def __str__(self):
        return str(self.__dict__)

class Atoms(dict):
    ### atoms inherited from dictionary class
    ### example: dict_atom["A:121"] = Point(1, 1, 0))
    def __setitem__(self, key, val):
        if not isinstance(val, Point):
            raise TypeError("Atoms dict only accepts %s" % Point)
        list_key = key.split(":")
        val.chain = list_key[0]
        val.position = list_key[1]
        return super(Atoms, self).__setitem__(key, val)
    
    def get_center(self, *args, **kwargs):
        # select residues
        list_selection = kwargs.get('list_selection', None)
        if list_selection is not None:
            for key in list(super(Atoms, self).keys()):
                if key not in list_selection:
                    super(Atoms, self).pop(key)   
        # calculate center
        list_x = list()
        list_y = list()
        list_z = list()
        for key, val in super(Atoms, self).items():
            list_x.append(val.x)
            list_y.append(val.y)
            list_z.append(val.z)
        return [sum(list_x)/len(list_x), sum(list_y)/len(list_y), sum(list_z)/len(list_z)]
    
    def get_size(self, *args, **kwargs):
        # select residues
        list_selection = kwargs.get('list_selection', None)
        if list_selection is not None:
            for key in list(super(Atoms, self).keys()):
                if key not in list_selection:
                    super(Atoms, self).pop(key)
        # calculate size
        list_x = list()
        list_y = list()
        list_z = list()
        for key, val in super(Atoms, self).items():
            list_x.append(val.x)
            list_y.append(val.y)
            list_z.append(val.z)
        return [max(list_x)-min(list_x), max(list_y)-min(list_y), max(list_z)-min(list_z)]

""""""""""""""""""""""""""""""
# main function
""""""""""""""""""""""""""""""
def main(args=None):
    ### obtain arguments from argument parser
    args = ArgumentsParser().parse_args(args)

    ### load keyword file
    str_keyword = ""
    if args.k is not None:
        with open(args.k, "r") as file_inputFile:
            for line in file_inputFile:
                str_keyword = line.strip()
    
    ### load ligand
    list_ligand = []
    if args.l is not None:
        with open(args.l, "r") as file_inputFile:
            for line in file_inputFile:
                list_ligand.append(line.strip())
        str_ligand = ",".join(list_ligand)

    ### create temp folder
    str_filepath_temp = os.path.join(args.o, "temp")
    if not os.path.exists(str_filepath_temp):
        os.makedirs(str_filepath_temp)

    ### create sdf folder
    str_filepath_sdf = os.path.join(args.o, "sdf")
    if not os.path.exists(str_filepath_sdf):
        os.makedirs(str_filepath_sdf)
    
    ### call the script of sdf downloading
    str_command = "python " + args.d + " "
    str_command += "--search_term" + " '" + str_keyword + "' "
    str_command += "--search_ligand" + " '" + str_ligand + "' "
    str_command += "--output_folder" + " " + str_filepath_sdf
    os.system(str_command)
    
    ### create pdbqt folder
    str_filepath_pdbqt = os.path.join(args.o, "pdbqt")
    if not os.path.exists(str_filepath_pdbqt):
        os.makedirs(str_filepath_pdbqt)

    ### convert sdf to pdbqt
    list_sdf = []
    for file in os.listdir(str_filepath_sdf):
        if file.endswith(".sdf"):
            list_sdf.append(file)

    for idx, sdf in enumerate(list_sdf):
        ### split multiple molecules
        print("spliting..." + "(" + str(idx+1) + "/" + str(len(list_sdf)) + ")")
        # obabel exampe: /opt/build/bin/obabel -isdf /data/ting/amphotericin_b_m.sdf -omol2 -O /data/ting/amphotericin_b_m.mol2 -m
        str_command = args.b + " "
        str_command += "-isdf " + os.path.join(str_filepath_sdf, sdf) + " "
        str_command += "-omol2 -O " + os.path.join(str_filepath_temp, sdf.replace(".sdf", ".mol2")) + " -m"
        process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        process.wait()

        ### generate 3d structure
        print("3D structure generating..." + "(" + str(idx+1) + "/" + str(len(list_sdf)) + ")")
        # obabel exampe: /opt/build/bin/obabel -imol2 /data/ting/amphotericin_b_m1.mol2 -omol2 -O /data/ting/amphotericin_b_min.mol2 --gen3D slowest
        str_command = args.b + " "
        str_command += "-imol2 " + os.path.join(str_filepath_temp, sdf.replace(".sdf", "1.mol2")) + " "
        str_command += "-omol2 -O " + os.path.join(str_filepath_temp, sdf.replace(".sdf", ".min.mol2")) + " --gen3D slowest"
        process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        process.wait()
        
        ### convert mol2 3d structure to pdbqt
        print("pdbqt converting..." + "(" + str(idx+1) + "/" + str(len(list_sdf)) + ")")
        # /usr/local/lib/python2.7/site-packages/AutoDockTools/Utilities24/prepare_ligand4.py -l /data/ting/amphotericin_b_min.mol2 -o /data/ting/amphotericin_b.pdbqt
        str_command = os.path.join(args.a, "Utilities24", "prepare_ligand4.py") + " "
        str_command += "-l " + os.path.join(str_filepath_temp, sdf.replace(".sdf", ".min.mol2")) + " "
        str_command += "-A checkhydrogens "
        str_command += "-o " + os.path.join(str_filepath_temp, sdf.replace(".sdf", ".pdbqt")) + " "
        str_command += "-U nphs_lps_waters_nonstdres"
        os.chdir(str_filepath_temp)
        process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        #### timeout for python2
        kill = lambda process: process.kill()
        t_timeout = Timer(60, kill, [process])

        try:
            t_timeout.start()
            stdout, stderr = process.communicate()
        finally:
            t_timeout.cancel()

        ### move pdbqt file to pdbqt folder
        str_command = "mv " + os.path.join(str_filepath_temp, sdf.replace(".sdf", ".pdbqt")) + " "
        str_command += os.path.join(str_filepath_pdbqt)
        process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        process.wait()

    ### remove temp folder
    str_command = "rm -rf " + os.path.join(str_filepath_temp)
    process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    process.wait()

    ### convert receptor 3d structure to pdbqt
    print("pdbqt converting...")
    # /usr/local/lib/python2.7/site-packages/AutoDockTools/Utilities24/prepare_receptor4.py -r 6lu7.pdb -A checkhydrogens -o 6lu7.pdbqt -U nphs_lps_waters_nonstdres
    str_command = os.path.join(args.a, "Utilities24", "prepare_receptor4.py") + " "
    str_command += "-r " + args.r + " "
    str_command += "-A checkhydrogens "
    str_command += "-o " + os.path.join(args.o, os.path.basename(args.r) + ".pdbqt") + " "
    str_command += "-U nphs_lps_waters_nonstdres"
    os.chdir(args.o)
    process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    ### timeout for python2
    kill = lambda process: process.kill()
    t_timeout = Timer(60, kill, [process])

    try:
        t_timeout.start()
        stdout, stderr = process.communicate()
    finally:
        t_timeout.cancel()

    ### load active sites
    list_site = None
    int_extension = 10
    with open(args.s, "r") as file_inputFile:
        for line in file_inputFile:
            if list_site is None:
                list_site = []
            list_site.append(line.strip())

    ### load .pdb file
    dict_atom = Atoms()
    with open(os.path.join(args.o, os.path.basename(args.r) + ".pdbqt"), "r") as file_inputFile:
        for line in file_inputFile:
            if line.startswith("ATOM"):
                list_line = line.strip().split()
                # Set Atoms (Example: dict_atom["A:121"] = Point(1, 1, 0))
                dict_atom["{}:{}".format(list_line[4], list_line[5])] = Point(list_line[6], list_line[7], list_line[8])

    ### add search space
    list_center = dict_atom.get_center(list_selection=list_site)
    list_size = dict_atom.get_size(list_selection=list_site)

    ### extend search space
    if list_site is not None:
        list_size = [a + int_extension for a in list_size]

    ### adjust exhaustiveness parameter depend on the protein size
    int_exhaustiveness = int(2 * 8 * (float(list_size[0])/30) * (float(list_size[1])/30) * (float(list_size[2])/30))
    int_exhaustiveness = max(int_exhaustiveness, 150)
    with open(os.path.join(args.o, os.path.basename(args.r) + ".conf"), "w") as file_outputFile:
        file_outputFile.writelines("center_x = " + str(list_center[0]) + "\n")
        file_outputFile.writelines("center_y = " + str(list_center[1]) + "\n")
        file_outputFile.writelines("center_z = " + str(list_center[2]) + "\n")
        file_outputFile.writelines("size_x = " + str(list_size[0]) + "\n")
        file_outputFile.writelines("size_y = " + str(list_size[1]) + "\n")
        file_outputFile.writelines("size_z = " + str(list_size[2]) + "\n")
        file_outputFile.writelines("\n")
        file_outputFile.writelines("energy_range = " + "10" + "\n")
        file_outputFile.writelines("exhaustiveness = " + str(int_exhaustiveness) + "\n")
        file_outputFile.writelines("num_modes = " + "20" + "\n")
    
    ### create dock folder
    str_filepath_dock = os.path.join(args.o, "dock")
    if not os.path.exists(str_filepath_dock):
        os.makedirs(str_filepath_dock)

    ### load pdbqt file
    list_pdbqt = []
    for file in os.listdir(str_filepath_pdbqt):
        if file.endswith(".pdbqt"):
            list_pdbqt.append(file)
    
    ### run AutoDock Vina
    dict_score = {}
    for idx, pdbqt in enumerate(list_pdbqt):
        str_filepath_dock = os.path.join(args.o, "dock", pdbqt.replace(".pdbqt", ""))
        if not os.path.exists(str_filepath_dock):
            os.makedirs(str_filepath_dock)

        list_log = []
        list_score = []
        for rep in range(int(args.n)):
            str_prefix = pdbqt.replace(".pdbqt", "") + "_" + str(rep)
            # /opt/autodock_vina_1_1_2_linux_x86/bin/vina --receptor 6nur.pdbqt --ligand ritonavir.pbdqt --config 6nur.conf --out 6nur_ritonavir.pbdqt --log 6nur_ritonavir.log
            str_command = args.v + " "
            str_command += "--receptor " + os.path.join(args.o, os.path.basename(args.r) + ".pdbqt") + " "
            str_command += "--ligand " + os.path.join(str_filepath_pdbqt, pdbqt) + " "
            str_command += "--config " + os.path.join(args.o, os.path.basename(args.r) + ".conf") + " "
            str_command += "--cpu " + args.t + " "
            str_command += "--out " + os.path.join(str_filepath_dock, str(str_prefix + ".pdbqt")) + " "
            str_command += "--log " + os.path.join(str_filepath_dock, str(str_prefix + ".log")) + " "
            
            process = subprocess.Popen(str_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            int_grep = False
            for line in process.stdout:
                if line.strip() == "-----+------------+----------+----------":
                    int_grep = True
                elif line.strip() == "Writing output ... done.":
                    int_grep = False
                elif int_grep == True:
                    list_log.append(str(str(rep+1) + "\t" + line.strip()))
                    list_line = line.strip().split()
                    if list_line[0] == '1':
                        list_score.append(float(list_line[1]))
            process.wait()
            print("docking..." + "(" + str(idx+1) + "/" + str(len(list_sdf)) + ") replicate:" + str(rep+1))
        
        ### output log for a ligand
        with open(os.path.join(str_filepath_dock, "Log.txt"), "w") as file_outputFile:
            for line in list_log:
                file_outputFile.writelines(line + "\n")

        ### keep docking score for a ligand
        if pdbqt.replace(".pdbqt", "") not in dict_score and len(list_score)!=0:
            dict_score[pdbqt.replace(".pdbqt", "")] = sum(list_score) / len(list_score)
    
    ### output final score list
    with open(os.path.join(args.o, "Average_Score.txt"), "w") as file_outputFile:
        for key, value in dict_score.items():
            file_outputFile.writelines(str(key) + "\t" + str(value) + "\n")


if __name__ == "__main__":
    main()
