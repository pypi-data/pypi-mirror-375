#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Nov 2023
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
N/A
Expected Output:
Start GUI
Description:
This module is the package entry.
This module is the only module to be called from User End script directly.
It ensures GUI is only created in the main process while allowing subprocesses
to be spawned for other tasks.
"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
# V2.0 (Jieming Ye) - Including License Check
# V3.0 (Jieming Ye) - Allow mult-process from MainProcess
# V4.0 (Jieming Ye) - Add freeze_support for frozen executables
# V5.0 (Jieming Ye) - Add initilization checking of public database
#=================================================================

import multiprocessing
import sys
import os

def is_main_process():
    """Check if current process is the main process."""
    return multiprocessing.current_process().name == 'MainProcess'

def initialize_gui():
    """Initialize the GUI if license check passes."""
    try:
        # license check
        from vision_oslo_extension import licensing
        if not licensing.main():
            input("Press any key to exit.....")
            return False
        # database folder check: This is on customised user database only
        from vision_oslo_extension import shared_contents
        filenamelist = shared_contents.SharedMethods.initial_missing_user_database_check()
        if filenamelist:
            shared_contents.SharedMethods.update_database_library(filenamelist=filenamelist,library=1)
        # Launch the GUI
        from vision_oslo_extension import gui_start
        app = gui_start.SampleApp()
        app.mainloop()
        return True
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        input("Press any key to exit.....")
        return False

def main():
    """Main entry point for the application."""
    print('Loading Application...')
    
    if not is_main_process():
        # If this is a subprocess, just return without creating GUI
        return
    
    # Set up multiprocessing to work with frozen executables if needed
    if getattr(sys, 'frozen', False):
        multiprocessing.freeze_support()
    
    # Initialize GUI in main process only
    initialize_gui()

if __name__ == '__main__':
    main()    