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
__version__ = "1.01"

from projectconfigexception import ProjectConfigException
import xml.etree.ElementTree as Et
from pathlib import Path

"""
This module contains the ProjectConfig class that provides an interface to the
project config XML file.
"""


# -------------------------------------------------------------------------------
#  Class description
# -------------------------------------------------------------------------------

class ProjectConfig:
    """This class reads the project config file and makes the contents available to
    other classes.
    """

    # ---------------------------------------------------------------------------
    #  Constructor
    # ---------------------------------------------------------------------------

    def __init__(self, project_config_filename):
        """Initialize the class.

        Argument:
            project_config_filename -  the full path to the project config file.
        """
        assert project_config_filename is not None, "Project config filename must not be null"
        assert len(project_config_filename) > 0, "Project config filename must not be empty"
        self._filename = project_config_filename
        self._configuration = None
        self._root = None
        self._workspace = None
        self._project = None
        self._environment = None
        self._product = None
        self._test_suites = None
        self._server = None
        return

    # ---------------------------------------------------------------------------
    #  Properties
    # ---------------------------------------------------------------------------

    @property
    def configuration(self):
        """
        Return the /TestConfiguration element
        """
        assert self._configuration is not None, "Top level element has not been set"
        return self._configuration

    @property
    def root(self):
        """Return the root location of the GFIT project files."""
        if self._root is None:
            self._root = ProjectConfig.fetch_text(self.configuration, "Root")
        return self._root

    @property
    def workspace(self):
        """Return the base workspace directory"""
        if self._workspace is None:
            self._workspace = ProjectConfig.fetch_text(self.configuration, "Workspace")
        return self._workspace

    @property
    def project(self):
        """Return the name of the project"""
        if self._project is None:
            self._project = ProjectConfig.fetch_text(self.configuration, "Project")
        return self._project

    @property
    def environment(self):
        """Return the name of the environment"""
        if self._environment is None:
            self._environment = ProjectConfig.fetch_text(self.configuration, "Environment")
        return self._environment

    @property
    def product(self):
        """Return the abbreviation for the Guidewire product (PC, BC, CC)"""
        if self._product is None:
            self._product = ProjectConfig.fetch_text(self.configuration, "Product")
            if self._product not in ["PC", "BC", "CC"]:
                message = "Invalid product abbreviation - " + self._product
                raise ProjectConfigException(message)
        return self._product

    @property
    def test_suites(self):
        """Return a list of the test suites for a project"""
        if self._test_suites is None:
            test_suite_root = ProjectConfig.fetch_element(self.configuration, "TestSuites")
            test_suite_elements = ProjectConfig.fetch_all_elements(test_suite_root, "TestSuite")
            self._test_suites = []
            for test_suite_element in test_suite_elements:
                self._test_suites.append(test_suite_element.text)
            if len(self._test_suites) == 0:
                message = "No test suites were found"
                raise ProjectConfigException(message)
        return self._test_suites

    @property
    def test_suite_directory(self):
        """
        Return the name of the directory that contains the test suites.  This directory usually has the same name
        as the Jenkins project name, but in some cases it will be different
        """
        suite_name = self.project
        if ProjectConfig.has_element(self.configuration, "SuiteDirectory"):
            suite_name = ProjectConfig.fetch_text(self.configuration, "SuiteDirectory")
        return suite_name

    @property
    def server(self):
        """
        Return the name of the server where the application is running
        """
        if self._server is None:
            self._server = ProjectConfig.fetch_text(self.configuration, "Server")
        return self._server

    # ---------------------------------------------------------------------------
    #  Operations
    # ---------------------------------------------------------------------------

    def parse(self):
        """
        Parse the project config file.
        """
        if not ProjectConfig.file_exists(self._filename):
            raise ProjectConfigException("Project config file does not exist - " + self._filename)
        try:
            tree = Et.parse(self._filename)
            root = tree.getroot()
            tag = root.tag
            if tag != "TestConfiguration":
                raise ProjectConfigException("Root element is not TestConfiguration - " + tag)
            self._configuration = root
        except Exception as e:
            raise ProjectConfigException(str(e))
        return

    @staticmethod
    def file_exists(filename):
        """
        Return true if the file exists and is readable
        """
        file = Path(filename)
        return file.is_file()

    @staticmethod
    def fetch_element(parent, tag):
        """
        Return the single element named in the tag argument. This method should be used only when
        only one element with this name is used.  If the element is not found, an exception
        is thrown.

        Argument:
            parent - the parent of the element being searched for
            tag - the name of the element to be retrieved

        Returns:
            The element being searched for.
        """
        assert tag is not None, "fetch_element: Tag must not be None"
        assert len(tag) > 0, "fetch_element: Tag must not be an empty string"
        assert parent is not None, "fetch_element: Parent of element " + tag + " must not be None"
        element = parent.find(tag)
        if element is None:
            message = "fetch_element: Element " + tag + " was not found in element " + parent.tag
            raise ProjectConfigException(message)
        return element

    @staticmethod
    def fetch_text(parent, tag):
        """
        Return the content of an element with the name equal to tag.  If the element is not found,
        an exception is thrown.

        Argument:
            parent - the parent of the element being searched for
            tag - the name of the element to be retrieved

        Returns:
            The content of the element being searched for.
        """
        element = ProjectConfig.fetch_element(parent, tag)
        return element.text

    @staticmethod
    def fetch_all_elements(parent, tag):
        """
        Return a list of subelements of the parent with the specified tag.

        Arguments:
            parent - the parent element being searched
            tag - the tag of the element
        """
        assert tag is not None, "fetch_all_element: Tag must not be None"
        assert len(tag) > 0, "fetch_all_element: Tag must not be an empty string"
        assert parent is not None, "fetch_all_element: Parent of element " + tag + " must not be None"
        elements = parent.findall(tag)
        if elements is None:
            elements = []
        return elements

    @staticmethod
    def has_element(parent, tag):
        """
        Return a list of subelements of the parent with the specified tag.

        Arguments:
            parent - the parent element being searched
            tag - the tag of the element
        """
        result = ProjectConfig.fetch_all_elements(parent, tag)
        return len(result) > 0
