#!/usr/bin/env groovy
/**
* This job monitor web page by running every 5 minutes
* How to use this:
* 1. Put your configuration file in Jenkins secrets. docs: https://www.jenkins.io/doc/developer/security/secrets/
* 2. Create Pipeline job in Jenkins
* 3. Copy this file or configure jenkins to fetch this from git
* 4. Trigger job in first time
* Remember to put kafka_to_posrgres script running also
*/

node('master'){

    // Build every 5 minutes
    properties([pipelineTriggers([cron('H/5 * * * *')])])
    deleteDir()

    git(url:'https://github.com/OPpuolitaival/web_monitor.git', branch:'main')
    withCredentials([file(credentialsId: 'config-file', variable: 'FILE')]) {

        stage('test'){
            def exitCode = sh(returnStatus: true, script: """#/bin/bash
                python3 -m venv temp_venv
                source temp_venv/bin/activate
                pip install -r requirements.txt
                cd pytests
                mv ${FILE} config.json
                pytest --junitxml=junit.xml --config config.json .
            """)

            // Make test report visible in Jenkins also
            junit('pytests/junit.xml')

            if (exitCode == 1) {
                echo "Failures in test execution"
                archiveArtifacts(artifacts:"*.log")
            }
            if (exitCode > 1) {
                archiveArtifacts(artifacts:"*.log")
                error "Pytest cannot run tests right. Check your configuration!"
            }
        }
    }
}