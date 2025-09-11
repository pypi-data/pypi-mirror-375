# #############################################################################
# 
# Copyright 2019 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Abhinav Sahu (abhinav.sahu@teradata.com)
# Secondary Owner: 
# 
# This file is used to get version information of the client packages (dependencies) 
# installed & server information for Build/Release for debugging purposes.
# 
# ############################################################################# 

import importlib
import locale
import os
import platform
import struct
import sys
import warnings
from teradataml.context.context import get_connection
from teradataml.options.display import display
from teradataml.options.configure import configure
from teradataml.utils.utils import execute_sql


def __get_sys_info():
    """
    Returns system information as a list.

    PARAMETERS:
        None.

    RETURNS:
        A list of tuples with key value pairs of the underlying system information.

    RAISES:
        None.

    EXAMPLES:
        __get_sys_info()
    """

    sysInfo = []

    try:
        (sysname, nodename, release,
         version, machine, processor) = platform.uname()
        sysInfo.extend([
            ("python", '.'.join(map(str, sys.version_info))),
            ("python-bits", struct.calcsize("P") * 8),
            ("OS", "{sysname}".format(sysname=sysname)),
            ("OS-release", "{release}".format(release=release)),
            ("machine", "{machine}".format(machine=machine)),
            ("processor", "{processor}".format(processor=processor)),
            ("byteorder", "{byteorder}".format(byteorder=sys.byteorder)),
            ("LC_ALL", "{lc}".format(lc=os.environ.get('LC_ALL', "None"))),
            ("LANG", "{lang}".format(lang=os.environ.get('LANG', "None"))),
            ("LOCALE", '.'.join(map(str, locale.getlocale()))),
        ])
    except (KeyError, ValueError):
        pass

    return sysInfo


def show_versions():
    """
    Displays client information, version information for client package 
    dependencies and server information.

    PARAMETERS:
        None.

    RETURNS:
        None.

    RAISES:
        ImportError, Warnings

    EXAMPLES:
        >>> import teradataml as tdml
        >>> tdml.show_versions()
        >>> INSTALLED VERSIONS: Client
            --------------------------
            python: 3.5.4.final.0
            python-bits: 64
            OS: Windows
            OS-release: 10
            machine: AMD64
            processor: Intel64 Family 6 Model 142 Stepping 10, GenuineIntel
            byteorder: little
            LC_ALL: None
            LANG: en
            LOCALE: None.None
            
            pandas: 0.24.2
            sqlalchemy: 1.3.2
            teradatasqlalchemy: 16.20.0.5
            teradatasql: 16.20.0.41
            teradataml: 16.20.0.4
            
            INSTALLED VERSIONS: Server
            --------------------------
            BUILD_VERSION: 08.10.00.00-e84ce5f7
            RELEASE: Vantage 1.1 GA
    """
    
    sys_info = __get_sys_info()

    deps = [
        # (MODULE_NAME, f(mod) -> mod version)
        ("pandas", lambda mod: mod.__version__),
        ("sqlalchemy", lambda mod: mod.__version__),
        ("teradatasqlalchemy", lambda mod: mod.__version__),
        ("teradatasql", lambda mod: mod.vernumber.sVersionNumber),
        ("teradataml", lambda mod: mod.__version__),
    ]

    deps_server = list()
    if get_connection() is not None:
        try:
            vantage_ver_qry = "select * from pm.versionInfo"
            result = execute_sql(vantage_ver_qry)
            for row in result:
                deps_server.append(row)
        except:
            # Raise a warning here.
            warnings.warn("Server information is available starting Vantage 1.1")
    else:
        # Raise a warning here.
        warnings.warn("Server information requires a working connection object.")
        
    deps_client = list()
    for (modname, ver_f) in deps:
        try:
            if modname in sys.modules:
                mod = sys.modules[modname]
            else:
                mod = importlib.import_module(modname)
            ver = ver_f(mod)
            deps_client.append((modname, ver))
        except ImportError:
            deps_client.append((modname, None))
              
    print("\nINSTALLED VERSIONS: Client")
    print("--------------------------")
    for k, stat in sys_info:
        print("{k}: {stat}".format(k=k, stat=stat))

    print("")
    for k, stat in deps_client:
        print("{k}: {stat}".format(k=k, stat=stat))
    
    print("\nINSTALLED VERSIONS: Server")
    print("--------------------------")
    for k, stat in deps_server:
        print("{k}: {stat}".format(k=k, stat=stat))

def print_options():
    """
    DESCRIPTION:
        Displays both configure and display options set in the current user's session.

    PARAMETERS:
        None.

    RETURNS:
        None.

    RAISES:
         Warnings

    EXAMPLES:
        >>> import teradataml as tdml
        >>> tdml.print_options()
        Display Options
        ------------------
        display.max_rows = 10
        display.precision = 3
        display.byte_encoding = base16
        display.print_sqlmr_query = False
        display.suppress_vantage_runtime_warnings = False

        Configure Options
        ------------------
        configure.default_varchar_size = 1024
        configure.column_casesensitive_handler = False
        configure.vantage_version = vantage2.0
        configure.val_install_location = None
    """
    display_options =  [params for params in dir(display) if not params.startswith('_')]
    configure_options = [params for params in dir(configure) if not params.startswith('_')]

    print("Display Options")
    print("------------------")
    for option in display_options:
        print("{0} = {1}".format(option, getattr(display, option, None)))

    print("\nConfigure Options")
    print("------------------")
    for option in configure_options:
        if option == "vantage_version" and get_connection() is None:
            print("Option 'vantage_version' information requires a working connection object.")
        else:
            print("{0} = {1}".format(option, getattr(configure, option, None)))