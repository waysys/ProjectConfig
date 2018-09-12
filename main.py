# -------------------------------------------------------------------------------
#
#  Copyright (c) 2018 Waysys LLC
#
# -------------------------------------------------------------------------------
#
#  Waysys LLC MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF
#  THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
#  TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE, OR NON-INFRINGEMENT. CastleBay SHALL NOT BE LIABLE FOR
#  ANY DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR
#  DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.
#
# For further information, contact wshaffer@waysysweb.com
#
# -------------------------------------------------------------------------------


__author__ = 'Bill Shaffer'
__version__ = "1.00"

import sys
import traceback
from projectconfigexception import ProjectConfigException
from projectconfig import ProjectConfig
from pathlib import Path
from filecreator import BatFileCreator
from filecreator import PropertyCreator

"""
This module executes the Project Configuration tool.  This tool creates and checks
directories and generates the rungfit.bat and property files for the Jenkins project.
"""


# -------------------------------------------------------------------------------
#  Main Function
# -------------------------------------------------------------------------------


def main(project_config_filename):
    """
    Run the ProjectConfig program.

    Arguments:
        project_config_filename - the XML file with the project configuration
    """
    print("Starting ProjectConfig")
    try:
        process(project_config_filename)
    except ProjectConfigException as e:
        print("Error: " + str(e))
        info = sys.exc_info()
        tb = info[2]
        traceback.print_tb(tb)
        sys.exit(1)
    except Exception as e:
        print("Exception: " + str(e))
        info = sys.exc_info()
        tb = info[2]
        traceback.print_tb(tb)
        sys.exit(1)
    finally:
        print("Ending ProjectConfig")
    sys.exit(0)


def process(project_config_filename):
    """
    Process the project configuration specification.

    Arguments:
        project_config_filename - the XML file with the project configuration
    """
    project_config = ProjectConfig(project_config_filename)
    project_config.parse()
    validate_root(project_config.root)
    validate_workspace(project_config.workspace, project_config.environment, project_config.project)
    validate_exec_dir(project_config.root,
                      project_config.environment,
                      project_config.product,
                      project_config.project)
    validate_test_suites(project_config.root,
                         project_config.product,
                         project_config.project,
                         project_config.test_suites)
    bat_creator = BatFileCreator(project_config)
    bat_creator.create_rungfit()
    properties_creator = PropertyCreator(project_config)
    properties_creator.create_properties_files()
    return


def validate_root(root_dir):
    """Check that the root directory exists.  If not, throw an exception"""
    if not is_dir(root_dir):
        message = "Root directory does not exist - " + root_dir
        raise ProjectConfigException(message)
    return


def validate_workspace(workspace, environment, project):
    """Check that the components of the workspace are present"""
    if not is_dir(workspace):
        message = "Workspace directory does not exist - " + workspace
        raise ProjectConfigException(message)
    environ_path = workspace + "/" + environment
    if not is_dir(environ_path):
        message = "Environment directory in workspace does not exist - " + environ_path
        raise ProjectConfigException(message)
    project_path = environ_path + "/" + project
    if not is_dir(project_path):
        print("Creating workspace project directory " + project_path)
        create_dir(project_path)
    project_path = project_path.replace("/", "\\")
    print("Jenkins workspace is: " + project_path)
    return


def validate_exec_dir(root, environment, product, project):
    """Check that the exec directory is present.  If the final project directory is not
    present, create it.

    Arguments:
        root - the root exec directory
        environment - the environment: DEV, QA, etc.
        product - the abbreviation for the Guidewire product, for example BC
        project - the name of the Jenkins project

    """
    if not is_dir(root):
        message = "Root directory does not exist - " + root
        raise ProjectConfigException(message)
    environ_path = root + "/" + environment
    if not is_dir(environ_path):
        message = "Environment directory does not exist - " + environ_path
        raise ProjectConfigException(message)
    product_path = environ_path + "/" + product
    if not is_dir(product_path):
        message = "Product directory does not exist - " + product_path
        raise ProjectConfigException(message)
    project_path = product_path + "/" + project
    if not is_dir(project_path):
        print("Creating project directory - " + project_path)
        create_dir(project_path)
    batch_command = project_path + "/rungfit.bat"
    batch_command = batch_command.replace("/", "\\")
    print("Jenkins batch command is: " + batch_command)
    return project_path


def validate_test_suites(root, product, project, test_suites):
    """Check that the directories holding the test suites exist.

    Arguments:
        root - the root exec directory
        product - the Guidewire product abbreviation, for example BC
        project - the name of the project
        test_suites - a list of test suites
    """
    test_suite_root = root + "/TESTSUITES"
    if not is_dir(test_suite_root):
        message = "Test suite root  directory does not exist - " + test_suite_root
        raise ProjectConfigException(message)
    test_suite_product_dir = test_suite_root + "/" + product
    if not is_dir(test_suite_product_dir):
        message = "Test suite root  directory does not exist - " + test_suite_product_dir
        raise ProjectConfigException(message)
    test_suite_project_dir = test_suite_product_dir + "/" + project
    if not is_dir(test_suite_project_dir):
        message = "Test suite root  directory does not exist - " + test_suite_project_dir
        raise ProjectConfigException(message)
    for test_suite in test_suites:
        suite_dir = test_suite_project_dir + "/" + test_suite
        if not is_dir(suite_dir):
            message = "Suite directory does not exist - " + suite_dir
            raise ProjectConfigException(message)
    return


def is_dir(dir_name):
    """Return true if dir is an existing directory.

    Arguments:
        dir_name - the name of a directory
    """
    assert dir_name is not None, "Directory name must not be None"
    assert len(dir_name) > 0, "Directory name must not be an empty "
    adir = Path(dir_name)
    return adir.is_dir()


def create_dir(dir_name):
    """
    Create the directory with the name dir_name

    Arguments:
        dir_name - name of the directory
    """
    assert dir_name is not None, "Directory name must not be None"
    assert len(dir_name) > 0, "Directory name must not be an empty string"
    if not is_dir(dir_name):
        Path(dir_name).mkdir()
    assert is_dir(dir_name), "Directory was not created - " + dir_name
    return


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------


if __name__ == '__main__':
    """Run the ProjectConfig program"""
    if len(sys.argv) != 2:
        print("""
              To execute ProjectConfig, use this command:

              python main.py project_config_filename 
              """)
        sys.exit(1)
    main(sys.argv[1])
