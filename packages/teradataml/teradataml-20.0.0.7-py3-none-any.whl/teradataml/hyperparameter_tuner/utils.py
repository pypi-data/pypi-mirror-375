# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Kesavaragavan B (kesavaragavan.b@Teradata.com)
# Secondary Owner: Pankaj Purandare (PankajVinod.Purandare@teradata.com),
#                  Pradeep Garre (pradeep.garre@teradata.com)
#
# This is a common utility file where common class functionality is included.
# Hyperparameter-tuner classes and other functionality can reuse this 
# utility features according to the requirements.
#
# ####################################################################
import sys
import threading
from collections import deque
from teradataml.utils.validators import _Validators


class _ProgressBar:
    """ Class to provide minimal logging with progress bar representation."""
    def __init__(self, jobs, prefix="Computing:", verbose=0):
        # Validate arguments.
        arg_info_matrix = []
        arg_info_matrix.append(["jobs", jobs, False, (int)])
        arg_info_matrix.append(["prefix", prefix, True, (str)])
        arg_info_matrix.append(["verbose", verbose, False, (int), False, [0, 1, 2]])
        _Validators._validate_function_arguments(arg_info_matrix)
        # Total number of jobs are scheduled.
        self.total_jobs = jobs
        # Completed jobs out of 'total_jobs'.
        self.completed_jobs = 0
        # Fill blank text While rewritting displayed previous line.
        self.blank_space_len = 0
        # Prefix is a progress bar title.
        self.prefix = prefix
        # Verbose holds the level of information logged.  
        self.verbose = verbose
        # Bar size mention length of the progress bar.
        self.BAR_SIZE = 60
        # BAR is a symbol used to notify the completed jobs in progress bar.
        # Check whether the stdout is from ipykernel or terminal.
        _is_terminal = "ipykernel" not in str(sys.stdout)
        # Based on that unicode symbols are selected.
        self.BAR = '█' if _is_terminal else '⫿'
        # Boundaries of progress bar.
        self.BOUNDARY_BAR = '|' if _is_terminal else '｜'
        # UNFILL_BAR notifies remaining jobs.
        self.UNFILL_BAR = '_' if _is_terminal else '⫾'
        # standard out specifies text output area.
        self.STDOUT = sys.stdout 
        # Queue to handle multiple thread input in sequence.
        self.queue = deque()
        # Initiate the progress bar.
        self.__show()

        self._lock = threading.Lock()


    def update(self,
               msg='',
               data=None,
               progress=True,
               ipython=False):
        """
        DESCRIPTION:
            Method to update the progress bar and live logs. Whenever, update()
            method is called with message it stores the message and update the 
            progress bar state. 
            Note:
                * Progress bar design varies based on interactive execution or 
                  script execution. 

        PARAMETERS:
            msg:
                Optional Argument.
                Specifies a message needs to be displayed. 
                Notes:
                    * Use ',' separator to distinguish multiple items in a message.
                    * Set verbose value greater than 1 to display message.
                    * Don't pass msg when verbos is set to 1. 
                Default value: None
                Types: str
            
            data:
                Optional Argument.
                Specifies the data needs to be displayed.
                Types: DataFrame/list/tuple/dict
            
            progress:
                Optional Argument.
                Specifies the progress of progress bar.
                When set True, increases the completed_jobs. Otherwise,
                completed_jobs remains constant.
                Default value: True
                Types: bool
            
            ipython:
                Optional Argument.
                Specifies the ipython enviornment.
                When set True, ipython libaray is used to display DataFrame. Otherwise,
                print is used to display dataframe
                default value: False
                Types: bool   

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Example 1: Set verbose value to 2, when valid message is passed.
            #            Update progress bar and log.
            >> pb_obj.update("Model_ID: XGBOOST_5, Status:PASS")
            Model-ID:XGBOOST_2 - Status:PASS                           
            Model-ID:XGBOOST_1 - Status:PASS                           
            Model-ID:XGBOOST_0 - Status:PASS                           
            Model-ID:XGBOOST_3 - Status:PASS                           
            Model-ID:XGBOOST_4 - Status:PASS                           
            Model-ID:XGBOOST_5 - Status:PASS                           
            Completed: ｜⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿｜ 100% - 6/6

            # Example 2: Set verbose value to 1, when "msg" argument is 
            #            not passed.
            #            Note: Default progress bar design functionality when 
            #                  it is called from ipykernel.
            # Update progress bar and log.
            >> pb_obj.update()
            Completed: ｜⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿｜ 100% - 10/10

            # Example 3: Set verbose value to 1, when "msg" argument is 
            #            not passed and executed script from console/terminal.
            #            Note: Progress bar design alone changes when 
            #                  same functionality is called from console/terminal.
            # Update progress bar and log.
            >> pb_obj.update()
            Completed: |████████████████████████████████████████████████████| 100% - 10/10
           
        """
        _Validators._validate_function_arguments([["msg", 
                                                   msg, 
                                                   self.verbose != 2, 
                                                   (str)]])
        # Thread-safe condition to avoid race-conditions and suitable for 
        # both sequential (single thread) and parallel (multi-thread) executions.
        # Note: Queue is a thread-safe but other parts are not resistance 
        # to race condition. Hence, locking is performed.

        with self._lock:
            # Append log message into queue.
            self.queue.append(msg)
            
            # Updated completed jobs count.            
            self.completed_jobs += int(progress)
            
            # Update log only when it is valid.
            if self.completed_jobs <= self.total_jobs:
                # Once all jobs are completed change the prefix of progress.
                # Display message and progress bar.
                self.__show(data, ipython, progress)

    
    def __show(self, 
               data=None,
               ipython=False,
               progress=True):
        """
        DESCRIPTION:
            Internal method to display updated message depending on its type. 

        PARAMETERS:
            data:
                Optional Argument.
                Specifies the data needs to be displayed.
                Types: DataFrame/list/tuple/dict
        
            ipyhton:
                Optional Argument.
                Specifies the ipython enviornment.
                When set True, ipython libaray is used to display DataFrame. Otherwise,
                print is used to display dataframe
                default value: False
                Types: bool
                
            progress:
                Optional Argument.
                Specifies the progress of progress bar.
                When set True, increases the completed_jobs. Otherwise,
                completed_jobs remains constant.
                Default value: True
                Types: bool

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >> self.__show()
        """ 
        # Check ipython library is installed or not.
        if ipython:
            try:
                from IPython.display import display, HTML
            except ImportError:
                ipython = False
        
        # Display message when verbose is greater than 1.
        if self.verbose > 1 and len(self.queue) > 0:
            # Overwrite the previous text in stdout using blank space.
            print(" " *self.blank_space_len, end='\r', flush=True)
            
            # Format the comma separated message.
            _msg = self.queue[-1].replace(","," - ")
            
            if _msg != '':
                if ipython:
                    display(HTML(_msg))
                else:
                    print(_msg)
            
            # Removes the unnecessary msg from queue. if,
            #  progress not True or _msg = ''
            if not progress or _msg == '':
                self.queue.pop()
            
            if data is not None:
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f'{key}: {value}')

                elif isinstance(data, (list,tuple)):
                    print(data)
                
                else:
                    if ipython:
                        display(data)
                    else:
                        print(data)
                        
        if self.verbose > 0:
            self._update_progress_bar()
        
    def _update_progress_bar(self):
        """
        DESCRIPTION:
            Internal method to display updated progress state. 
            
        PARAMETERS:
            None.
        
        RETURNS:
            None.
        
        RAISES:
            None.
        """
        if self.completed_jobs == self.total_jobs:
            self.prefix = "Completed:"
            
        # Compute the number of completed bars to be displayed.
        _fill_bar = int(self.BAR_SIZE*(self.completed_jobs/self.total_jobs))
        # Compute progress precentage.
        _progress_percent = int((self.completed_jobs/self.total_jobs)*100)
        # Format the progress bar.
        _msg = "{prefix} {start_boundary}{fill_bar}{balance_bar}{close_boundary} "\
               "{progress_precent}% - {completed_jobs}/{total_jobs}".format(
               prefix=self.prefix, 
               start_boundary=self.BOUNDARY_BAR,
               fill_bar=self.BAR*_fill_bar, 
               balance_bar=self.UNFILL_BAR*(self.BAR_SIZE-_fill_bar),
               close_boundary=self.BOUNDARY_BAR,
               progress_precent=_progress_percent,
               completed_jobs=self.completed_jobs,
               total_jobs=self.total_jobs)
        # Add padding to clear any leftover characters from the previous message.
        padded_msg = _msg.ljust(self.blank_space_len)
        # Display the formatted bar.
        print(padded_msg, end='\r', file=self.STDOUT, flush=True)
        self.blank_space_len = len(padded_msg)
