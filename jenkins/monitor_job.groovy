#!/usr/bin/env groovy
/**
* This job monitor web page by running every now and then
*/

node('master'){

    git(url:'git@github.com:OPpuolitaival/web_monitor.git', credentialsId:'ssh-key')
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
            junit('junit.xml')

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