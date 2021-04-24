#!/usr/bin/env groovy

/**
* This can be used by Jenkins multibranch pipeline
* Documentation: https://www.jenkins.io/doc/book/pipeline/multibranch/
*/

node('master'){

    checkout scm
    sh 'python3 -m temp_venv'

    sh """#/bin/bash
        source temp_venv/bin/activate
        pip install -r requirements.txt
    """
}
