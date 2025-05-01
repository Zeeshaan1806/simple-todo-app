pipeline {
    agent any

    environment {
        SONAR_TOKEN = credentials('sonar-token')
        SONAR_HOST_URL = 'http://localhost:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checkout complete'
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    withSonarQubeEnv('SonarQube') {
                        bat '''
                        sonar-scanner.bat ^
                            -Dsonar.projectKey=simple-todo-app ^
                            -Dsonar.sources=. ^
                            -Dsonar.host.url=%SONAR_HOST_URL% ^
                            -Dsonar.login=%SONAR_TOKEN%
                        '''
                    }
                }
            }
        }

        stage('SCA - Dependency Check') {
            steps {
                bat 'dependency-check.bat --project "simple-todo-app"
