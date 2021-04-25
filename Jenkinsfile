#!/usr/bin/env groovy

/**
 * This is doing basic checks in Jenkins when changes are done in branches or pull requests
 * Need to be configure in Jenkins multibranch pipeline
 * Documentation: https://www.jenkins.io/doc/book/pipeline/multibranch/
 */

def run_with_virtualenv(command) {
    sh """#/bin/bash
        source temp_venv/bin/activate
        ${command}
    """
}

node('master') {

    checkout scm
    stage('Setup') {
        sh 'python3 -m venv temp_venv'
        run_with_virtualenv('pip install -r requirements.txt')
    }
    stage('Pylint') {
        run_with_virtualenv('pylint --ignore-patterns=temp_venv *')
    }
}
