# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rameshchandra.d@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

teradataml garbage collector module
----------
The garbage collector functionality helps to collect & cleanup the temporary
output tables, views and scripts generated while executing teradataml.

"""
from os.path import expanduser
import teradataml.common as tdmlutil
import teradataml.context as tdmlctx
from teradataml.common.exceptions import TeradataMlException
from teradataml.common import pylogger
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.constants import TeradataConstants
from teradataml.options.configure import configure
from teradataml.utils.internal_buffer import _InternalBuffer
from teradatasql import OperationalError
import psutil
import getpass
import os

logger = pylogger.getLogger()


class GarbageCollector():
    """
    The class has functionality to add temporary tables/views/scripts/container to
    garbage collection, so that they can be dropped when connection is disconnected/lost.
    Writes to a output file where the database name & table/view/script names are persisted.
    """
    # Adding old garbage collector file name to support backward compatibility.
    __old_garbage_persistent_file_name = getpass.getuser() + "_garbagecollect.info"
    __garbagecollector_folder_name = '.teradataml'
    __contentseperator = ","
    __filenameseperator = "_"
    __version = "ver1.0"
    __gc_tables = []
    __gc_views = []
    __gc_scripts = []
    __gc_container = []
    __gc_apply = []
    # Function to get the garbage collector file name specific to host and process.
    _get_gc_file_name = lambda: "{}_{}_{}_garbagecollect.info".format(
        getpass.getuser(),
        tdmlctx.context._get_host_ip(),
        str(os.getpid()))

    @staticmethod
    def _get_temp_dir_name():
        """
        DESCRIPTION:
            Function to return the directory where garbage collector file will be persisted.

        PARAMETERS:
            None.

        RETURNS:
            Garbage collector temporary directory name.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector._get_temp_dir_name()
        """
        # Default location for .teradataml is user's home directory if configure.local_storage is not set.
        tempdir = expanduser("~")
        tempdir = os.path.join(tempdir, GarbageCollector.__garbagecollector_folder_name)

        # set the .teradataml location to the location specified by the user.
        if configure.local_storage:
            tempdir = os.path.join(configure.local_storage, GarbageCollector.__garbagecollector_folder_name)
        return tempdir

    @staticmethod
    def __make_temp_file_name():
        """
        DESCRIPTION:
            Builds the temp directory where the garbage collector file will be persisted.

        PARAMETERS:
            None.

        RETURNS:
            Garbage collector temporary file name.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector.__build_temp_directory()
        """
        tempdir = GarbageCollector._get_temp_dir_name()
        os.makedirs(tempdir, exist_ok=True)
        tempfile = os.path.join(os.path.sep, tempdir, GarbageCollector._get_gc_file_name())
        return tempfile

    @staticmethod
    def __validate_gc_add_object(object_name,
                                 object_type=TeradataConstants.TERADATA_TABLE):
        """
        DESCRIPTION:
            Function to add table/view/script/container to the list of gc
            validations.

        PARAMETERS:
            object_name:
                Required Argument.
                Specifies the name of the table/view/script/container to be
                validated for GC.
                Types: str

            object_type:
                Optional Argument.
                Specifies the type of object (table/view/script/container).
                Default Values: TeradataConstants.TERADATA_TABLE
                Types: TeradataConstants

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector.__validate_gc_add_object(object_name, object_type)
        """
        if object_type == TeradataConstants.TERADATA_TABLE:
            GarbageCollector.__gc_tables.append(object_name)
        elif object_type == TeradataConstants.TERADATA_VIEW:
            GarbageCollector.__gc_views.append(object_name)
        elif object_type == TeradataConstants.CONTAINER:
            GarbageCollector.__gc_container.append(object_name)
        elif object_type == TeradataConstants.TERADATA_APPLY:
            GarbageCollector.__gc_apply.append(object_name)
        else:
            GarbageCollector.__gc_scripts.append(object_name)

    @staticmethod
    def __validate_gc():
        """
        DESCRIPTION:
            Function validates whether all created tables/views/scripts/container
            are removed or not.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            RuntimeError - If GC is not done properly.

        EXAMPLES:
            GarbageCollector.__validate_gc()
        """
        raise_error = False
        err_msg = ""
        if len(GarbageCollector.__gc_tables) != 0:
            err_msg = "Failed to cleanup following tables: {}\n".format(str(GarbageCollector.__gc_tables))
            raise_error = True
        if len(GarbageCollector.__gc_views) != 0:
            err_msg = "{}Failed to cleanup following views: {}\n".format(err_msg, str(GarbageCollector.__gc_views))
            raise_error = True
        if len(GarbageCollector.__gc_scripts) != 0:
            err_msg = "{}Failed to cleanup following STO scripts: {}\n".format(err_msg, str(GarbageCollector.__gc_scripts))
            raise_error = True
        if len(GarbageCollector.__gc_apply) != 0:
            err_msg = "{}Failed to cleanup following OpenAF scripts: {}\n".format(err_msg, str(GarbageCollector.__gc_apply))
            raise_error = True
        if raise_error:
            raise RuntimeError(err_msg)

    @staticmethod
    def _add_to_garbagecollector(object_name,
                                 object_type=TeradataConstants.TERADATA_TABLE):
        """
        DESCRIPTION:
            Add database name & temporary table/view/script name to the garbage collector.

        PARAMETERS:
            object_name:
                Required Argument.
                Name of the temporary table/view/script along with database name, container.
                that needs to be garbage collected.
                Note:
                    If "object_type" is TeradataConstants.TERADATA_APPLY, then the format of
                    "object_name" should be <user_env_name(str)>::<apply_script_name>.
                Types: str

            object_type:
                Optional Argument.
                Specifies the type of object to be added to Garbage Collector.
                Default Values: TeradataConstants.TERADATA_TABLE
                Types: TeradataConstant

        RETURNS:
            True, if successful.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector._add_to_garbagecollector(object_name = "temp"."temp_table1")
        """
        # Use global lock while writing to the garbage collector file.
        with _InternalBuffer.get("global_lock"):
            if object_name and object_type:
                try:
                    tempfilename = GarbageCollector.__make_temp_file_name()
                    writecontent = str(GarbageCollector.__version) + "," + str(os.getpid())
                    writecontent += "," + str(object_type.value)
                    writecontent += "," + object_name + "\n"
                    with open(tempfilename, 'a+') as fgc:
                        fgc.write(writecontent)
                    if configure._validate_gc:
                        GarbageCollector.__validate_gc_add_object(object_name, object_type)
                except TeradataMlException:
                    raise
                except Exception as err:
                    logger.error(Messages.get_message(MessageCodes.TDMLDF_CREATE_GARBAGE_COLLECTOR) + str(err))
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_CREATE_GARBAGE_COLLECTOR),
                                                MessageCodes.TDMLDF_CREATE_GARBAGE_COLLECTOR) from err
                finally:
                    if fgc is not None:
                        fgc.close()
        return True

    @staticmethod
    def __deleterow(content_row, file_name):
        """
        DESCRIPTION:
            Deletes an entry from persisted file.

        PARAMETERS:
            content_row:
                Required Argument.
                Specifies the text of row to delete from the persisted file.
                Types: str
            
            file_name:
                Required Argument.
                Specifies the name of the file to delete the row.
                Types: str

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector._deleterow(content_row = 'ver1.0,72136,3,"alice"."temp_table_gbview1"')
        """
        try:
            if not os.path.isfile(file_name):
                return True
            with open(file_name, 'r+') as fgc:
                output = fgc.readlines()
                fgc.seek(0)
                for dbtablename in output:
                    if content_row != dbtablename.strip():
                        fgc.write(dbtablename)
                fgc.truncate()
        except Exception as e:
            raise
        finally:
            if fgc and fgc is not None:
                fgc.close()

    @staticmethod
    def __delete_gc_tempdir_local_file(db_object, object_type=TeradataConstants.TERADATA_TABLE):
        """
        DESCRIPTION:
            Creates path to the file in temp directory on client machine
            and deletes the file.

        PARAMETERS:
            db_object:
                Required Argument.
                Specifies the name of the file/script to be deleted.
                Types: str

            object_type:
                Optional Argument.
                Specifies the type of the object (table/view/script) to be deleted.
                Default Value: TeradataConstants.TERADATA_TABLE
                Types: TeradataConstants

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector.__delete_gc_tempdir_local_file(
                'ALICE.ml__script_executor__<uniqueID>.py', TeradataConstants.TERADATA_TABLE)
        """
        try:
            tempdir = GarbageCollector._get_temp_dir_name()
            script_alias = tdmlutil.utils.UtilFuncs._teradata_unquote_arg(
                tdmlutil.utils.UtilFuncs._extract_table_name(db_object), quote='"')

            if object_type == TeradataConstants.TERADATA_APPLY.value:
                # Apply script is stored in the format <user_env_name>::<apply_script_name>.
                _, script_file = script_alias.split("::")
                script_alias = script_file

            # Currently assumed that the file name will be '<UIF_ID>.py'.
            # That is how the scripts will be created and installed from teradataml.
            file_name = os.path.join(tempdir, script_alias)
            GarbageCollector._delete_local_file(file_name)
        except Exception as e:
            raise

    @staticmethod
    def _delete_object_entry(objects_to_delete,
                             object_type=TeradataConstants.TERADATA_TABLE,
                             remove_entry_from_gc_list=False):
        """
        DESCRIPTION:
            Deletes an entry of table/view/script from persisted file.
            This makes sure that the object(s) is/are not garbage collected.

        PARAMETERS:
            objects_to_delete:
                Required Argument.
                Specifies the names of the table/view/script to be deleted.
                Types: str or list of str

            object_type:
                Optional Argument.
                Specifies the type of the object (table/view/script) to be deleted.
                Note:
                    Pass None, when object type is not available. In this case, the given object will be
                    removed from GC file based on just object name and current process id.
                Default Value: TeradataConstants.TERADATA_TABLE
                Types: TeradataConstants

            remove_entry_from_gc_list:
                Optional Argument.
                Specifies whether to delete the entry from one of the following:
                * __gc_tables - list of tables created
                * __gc_views - list of views created
                * __gc_scripts - list of STO scripts installed
                * __gc_apply - list of OpenAF scripts installed
                When set to True, the entry is removed from the appropriate list.
                This argument comes in handy for the GC validation to
                make sure that all intended tables/views/scripts are dropped by GC.
                Default Value: False
                Types: bool

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector._delete_table_view_entry(objects_to_delete = 'temp.temp_table1')
        """
        from teradataml.common.utils import UtilFuncs
        objects_to_delete = UtilFuncs._as_list(objects_to_delete)

        try:
            tempfilename = GarbageCollector.__make_temp_file_name()
            if not os.path.isfile(tempfilename):
                return True
            with open(tempfilename, 'r+') as fgc:
                output = fgc.readlines()
                fgc.seek(0)
                for db_object_entry in output:
                    record_parts = db_object_entry.strip().split(GarbageCollector.__contentseperator)
                    if len(record_parts) < 2:
                        # If record is empty, just continue.
                        continue
                    contentpid = int(record_parts[1].strip())
                    db_object_type = int(record_parts[2].strip())
                    db_object = record_parts[3].strip()

                    _added_in_gc_file = False # Set to True if the entry is added to GC file.

                    # Avoid substring matches by comparing object names in full.
                    # Also make sure to check for the pid.
                    if object_type and not (db_object in objects_to_delete
                            and object_type.value == db_object_type
                            and int(os.getpid()) == contentpid):
                        fgc.write(db_object_entry)
                        _added_in_gc_file = True

                    elif object_type is None:
                        if db_object in objects_to_delete and int(os.getpid()) == contentpid:
                            # Skip adding to GC file if the object is being deleted but object_type is passed as None.
                            pass
                        else:
                            fgc.write(db_object_entry)
                            _added_in_gc_file = True


                    if not _added_in_gc_file and remove_entry_from_gc_list and configure._validate_gc:
                        # Delete the entry from gc lists if required.
                        GarbageCollector.__delete_object_from_gc_list(db_object, object_type)


                    # If object is a script, also delete the local copy of the file.
                    if not _added_in_gc_file and object_type in \
                        [TeradataConstants.TERADATA_SCRIPT,
                         TeradataConstants.TERADATA_APPLY,
                         TeradataConstants.TERADATA_TEXT_FILE,
                         TeradataConstants.TERADATA_LOCAL_SCRIPT]:
                        GarbageCollector.__delete_gc_tempdir_local_file(db_object, object_type)
                fgc.truncate()
        except Exception as e:
            raise
        finally:
            if fgc and fgc is not None:
                fgc.close()

    @staticmethod
    def __delete_object_from_gc_list(object_name, object_type=TeradataConstants.TERADATA_TABLE):
        """
        DESCRIPTION:
            Deletes an entry of table/view/script from gc list when configure option
            '_validate_gc' is set to 'True'.

        PARAMETERS:
            object_name:
                Required Argument.
                Specifies the name of the table/view/script to be deleted.
                Types: str

            object_type:
                Optional Argument.
                Specifies the type of the object (table/view/script) to be deleted.
                Default value: TeradataConstants.TERADATA_TABLE
                Types: TeradataConstant

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector._delete_object_from_gc_list(object_name = 'temp.temp_table1')
            GarbageCollector._delete_object_from_gc_list(object_name = 'temp.temp_view1',
                                                         object_type = TeradataConstants.TERADATA_VIEW)
            GarbageCollector._delete_object_from_gc_list(object_name = 'temp.temp_script1',
                                                         object_type = TeradataConstants.TERADATA_SCRIPT)
            GarbageCollector._delete_object_from_gc_list(object_name = 'temp.temp_script1',
                                                         object_type =
                                                         TeradataConstants.TERADATA_LOCAL_SCRIPT)
            GarbageCollector._delete_object_from_gc_list(object_name = '7efhghsghg',
                                                         object_type =
                                                         TeradataConstants.CONTAINER)
        """
        if configure._validate_gc:
            if TeradataConstants.TERADATA_TABLE == object_type:
                GarbageCollector.__gc_tables.remove(object_name)
            elif TeradataConstants.TERADATA_VIEW == object_type:
                GarbageCollector.__gc_views.remove(object_name)
            elif TeradataConstants.CONTAINER == object_type:
                GarbageCollector.__gc_container.remove(object_name)
            elif TeradataConstants.TERADATA_APPLY == object_type:
                GarbageCollector.__gc_apply.remove(object_name)
            elif TeradataConstants.TERADATA_SCRIPT == object_type:
                GarbageCollector.__gc_scripts.remove(object_name)
            else:
                # If none of the conditions met, then try removing from all.
                _all_gc_lists = [GarbageCollector.__gc_tables, GarbageCollector.__gc_views,
                                 GarbageCollector.__gc_scripts, GarbageCollector.__gc_container,
                                 GarbageCollector.__gc_apply]
                for _list in _all_gc_lists:
                    try:
                        _list.remove(object_name)
                    except ValueError:
                        # If the object is not found in the list, just ignore.
                        pass

    @staticmethod
    def _delete_local_file(file_path):
        """
        DESCRIPTION:
            Function to delete the specified local file.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies the path of the file to be deleted.
                Types: str

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector._delete_local_file(file_path = '.teradataml/ml__1603874893436650.py')
        """
        try:
            os.remove(file_path)
        except:
            pass

    @staticmethod
    def _cleanup_garbage_collector():
        """
        DESCRIPTION:
            Drops the tables/views/scripts/container that are garbage collected.

        PARAMETERS:
            None.

        RETURNS:
            True, when successful.

        RAISES:
            None.

        EXAMPLES:
            GarbageCollector._cleanup_garbage_collector()
        """
        try:
            td_connection = tdmlctx.context.get_connection()
            # Get the temp directory where garbage collector file is persisted.
            tempdir = GarbageCollector._get_temp_dir_name()
            # Garbage collect file that is created by the current host and current process.
            # Also check if file is not of current process and associated process is
            # currently running in the system or not.
            # Walk through the temp directory and filter garbage collector files.
            tempfiles = []
            for root, _, files in os.walk(tempdir):
                for file in files:
                    if file.endswith('_garbagecollect.info'):
                        try:
                            filepath = os.path.join(root, file)
                            fileparts = file.split(GarbageCollector.__filenameseperator)
                            hostname = fileparts[1]
                            filepid = int(fileparts[2])
                            # Check for both host ip and hostname in case user passed hostname for creating connection.
                            if hostname == tdmlctx.context._get_host_ip() or hostname == tdmlctx.context._get_host():
                                if filepid == os.getpid() or not psutil.pid_exists(filepid):
                                    tempfiles.append(filepath)
                        except (IndexError, ValueError):
                            # Handle the case where the filename format is not as expected
                            # check if old garbage collector file is present.
                            if file == GarbageCollector.__old_garbage_persistent_file_name:
                                tempfiles.append(filepath)

            # Process each garbage collector file.
            if len(tempfiles) == 0:
                return True
            else:
                for tempfilename in tempfiles:
                    if not os.path.isfile(tempfilename):
                        return True
                    with open(tempfilename, 'r+') as fgc:
                        content = fgc.readlines()

                    for contentrecord in content:
                        contentrecord = contentrecord.strip()
                        if (td_connection is not None) and (len(contentrecord) > 0):
                            try:
                                recordparts = contentrecord.split(GarbageCollector.__contentseperator)
                                object_type = int(recordparts[2].strip())
                                database_object = recordparts[3].strip()

                                # Create the TeradataConstant to use with __delete_object_from_gc_list().
                                object_type_enum = TeradataConstants(object_type)

                                try:
                                    # Drop the table/view/script/container based on database object type retrieved from the collector file.
                                    # # Drop table.
                                    if TeradataConstants.TERADATA_TABLE.value == object_type:
                                        tdmlutil.utils.UtilFuncs._drop_table(database_object,
                                                                            check_table_exist=False)

                                    # # Drop view.
                                    elif TeradataConstants.TERADATA_VIEW.value == object_type:
                                        tdmlutil.utils.UtilFuncs._drop_view(database_object,
                                                                            check_view_exist=False)

                                    elif object_type in [TeradataConstants.TERADATA_LOCAL_SCRIPT.value,
                                                        TeradataConstants.TERADATA_TEXT_FILE.value]:
                                        GarbageCollector.__delete_gc_tempdir_local_file(database_object, object_type)

                                    # # Drop Apply script.
                                    elif TeradataConstants.TERADATA_APPLY.value == object_type:
                                        tdmlutil.utils.UtilFuncs._delete_script(database_object,
                                                                                file_type=object_type_enum)
                                        # Delete the script locally
                                        GarbageCollector.__delete_gc_tempdir_local_file(database_object, object_type)

                                    # # Drop STO script.
                                    else:
                                        tdmlutil.utils.UtilFuncs._delete_script(database_object,
                                                                                file_type=object_type_enum,
                                                                                check_script_exist=False)
                                        # Delete the script locally
                                        GarbageCollector.__delete_gc_tempdir_local_file(database_object, object_type)

                                    # Remove the entry for a table/view from GC, after it has been dropped.
                                    GarbageCollector.__deleterow(contentrecord, tempfilename)
                                    
                                    # Finally, delete the entry from gc lists if required.
                                    GarbageCollector.__delete_object_from_gc_list(database_object,
                                                                                object_type_enum)
                                except OperationalError as operr:
                                    # Remove the entry for a table/view/script even after drop has failed,
                                    # if that object does not exist.
                                    # Also added additional check for error when the database containing
                                    # the object doesn't exist anymore.
                                    if "[Teradata Database] [Error 3802] Database" in str(operr) or \
                                            "[Teradata Database] [Error 3807] Object" in str(operr) or \
                                            "[Teradata Database] [Error 9852] The file" in str(operr):
                                        GarbageCollector.__deleterow(contentrecord, tempfilename)
                                        # Delete entry from gc lists of required.
                                        GarbageCollector.__delete_object_from_gc_list(database_object,
                                                                                    object_type_enum)
                                except (TeradataMlException, RuntimeError) as err:
                                    if "Failed to execute get_env" in str(err) or \
                                        "Failed to execute remove_file" in str(err):
                                        # For removing files in OpenAF environment.
                                        GarbageCollector.__deleterow(contentrecord, tempfilename)
                                        # Delete entry from gc lists of required.
                                        GarbageCollector.__delete_object_from_gc_list(database_object,
                                                                                    object_type_enum)
                                except FileNotFoundError:
                                    # This will occur only when the item being deleted is a file,
                                    # and it's local copy is not found.
                                    GarbageCollector.__deleterow(contentrecord, tempfilename)
                                    if object_type == TeradataConstants.TERADATA_APPLY:
                                        GarbageCollector.__gc_apply.remove(database_object)
                                    elif object_type == TeradataConstants.TERADATA_SCRIPT:
                                        GarbageCollector.__gc_scripts.remove(database_object)
                            except Exception as err:
                                pass
                    # delete empty file itself after deleting the entry from the file
                    if os.path.getsize(tempfilename) == 0:
                        GarbageCollector._delete_local_file(tempfilename)
        except Exception as e:
            logger.error(Messages.get_message(MessageCodes.TDMLDF_DELETE_GARBAGE_COLLECTOR) + str(e))
        finally:
            if configure._validate_gc:
                GarbageCollector.__validate_gc()
        return True
