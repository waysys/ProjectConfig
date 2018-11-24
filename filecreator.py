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

"""
This module contains the BatFileCreator and PropertiesCreator classes.
"""

from projectconfigexception import ProjectConfigException
from string import Template

rungfit_template = """
SET DRIVE=${root_dir}
${java_list}
"""

java_templte = """
java  -ea -jar %DRIVE%\\EXEC\\runGFIT.jar -prop %DRIVE%${property_file}
"""

properties_template = """
url=${url}
username=su
password=gw
testsuite=${testsuite}
reports=${reports}
timeout=960000
"""

ports = {
    "bc": "8580",
    "cc": "8080",
    "pc": "8180"
}

# -------------------------------------------------------------------------------
#  File Creator
# -------------------------------------------------------------------------------


class FileCreator:
    """This class is the parent class for BatFileCreator PropertiesCreator"""

    # ---------------------------------------------------------------------------
    #  Constructor
    # ---------------------------------------------------------------------------

    def __init__(self, project_config):
        """Initialize this class.

        Argument:
            project_config - an instance of the ProjectConfig class.
        """
        assert project_config is not None, "Project config instance must not be null"
        self._project_config = project_config
        self._drive = None
        self._project_dir = None
        self._test_suites = None
        return

    # ---------------------------------------------------------------------------
    #  Properties
    # ---------------------------------------------------------------------------

    @property
    def pcf(self):
        """Return the instnace of the product config"""
        return self._project_config

    @property
    def drive(self):
        """Return the path to the root of the exec folders, including the GFIT directory name"""
        if self._drive is None:
            self._drive = self.pcf.root
            self._drive = self._drive.replace("/", "\\")
        return self._drive

    @property
    def project_dir(self):
        """Return the path including the project dire"""
        if self._project_dir is None:
            self._project_dir = self.drive + "\\" + self.pcf.environment + "\\" + \
                                self.pcf.product + "\\" + self.pcf.project
        return self._project_dir

    @property
    def test_suites(self):
        """Return a list of test suites"""
        if self._test_suites is None:
            self._test_suites = self.pcf.test_suites
        return self._test_suites

    @property
    def product(self):
        """Return the product abbreviation in lower case
        """
        prod = self.pcf.product
        prod = prod.lower()
        return prod

    # ---------------------------------------------------------------------------
    #  Operations
    # ---------------------------------------------------------------------------

    @staticmethod
    def open_file(filename):
        """Open the rungfit.bat file for writing.

        Argument:
            filename - the full path name of the file
        """
        try:
            file = open(filename, mode="w")
        except Exception as e:
            message = "Unable to open " + filename + " because " + str(e)
            raise ProjectConfigException(message)
        return file

    def generate_property_filename(self, test_suite):
        """Return the full path name of the properties file"""
        path = "\\"
        path += self.pcf.environment + "\\"
        path += self.pcf.product + "\\"
        path += self.pcf.project + "\\"
        path += test_suite + ".properties"
        path = path.replace("/", "\\")
        return path

# -------------------------------------------------------------------------------
#  BatFileCreator
# -------------------------------------------------------------------------------


