#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Feb 2024
# Last Modified: Feb 2024
#=================================================================
# Copyright (c) 2024 [Jieming Ye]
#
# This Python source code is licensed under the 
# Open Source Non-Commercial License (OSNCL) v1.0
# See LICENSE for details.
#=================================================================
"""
Pre-requisite: 
N/A
Used Input:
Various
Expected Output:
Various
Description:
This script defines two shared classes of default values to be shared among various scripts.
This script also defines a SharedMethods class containing common functions to be used for various scripts such as checking the existence of files, time manipulation, etc. 

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
# V1.1 (Jieming Ye) - 2024-12-04 Bring simname to osop command
# V2.0 (Jieming Ye) - Update GitHub repository location
# V3.0 (Jieming Ye) - Introduction of Data Lirary folder
#=================================================================
# Set Information Variable
# N/A
#=================================================================


#import tkinter as tk
import os
import shutil
import importlib
import importlib.resources
import importlib.metadata
import csv
import subprocess
import sys
import tempfile
import requests
import platform
from itertools import islice
from datetime import datetime

from collections import Counter

class DataFilenames:
    '''
    This class holds the database file name as in two lists.
    These two list will be checked at the very beginning of application lauching
    Any new dataset added in the future needs to be added to this comprehensive data list.
    public_file list are files hold on the GitHub public repository
    private_file list are files hold locally in data folder
    '''
    public_file = {
        'tiploc_library': 'tiploc_library.csv'
    }
    private_file = {
        'Potteric_Carr': 'ABB_Potteric_Carr.csv',
        'Hambleton_Jcn': 'Siemens_Hambleton_Jcn.csv'
    }

class SharedVariables:
    # this class will store all shared varibles
    sim_variable = None # get when be called
    main_option = None # default varies
    osop_version = None # default update at gui_start.py
    used_database_path = None # default update at gui_start.py (would be string either database_path_user or databse_path_default)
    
    # varible to be updated following version upgrade:
    # Replace 'your_package_name' with the actual name of your package
    package_name = 'vision_oslo_extension'
    support_name = 'support'
    private_data_name = 'data'
    installed_version = importlib.metadata.version(package_name)
    public_data_path = "https://github.com/NR-ESTractionPower/vo_extension_database"
    raw_data_url_begin = "https://raw.githubusercontent.com/NR-ESTractionPower/vo_extension_database/refs/heads/main/"
    
    lastupdate = 'July / 2025' # date of checking all links below
    copyright = 'CopyRight @ 2025, All Rights Reserved.'

    bhtpbank_path = 'C:\\Users\\Public\\Documents\\VISION\\Resources\\bhtpbank'
    database_path_user = 'C:\\Users\\Public\\Documents\\Vision_Oslo_Extension\\user_data' # This is user controlled library
    database_path_default = 'C:\\Users\\Public\\Documents\\Vision_Oslo_Extension\\default_data' # This is forced default data library

    contacts = "Email: 'traction.power@networkrail.co.uk'"
    license_online = "https://raw.githubusercontent.com/NR-ESTractionPower/vo_addin/refs/heads/main/vision_oslo_extension_license.txt"
    support_online = "https://github.com/NR-ESTractionPower/vo_addin"
    issue_online = "https://github.com/NR-ESTractionPower/Vision-Oslo-Extension/issues"
    vo_issue_online = "https://github.com/NR-ESTractionPower/vision_oslo_issues/issues"

    bhtpbank_central_library = ("https://networkrail.sharepoint.com/:f:/r/sites/NRDDTDNS/Shared%20Documents/"
                                "05%20-%20Traction%20Power%20Modelling/02%20-%20Asset%20Data/"
                                "07%20-%20Rolling%20Stock/01%20-%20Master%20BHTPBANK%20Library?csf=1&web=1&e=gtytu8")

    license_file = os.path.join(importlib.resources.files(package_name), "license.json")
    config_file = os.path.join(importlib.resources.files(package_name), "config.json")
    current_path = None # get current path
    admin_password = "passwordS3F3" # this is the Mac password

    file_extension = [".srt",".opf",".trp.txt",".tkp.txt",".mcl",".pd.fil",".pd.log",".egy.txt", \
                      ".rpt.txt",".idt",".idp.txt",".ckp",".jcn.txt",".scp.txt",".tfp",".mon.txt", \
                      ".lst.txt",".tco.txt",".plt.txt",".gd",".oslo.txt",".xrf",".ttp.txt",".dat", \
                      ".opa",".oof",".tra.txt",".ocl",".routes",".vcf.txt",".rte",".wrn.txt",".routes.mon.txt", \
                      ".C2V.routes.txt",".routes.itf.txt",".VVW",".vvw",".VCN",".vcn", \
                      ".icr",".xcr",".opc",".battery.txt",".traction.txt",".pdv.csv"]

class SharedMethods:
    # check if the script running in debug mode or not
    def is_debug_mode():
        # Checks if the debugger is attached by inspecting system flags
        return sys.gettrace() is not None

    # text file reading progress bar print out
    def text_file_read_progress_bar(index, total_line):
        """
        This function handles a text file only.
        It requires the index which is the current line  index and
        total_line which is the total number of lines in the file.

        It will output a progress bar in the console.
        """
        bar_length = 50
        if index % (total_line // 100) == 0: # update progress bar every 1%
            percent = int(index * 100 / total_line)
            filled = int(bar_length * percent / 100)
            bar = '=' * filled + '-' * (bar_length - filled)
            print(f"\rProgress: |{bar}| {percent}% completed", end='', flush=True)
        # print out the last line when index is the last line
        if index == total_line - 1:
            print(f"\rProgress: |{'=' * bar_length}| 100% completed", flush=True)        
        return

    # check bhtpbank file's existance in the source library
    @staticmethod
    def check_bhtpbank_from_root(filename):
        file_path = os.path.join(SharedVariables.bhtpbank_path,filename)

        if not os.path.isfile(file_path): # if the oof file does not exist
            SharedMethods.print_message(f"ERROR: Traction Profile {filename} does not exist. Checking required...","31")
            return False

        return file_path
    
    # check if a extraction file contains information or not
    @staticmethod
    def validate_extracted_result(filename: str, force_data: bool = False):
        '''Check if an osop extracted file contains no info or not. For ds1 and d4 files'''
        # Map file extensions to the required minimum number of lines
        min_lines_required = {
            'ds1': 18,   # More than 17 lines
            'd4': 13,    # More than 12 lines
            'mxn': 17,    # (TODO) to be updatedMore than 16 lines at least (minmax and smooth branch current)
            'vlt': 18,    # More than 17 lines
            'lst': 1,       # (TODO) This is a bit random
            'snp': 1,       # This file will not even be created if empty
            '12':1,        # This file will show info as zero even not valid

        }

        # Get the file extension (last suffix)
        file_extension = filename.split('.')[-1].lower()

        # Check if the extension is one we are handling
        if file_extension not in min_lines_required:
            SharedMethods.print_message(f"WARNING: Unreconginize file type: {file_extension}.Ignore Checking. Contact support to add this.","33")
            return True

        try:
            # Read all lines from the file
            with open(filename, 'r') as file:
                lines = list(islice(file,50)) # Read only the first 50 lines
            
            # Check if the line count meets the requirement
            if len(lines) >= min_lines_required[file_extension]:
                return True
            else:
                SharedMethods.print_message(f"WARNING: Extracted '{file_extension}' is empty: {filename}","33")
                if force_data:
                    return False
                else:
                    return True
            
        except Exception as e:
            SharedMethods.print_message(f"ERROR: An error occurred while openning the file [{filename}]: {e}","31")
            return False

    # copy files from source folder to active entry
    @staticmethod
    def copy_example_files(filename):
        distribution = importlib.resources.files(SharedVariables.package_name)
        # Get the path to the package
        #package_path = distribution.location + "\\" + SharedVariables.package_name
        package_path = os.path.join(str(distribution), SharedVariables.support_name)

        # Get the absolute path of the file in the package location
        file_in_package = os.path.join(package_path, filename)
        current_path = os.getcwd() # get current path

        check_file = os.path.join(current_path, filename)

        if os.path.exists(check_file):
            print(f"File '{filename}' already exists in the current working directory. Skipping copy...")
        else:
            # Copy the file to the current working directory
            shutil.copy(file_in_package,current_path)
            print(f"File '{filename}' copied to the current working directory. Config as required...")

    # initial database system check
    @staticmethod
    def initial_missing_user_database_check():
        '''
        This function doing application database entering checking and returing:
        FALSE: if the initial database check passed i.e. no missing files.
        Filenamelist: if the initial database check failed.
        '''
        filenamelist = []
        # check if the database path exist.
        if not os.path.exists(SharedVariables.database_path_user):
            for filename in DataFilenames.private_file.values():
                filenamelist.append(filename)
            for filename in DataFilenames.public_file.values():
                filenamelist.append(filename)
        
        # loop the database folder and add the missing files into the filename list
        else:
            for filename in DataFilenames.private_file.values():
                file_in_package = os.path.join(SharedVariables.database_path_user, filename)
                if not os.path.isfile(file_in_package):
                    filenamelist.append(filename)
            for filename in DataFilenames.public_file.values():
                file_in_package = os.path.join(SharedVariables.database_path_user, filename)
                if not os.path.isfile(file_in_package):
                    filenamelist.append(filename)

        # if not empty filename list return filenamelist otherwise False
        if filenamelist:
            return filenamelist
        else:
            return False

    # update the customised database library
    @staticmethod
    def update_database_library(filenamelist: list=None, library: int = 0):
        '''
        This function updates the customised database library from GitHub Repo online (if public)
        or data folder (if private).
        This will overwrite the existing database file blindly.

        if no input is not provided, this will restore all default database library

        library: (int)
        default to 0: default library
        1: user library
        '''
        if library == 0:
            controlled_data_path = SharedVariables.database_path_default
        else:
            controlled_data_path = SharedVariables.database_path_user

        print(f"Config Path: '{controlled_data_path}'")
        # check if the database path exist, if not create one.
        if not os.path.exists(controlled_data_path):
            try:
                os.makedirs(controlled_data_path)
                SharedMethods.print_message(f"ATTENTION: Folder '{controlled_data_path}' created.","33")
            except Exception as e:
                SharedMethods.print_message(f"ERROR: Error creating folder {controlled_data_path}: {e}. Please contact support using this error message...", "31")
                return False
        
        private_file_list = []
        public_file_list = []

        if filenamelist:
            for filename in filenamelist:
                # check if the filename belongs public or private dataset, and update accordingly
                if filename in DataFilenames.private_file.values():
                    private_file_list.append(filename)
                elif filename in DataFilenames.public_file.values():
                    public_file_list.append(filename)
                else:
                    SharedMethods.print_message(f"ERROR: File '{filename}' is not recognised as a valid database file. Please contact support using this error message...", "31")
                    return False
        else:
            for file in DataFilenames.private_file.values():
                private_file_list.append(file)
            for file in DataFilenames.public_file.values():
                public_file_list.append(file)
        
        # copy the private data from the packaged data folder
        distribution = importlib.resources.files(SharedVariables.package_name)
        package_path = os.path.join(str(distribution), SharedVariables.private_data_name)

        # Get the absolute path of the file in the package location
        for file in private_file_list:
            file_in_package = os.path.join(package_path, file)
            target_file = os.path.join(controlled_data_path, file)
            try:
                shutil.copy(file_in_package, target_file)
                SharedMethods.print_message(f"ATTENTION: '{file}' database updated to default dataset.","33")
            except Exception as e:
                SharedMethods.print_message(f"ERROR: Error copying file {file} to {target_file}: {e}. Please contact support using this error message...", "31")
                return False
        
        # check online resources and download the public data to the same folder
        # Check internet connection
        if not InternetValidation.internet_check(SharedVariables.public_data_path):
            SharedMethods.print_message(f"WARNING: Online databse updated cannot proceed due to not allowed network. Skipping...","33")
            return False
        
        for file in public_file_list:
            file_url = SharedVariables.raw_data_url_begin + file
            # download the csv file to the target folder
            target_file = os.path.join(controlled_data_path, file)
            try:
                response = requests.get(file_url)
                response.raise_for_status()  # Raise an error for bad responses
                with open(target_file, 'wb') as f:
                    f.write(response.content)
                SharedMethods.print_message(f"ATTENTION: '{file}' database updated to default dataset.","33")
            except Exception as e:
                SharedMethods.print_message(f"ERROR: Error downloading file {file} from {file_url}: {e}. Please contact support using this error message...", "31")
                return False
            
        return True

    # check data library files, return full path if found
    @staticmethod
    def check_data_files(filename):
        # Get the absolute path of the file in the package location
        file_in_package = os.path.join(SharedVariables.used_database_path, filename)

        if os.path.exists(file_in_package):
            print(f"Data file '{filename}' exist in the Data library. Reading will be done.")
            return file_in_package
        else:
            SharedMethods.print_message(f"WARNING: Data file '{filename}' does NOT exist in the Data library. Reading will be skipped.","33")
            SharedMethods.print_message(f"ATTENTION: You can add data file '{filename}' to {SharedVariables.used_database_path} and report it to support.","33")
            return False

    #check existing file
    @staticmethod
    def check_existing_file(filename):
        print(f"Checking File {filename}...")

        first = filename.split('.')[0]
        if first == "":
            SharedMethods.print_message("ERROR: Select the simulation or required file to continue...","31")
            return False

        current_path = os.getcwd() # get current path
        file_path = os.path.join(current_path,filename) # join the file path
        if not os.path.isfile(file_path): # if the oof file does not exist
            SharedMethods.print_message(f"ERROR: Required file {filename} does not exist. Checking required...","31")
            return False
        return True

    # check the folder and file for summary
    @staticmethod
    def folder_file_check(subfolder,filename,required=True):
        """
        Check if a specific file exists in a given subfolder.
        Returns True if the file exists, False otherwise.
        if required is True, it will print an error message and exit if the file does not exist.
        """
        print(f"Checking File {filename} in {subfolder}...")
        current_path = os.getcwd() # get current path

        # Create the complete folder path
        folder_path = os.path.join(current_path, subfolder)
        
        # Check if the folder exists
        if not os.path.exists(folder_path):
            if required:
                SharedMethods.print_message(f"ERROR: Required folder {subfolder} does not exist. Check your Input. Exiting...","31")
            return False
        
        # file path
        file_path = os.path.join(folder_path,filename) # join the file path
        # print(file_path)
        if not os.path.isfile(file_path):
            if required:
                SharedMethods.print_message(f"ERROR: Required file {filename} does not exist at {subfolder}. Check your Input. Exiting...","31")
            return False
        return True

    # copy the file to a subfolder / if not exist, create the subfolder
    @staticmethod
    def copy_file_to_subfolder(subfolder, filename, new_filename=None):
        print(f"Copying File {filename} to {subfolder}...")
        current_path = os.getcwd()  # Get current path
        folder_path = os.path.join(current_path, subfolder)

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                print(f"Folder '{subfolder}' created.")
            except Exception as e:
                SharedMethods.print_message(f"ERROR: Error creating folder {subfolder}: {e}. Check your Input...", "31")
                return False

        # Determine the target file name
        target_filename = new_filename if new_filename else filename
        file_path = os.path.join(folder_path, target_filename)

        # Warn if the target file already exists
        if os.path.isfile(file_path):
            SharedMethods.print_message(f"WARNING: File {target_filename} already exists in {subfolder}. Overwriting...", "33")
            os.remove(file_path)

        # Copy the file
        try:
            shutil.copy(filename, file_path)
            print(f"File '{filename}' copied to subfolder successfully'.")
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error copying file {filename} to {file_path}: {e}. Check your Input...", "31")
            return False

        return True

    # check oof file
    @staticmethod
    def check_oofresult_file(simname):

        resultfile = simname + ".oof"
        if simname == "":
            SharedMethods.print_message("ERROR: Please select the simulation to Continue...","31")
            return False

        if not SharedMethods.check_existing_file(resultfile):
            return False

        return True

    # osop running
    @staticmethod       
    def osop_running(simname):
        # delete osop.exe if exist in the current folder
        if os.path.exists("osop.exe"):
            try:
                os.remove("osop.exe")
                SharedMethods.print_message("WARNING: Existing osop.exe deleted to avoid version conflict. Continue...","33")
            except Exception as e:
                SharedMethods.print_message(f"ERROR: Error deleting existing osop.exe: {e}. Check your Input...","31")
                return False

        # write command line
        cmdline = f'osop "{simname}"'
        # package_name = 'vision_oslo_extension'
        # Get the distribution object for your package
        distribution = importlib.resources.files(SharedVariables.package_name)
        # Get the path to the package
        package_path = str(distribution)

        if SharedVariables.osop_version == 1:
            package_path = os.path.join(package_path,'rn26')
        elif SharedVariables.osop_version == 2:
            package_path = os.path.join(package_path,'rn27')
        elif SharedVariables.osop_version == 3:
            package_path = os.path.join(package_path,'rn29')
        # add this for debugging version purpose. Default to RN26
        else:
            package_path = os.path.join(package_path,'rn26')

        with open("batch_run.bat","w") as fba:
            fba.writelines("@echo off\n")
            fba.writelines("set PATH=%PATH%;" + package_path + "\n")
            fba.writelines("@echo on\n")
            fba.writelines(cmdline)
        # os.system("batch_run.bat")

        if SharedMethods.is_debug_mode():
            print("OSOP EXTRACTION DOES NOT WORK IN DEBUG MODE DUE TO ENVIROMENT SETTINGS. MANUAL EXTRACT RESULT FIRST.")
            print("THIS PROCESS WILL BE IGNORED AND CONTINUED.")
            return True
        # JY 2024:10. Adjust to use subprocess to run OSOP
        # Run the batch file and capture output
        print("\rOSOP extraction running. Please wait......", end='', flush=True)

        process = subprocess.Popen("batch_run.bat", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            #print(process.returncode)
            #code 10029: when fatal error with space in the simname but no quatation mark. (this has been fixed by changing the cmdline)
            if process.returncode == 999:
                SharedMethods.print_message(f"\nERROR: Error when running the command: '{cmdline}'...","31")
                SharedMethods.print_message(f"ERROR: osop.exe return Error due to control data issues...","31")
                SharedMethods.print_message(f"ERROR: Possibly you are trying to extract something which is not modelled. Check your input or contract support...","31")
            else:
                SharedMethods.print_message(f"\nERROR: Error running command: {stderr.decode()}","31")
                SharedMethods.print_message(f"ERROR: Check OSOP VERSION configuration or contact support...","31")
            return False
        else:
            # this means the command was successful finished
            # Capture and print the last line of output for processing
            output_lines = stdout.decode().splitlines()
            # for line in output_lines:
            #     if line != '':
            #         print(line)
            if output_lines:
                last_line = output_lines[-1]
                if last_line == "Run completed.":
                    # check the simname.osop.lst file
                    if SharedMethods.check_osop_lst_file_status(simname):
                        print("\rOSOP run completed successfully.",flush=True)
                        return True
                    else:
                        SharedMethods.print_message(f"\nERROR: Warning from osop. Check OSOP VERSION configuration ...","31")
                        return False
                else:
                    SharedMethods.print_message(f"\nERROR: Error in osop.exe. Extraction Failed. Check OSOP VERSION configuration or contact support...","31")
                    return False
            else:
                SharedMethods.print_message(f"\nERROR: No output from osop.exe. Extraction Failed. Check OSOP VERSION configuration or contact support...","31")
                return False

    # check simname.osop.lst file for output status
    @staticmethod
    def check_osop_lst_file_status(simname):
        lst_file = simname + ".osop.lst"
        status = True # default status is True
        # read the lst file ine by line
        try:
            with open(lst_file, 'r') as file:
                for line in file:
                    if line[:25].strip() == "End of input card listing":
                        break
                    if line[:7].strip().lower() == "warning":
                        SharedMethods.print_message(f"WARNING: {line.strip()}","33")
                        status = False
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error reading the lst file {lst_file}: {e}.","31")
            status = False

        return status
        
    # rename files
    @staticmethod
    def file_rename(old_name,new_name):
        try:
            os.rename(old_name,new_name)
            print(f"File {new_name} successfully created. Processing Continue...")
        except FileExistsError:
            os.remove(new_name)
            os.rename(old_name,new_name)
            print(f"File {new_name} successfully replaced. Processing Continue...")
        except FileNotFoundError:
            SharedMethods.print_message(f"ERROR: File {new_name} FAILED as the OSOP extraction fail. Check Input...","31")

    # module to check 7 digit user input time
    @staticmethod
    def time_input_process(time_string,option_back):
        """
        This function processes a 7-digit time string in the format DHHMMSS.
        It returns original string if option is 1, or the total seconds if option is 2.
        It return False if the input is invalid.
        """
        print(f"Checking 7 digit time input: '{time_string}'...")

        if not len(time_string) == 7:
            SharedMethods.print_message("ERROR: Invalid time format input. Press reenter the 7 digit time.","31")
            return False

        seconds_int = 0        
        day = int(time_string[:1])
        hour = int(time_string[1:3])
        minute = int(time_string[3:5])
        second = int(time_string[5:7])

        if not 0 <= day <= 9:
            SharedMethods.print_message("ERROR: Invalid DAY input (0-9). Press reenter the 7 digit time.","31")
            return False
                
        if 0 <= hour <= 24:
            seconds_int += hour*60*60
        else:
            SharedMethods.print_message("ERROR: Invalid HOUR input (0-24). Press reenter the 7 digit time.","31")
            return False
                
        if 0 <= minute <= 60:
            seconds_int += minute*60
        else:
            SharedMethods.print_message("ERROR: Invalid MINUTE input (0-60). Press reenter the 7 digit time.","31")
            return False
                
        if 0 <= second <= 60:
            seconds_int += second
        else:
            SharedMethods.print_message("ERROR: Invalid SECOND input (0-60). Press reenter the 7 digit time.","31")
            return False

        if option_back == 1:
            return time_string
        else:
            return seconds_int

    # check the propoer life file of the model
    @staticmethod
    def check_and_extract_lst_file(simname, time_start=None, time_end=None):
        
        filename = simname + ".osop.lst"
        opcname = simname + ".opc"
        flag_time_boundary = False # default is False

        if time_start is not None and time_start is not None:
            time_start = SharedMethods.time_input_process(time_start,1)
            time_end = SharedMethods.time_input_process(time_end,1)

            if time_start and time_end: # both are valid
                flag_time_boundary = True

        # Create batch file for list command and run the batch file
        # and define the lst file name to process the information
        # generate List file
        if not os.path.isfile(filename):
            with open(opcname,"w") as fopc:
                if flag_time_boundary:
                    fopc.writelines("LIST INPUT FILE FROM "+time_start+" TO "+time_end+"\n")
                else:
                    fopc.writelines("LIST INPUT FILE\n")
            if not SharedMethods.osop_running(simname):
                return False
        else:
            lst_file_size = os.path.getsize(filename)
            if lst_file_size < 10000: # a random size (bytes) to check if lst should be redone (10000 bytes = 10 kb)
                with open(opcname,"w") as fopc:
                    if flag_time_boundary:
                        fopc.writelines("LIST INPUT FILE FROM "+time_start+" TO "+time_end+"\n")
                    else:
                        fopc.writelines("LIST INPUT FILE\n")
                if not SharedMethods.osop_running(simname):
                    return False
            else:
                SharedMethods.print_message(f"WARNING: {simname} list file extraction is SKIPPED as previously done (>10kb).","33")
                SharedMethods.print_message(f"WARNING: Manually delete the file if a new extraction is required.","33")
        
        return True
    
    # module to read the text file input
    @staticmethod
    def file_read_import(filename,simname):
        
        if not os.path.isfile(filename): # if the file exist
            SharedMethods.print_message(f"ERROR: Required input file {filename} does not exist. Please select another option.","31")
            return False

        # reading the train list file
        text_input = []
        with open(filename) as fbrlist:
            for index, line in enumerate(fbrlist):
                item = line[:50].strip()
                if not item:
                    continue # skip the empty line

                if item in text_input:
                    SharedMethods.print_message(f"WARNING: Duplicate item '{item}' identified. This will be read again.","33")
                text_input.append(item)

        return text_input
    
    # module to convert 7 digits time to time format
    @staticmethod
    def time_convert(time_string):
        
        #time_string = input()          
        day = int(time_string[:1])
        hour = int(time_string[1:3])
        minute = int(time_string[3:5])
        second = int(time_string[5:7])

        if not day == 0:
            day = day # to be updated to process info at a later stage
        time = str(hour) + ":" + str(minute) + ":" + str(second)        
        #debug purpose
        #print(seconds_int)
        # Return the second integer number as same used in the list file           
        return time

    # read tiploc information
    @staticmethod
    def get_tiploc_library():
        tiploc = {} # create a empty tiploc
        filename = DataFilenames.public_file['tiploc_library']
        filepath = os.path.join(SharedVariables.used_database_path, filename)
        valid = True # flag to check if the data format is valid or not

        try:
            with open(filepath,'r') as file:
                csv_reader = csv.reader(file)
                first_row = True  # Flag to identify the first row
                for row in csv_reader:
                    if first_row:
                        # Read row[1] as a string referring to the date
                        updated_date = row[1]
                        first_row = False  # Reset the flag after processing the first row
                        # Check if date is in dd/mm/yyyy format
                        try:
                            parsed_date = datetime.strptime(updated_date, "%d/%m/%Y")
                        except ValueError:
                            SharedMethods.print_message(f"ERROR: Invalid date format: '{updated_date}' for the first row.","31")
                            valid = False
                    else:
                        # Continue the logic for subsequent rows
                        key = row[0]
                        value = row[1]
                        tiploc[key] = value
                        # check TIPLOC code (key) in all capital letter and less equal then 7 char
                        if not key.isupper() or len(key) > 7:
                            SharedMethods.print_message(f"ERROR: Invalid TIPLOC code: '{key}'. Must be all capital letters and <= 7 characters.","31")
                            valid = False
            
            # validation check
            if not valid:
                SharedMethods.print_message(f"ERROR: TIPLOC library in '{SharedVariables.used_database_path}' has incompatible format. Restore the database library required.","31")
                return False

            print(f"\nTIPLOC Libray Last Update: {updated_date}")
            SharedMethods.print_message(f"ATTENTION: Update {SharedVariables.used_database_path} if an update is needed!","33")
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Reading CIF TIPLOC lookup library failed. {e}. Restore the database library required.","31")
            return False
        
        return tiploc

    # open a file in support folder
    @staticmethod
    def open_support_file(filename):
        distribution = importlib.resources.files(SharedVariables.package_name)
        package_path = os.path.join(str(distribution), SharedVariables.support_name)
        # Get the absolute path of the file in the package location
        file_in_package = os.path.join(package_path, filename)

        # create a temp directory and copy the file there
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, filename)

        try:
            shutil.copy(file_in_package, temp_file) # copy the file to temp directory
            subprocess.Popen(['start', '', temp_file], shell=True,close_fds=True)
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error opening file with default app: {e}","31")

        return
    
    # find duplication in a list
    @staticmethod
    def find_duplicates(lst):
        # Count occurrences of each element
        counts = Counter(lst)
        # Extract elements with more than one occurrence
        duplicates = [item for item, count in counts.items() if count > 1]

        if not duplicates == []:
            SharedMethods.print_message(f"ERROR: Duplicated ID exists in the input lists: {duplicates}.","31")
            SharedMethods.print_message(f"ERROR: Please clear the duplicates before continue...","31")
            return False
        else:
            return True

    # delete all simulation result:
    def clean_up_simulation_folder():
        reserved_file_suffix = ['.vvw','.ocl','.vcn','extra.oslo','extra.bat.oslo','pdv.csv','.xlsx','xlsm']
        # delete all files in current working directory if file name not ending as in the list
        current_path = os.getcwd() # get current path
        for filename in os.listdir(current_path):
            if not any(filename.endswith(suffix) for suffix in reserved_file_suffix):
                file_path = os.path.join(current_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)  # remove the file or link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # remove the directory and its contents
                    print(f"INFO: File '{filename}' been deleted.")
                except Exception as e:
                    SharedMethods.print_message(f"ERROR: Failed to delete {file_path}. Reason: {e}", "31")
        print("INFO: Simulation Folder Clean Up Completed.")

    # define the running in thread mechanism    
    def launch_new_thread_or_process(import_option, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step,cwd=None):
        # Define a dictionary mapping import_option to module names
        module_mapping = {
            "cif_prepare.py": "cif_prepare",
            "model_check.py": "model_check",
            "oslo_extraction.py": "oslo_extraction",
            "post_processing.py": "post_processing",
            "average_load.py": "average_load",
            "protection_if.py": "protection_if",
            "grid_connection.py": "grid_connection",
            "ole_processing.py": "ole_processing",
            "sfc_assess.py": "sfc_assess",
            "batch_processing.py": "batch_processing",
            "dc_summary.py": "dc_summary",
            "dc_single_end_feeding.py": "dc_single_end_feeding",
            "dc_falling_voltage_protection.py": "dc_falling_voltage_protection",
            "battery_processing.py":"battery_processing",
            "cif_output_analysis.py":"cif_output_analysis",
            "simulation_batch_run.py":"simulation_batch_run",
            "bhtpbank_check.py":"bhtpbank_check",
        }

        if cwd:
            # Change the current working directory to the specified path
            # this is compolsory for new process
            os.chdir(cwd)

        # Get the module name corresponding to import_option
        module_name = module_mapping.get(import_option)

        # Import the module
        if module_name:
            fc = importlib.import_module(f"{SharedVariables.package_name}.{module_name}")
            #from vision_oslo_extension import module_name as fc
        else:
            # Handle the case when import_option doesn't match any module
            print("Invalid import_option:", import_option)
        
        try:    
            continue_process = fc.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
            if not continue_process:
                # Do something if the process should not continue
                # Print error message in red
                SharedMethods.print_message("ERROR: Process terminated due to captured issue. "
                                            "Please check the error history above or contact support. "
                                            "You can continue using other options...", '31')
            else:
                # Do something if the process should continue
                # Print success message in green
                SharedMethods.print_message("Action successfully completed. "
                                            "Check monitor history above and result files in your folder.", '32')
        
        except Exception as e:
            SharedMethods.print_message(f"ERROR: UNEXPECTED! PLEASE REPORT BUG AND CONTACT SUPPORT... ", '31')
            SharedMethods.print_message(f"ERROR: source code module - {import_option}: {e}","31")
    
    def print_message(message, color_code):
        os.system("")
        color_start = f'\033[1;{color_code}m'   # Start color
        color_reset = '\033[1;0m'               # Reset color
        print(color_start + message + color_reset)

class InternetValidation:
    def internet_check(url):
        '''Check if a handshake with internet can be established or not. To decide if an upgrade is possible or not'''

        # check connected network to see if it is NR network or not
        if InternetValidation.check_restricted_network():
            SharedMethods.print_message(f"WARNING: Abort internet connection due to Network Rail private network detected.","33")
            return False

        try:
            # Send a HEAD request using requests with a timeout of 5 seconds
            response = requests.get(url, timeout=5)
            return True

        except requests.exceptions.Timeout:
            SharedMethods.print_message("ERROR: Request timed out after 5 seconds. POOR INTERNET...", "31")
            return False
        
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Unexpected connection: {e}. Please contact the support...","31")
            return False

    def check_restricted_network():
        '''Return TRUE if connected to the NR Office Environment'''
        system = platform.system()
        try:
            if system == "Windows":
                # WIFI Network Check
                result = subprocess.run(["netsh", "wlan", "show", "interfaces"],
                                        capture_output=True, text=True, check=True)
                for line in result.stdout.splitlines():
                    if "SSID" in line and "BSSID" not in line:
                        ssid = line.split(":", 1)[1].strip()
                        if ssid == "14":
                            # print("NR CORP WIFI 14 DETECTED.")
                            return True
                        else:
                            break
                # Ehternet Network Check
                block = False
                result = subprocess.run(["ipconfig", "/all"],
                                        capture_output=True, text=True, check=True)
                for line in result.stdout.splitlines():
                    if "adapter" in line.lower() and "Ethernet" in line:
                        block = True
                    if block:
                        # skip the check if the ethernet cable is not used
                        if "media disconnected" in line.lower():
                            # this means WIFI not 14 and Ethernet cable is not connected
                            return False
                        type = line.split(":", 1)[0].strip().lower()
                        if "default gateway" in type:
                            gatewayip = line.split(":", 1)[1].strip()
                            if gatewayip.startswith("10.176."): # This IP is only used for small private network
                                # print("NR CORP ETHERNET CONNECTION DETECTED.")
                                return True
                            else:
                                return False
            else: # not ready for other operating system yet
                return False
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Unexpected error: {e}. Please contact the support...","31")
            return False
        return False