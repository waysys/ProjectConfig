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

"""
This module outputs the Jenkins pipeline for the project.
"""

from string import Template

pipeline_template = """
pipeline {
    agent {
        node {
            label "master"
            customWorkspace "${workspace}"
        }
    }
    stages {
        stage('${project_name}') {
            steps {
                bat "${run_file}"
            }
        }
    }
    post {
        always {
            junit '*.xml'
        }
    }
}
"""

# -------------------------------------------------------------------------------
#  Class description
# -------------------------------------------------------------------------------


class PipelineGenerator:
    """
    This class generates the declarative pipeline code for Jenkins for this project.
    """

    def __init__(self, project_config):
        """Initialize the class.

        Argument:
            project_config - the project configuration class with the properties
               needed to produce the pipeline.
        """
        assert project_config is not None, "Project configuration argument must not be None"
        self._project_config = project_config
        return

    def output_pipeline(self, workspace_path, run_file):
        """
        Output the pipeline to the console.

        Arguments:
            workspace_path - the full path of the workspace
            run_file - the full path of the .bat file
        """
        subs = {
            "workspace": workspace_path,
            "project_name": self._project_config.project,
            "run_file": run_file
        }
        content = Template(pipeline_template).substitute(subs)
        # Replace backslash with forward slash which can be handled Jenkins.
        # Jenkins treats the backslash as an escape characters in pipelines.
        content = content.replace("\\", "/")
        print(content)
        return