class BatFileCreator(FileCreator):
    """This class generates the batch file to run the tests."""

    # ---------------------------------------------------------------------------
    #  Constructor
    # ---------------------------------------------------------------------------

    def __init__(self, project_config):
        """Initialize this class.

        Argument:
            project_config - an instance of the ProjectConfig class.
        """
        super(BatFileCreator, self).__init__(project_config)
        return

    # ---------------------------------------------------------------------------
    #  Properties
    # ---------------------------------------------------------------------------

    @property
    def file_name(self):
        """Return the full path name of the rungfit.bat file"""
        path = self.project_dir + "/" + "rungfit.bat"
        return path

    # ---------------------------------------------------------------------------
    #  Operations
    # ---------------------------------------------------------------------------

    def create_rungfit(self):
        """Generate the rungfit.bat file in the project directory"""
        file = None
        try:
            file = FileCreator.open_file(self.file_name)
            content = self.generate_content()
            file.write(content)
        except ProjectConfigException as e:
            raise e
        finally:
            if file is not None:
                file.close()

    def generate_content(self):
        """Return the content of the rungfit.bat file"""
        java_lines = ""
        for test_suite in self.test_suites:
            java_line = self.generate_java_line(test_suite)
            java_lines += java_line + "\n"
        subs = {"root_dir": self.drive,
                "java_list": java_lines}
        content = Template(rungfit_template).substitute(subs)
        return content

    def generate_java_line(self, test_suite):
        """Return the content of the call to the java .jar file"""
        subs = {
            "property_file": self.generate_property_filename(test_suite)
        }
        java_line = Template(java_templte).substitute(subs)
        return java_line

# -------------------------------------------------------------------------------
#  Property Creator
# -------------------------------------------------------------------------------


class PropertyCreator(FileCreator):
    """
    This class generates the properties files for the project.
    """

    # ---------------------------------------------------------------------------
    #  Constructor
    # ---------------------------------------------------------------------------

    def __init__(self, project_config):
        """Initialize this class.

        Argument:
            project_config - an instance of the ProjectConfig class.
        """
        super(PropertyCreator, self).__init__(project_config)
        return

    # ---------------------------------------------------------------------------
    #  Properties
    # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------
    #  Operations
    # ---------------------------------------------------------------------------

    def create_properties_files(self):
        """Create the required properties files"""
        for test_suite in self.test_suites:
            self.create_properties_file(test_suite)
        return

    def create_properties_file(self, test_suite):
        """Create a single property file for the test suite.

        Argument:
            test_suite - the name of the test suite
        """
        file = None
        try:
            file = FileCreator.open_file(self.generate_property_filename(test_suite))
            content = self.generate_content(test_suite)
            file.write(content)
        except ProjectConfigException as e:
            raise e
        finally:
            if file is not None:
                file.close()

    def generate_property_filename(self, test_suite):
        """Generate the full file name of the property.

        Argument:
            test_suite - the name of the test suite
        """
        path = self.pcf.root + "\\"
        path += self.pcf.environment + "\\"
        path += self.pcf.product + "\\"
        path += self.pcf.project + "\\"
        path += test_suite + ".properties"
        path = path.replace("/", "\\")
        return path

    def generate_content(self, test_suite):
        """
        Generate the content of the properies file.

        Argument:
            test_suite - the name of the test suite
        """
        url = self.generate_url()
        ts = self.generate_test_suite_path(test_suite)
        reports = self.generate_reports_path(test_suite)
        subs = {
            "url": url,
            "testsuite": ts,
            "reports": reports
        }
        content = Template(properties_template).substitute(subs)
        return content

    def generate_url(self):
        """
        Return the URL for the appropriate server and product
        """
        product = self.product
        assert product in ports, "Product abbreviation is inccorrect - " + product
        url = "http://" + self.pcf.server + ":" + ports[product] + "/" + product
        return url

    def generate_test_suite_path(self, test_suite):
        """
        Generate the full path to the test suite
        """
        path = self.pcf.root + "/" + "TESTSUITES/" + self.pcf.product
        path += "/" + self.pcf.project
        path += "/" + test_suite
        path = PropertyCreator.double_backslash(path)
        return path

    def generate_reports_path(self, test_suite):
        """Generate the path for reports.

        Argument:
            test_suite - the name of the test suite
        """
        path = self.pcf.workspace + "/" + self.pcf.environment + "/"
        path += self.pcf.project + "/" + test_suite
        path = PropertyCreator.double_backslash(path)
        return path

    @staticmethod
    def double_backslash(path):
        """In a path, make sure all separators are double \

        Argument:
            path - a path with possible \ and / separators
        """
        path = path.replace("\\", "/")
        path = path.replace("/", "\\\\")
        return path
