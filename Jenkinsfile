pipeline {
    agent any

    environment {
        SONAR_URL = 'http://localhost:9000'
        SONAR_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Wait for SonarQube') {
            steps {
                script {
                    def isWindows = isUnix() == false
                    retry(10) {
                        echo "Waiting for SonarQube to become healthy..."
                        if (isWindows) {
                            bat """
                                curl -f %SONAR_URL%/api/system/health || exit 1
                            """
                        } else {
                            sh """
                                curl -f ${env.SONAR_URL}/api/system/health || exit 1
                            """
                        }
                        sleep 10
                    }
                }
            }
        }

        stage('Run SonarQube Scan') {
            steps {
                withSonarQubeEnv('MySonarQubeServer') {
                    script {
                        def isWindows = isUnix() == false
                        if (isWindows) {
                            bat 'mvn clean verify sonar:sonar'
                        } else {
                            sh 'mvn clean verify sonar:sonar'
                        }
                    }
                }
            }
        }

        stage('Run OWASP Dependency-Check') {
            steps {
                script {
                    def isWindows = isUnix() == false
                    if (isWindows) {
                        bat 'dependency-check.bat --project simple-todo-app --scan . --format ALL --out reports'
                    } else {
                        sh './dependency-check.sh --project simple-todo-app --scan . --format ALL --out reports'
                    }
                }
            }
        }

        stage('Run Trivy Scan') {
            steps {
                script {
                    def isWindows = isUnix() == false
                    if (isWindows) {
                        bat 'trivy fs --exit-code 0 --format table .'
                    } else {
                        sh 'trivy fs --exit-code 0 --format table .'
                    }
                }
            }
        }

        stage('Run OWASP ZAP Scan') {
            steps {
                script {
                    def isWindows = isUnix() == false
                    if (isWindows) {
                        bat 'zap.bat -quickurl http://localhost:3000 -quickout zap-report.html'
                    } else {
                        sh 'zap.sh -quickurl http://localhost:3000 -quickout zap-report.html'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/reports/**/*, zap-report.html', allowEmptyArchive: true
        }
    }
}
