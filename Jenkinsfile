pipeline {
    agent any

    environment {
        SONAR_URL = 'http://localhost:9000'
    }

    tools {
        nodejs 'NodeJS 20'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Wait for SonarQube') {
            environment {
                SONAR_TOKEN = credentials('sonar-token')
            }
            steps {
                script {
                    retry(10) {
                        echo "Waiting for SonarQube to become healthy..."
                        if (isUnix()) {
                            sh """
                                curl -u ${env.SONAR_TOKEN}: -f ${env.SONAR_URL}/api/system/health || exit 1
                            """
                        } else {
                            bat """
                                curl -u %SONAR_TOKEN%: -f %SONAR_URL%/api/system/health || exit 1
                            """
                        }
                        sleep 10
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'npm test || true'
            }
        }

        stage('SonarQube Analysis') {
            environment {
                SONAR_TOKEN = credentials('sonar-token')
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh """
                        npx sonar-scanner \
                        -Dsonar.projectKey=simple-todo-app \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=${SONAR_URL} \
                        -Dsonar.login=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Dependency Check') {
            steps {
                sh 'dependency-check.sh --project "simple-todo-app" --scan . || true'
            }
        }

        stage('Trivy Scan') {
            steps {
                sh 'trivy fs --exit-code 0 --severity HIGH,CRITICAL . || true'
            }
        }

        stage('OWASP ZAP Scan') {
            steps {
                sh 'zap-cli start && zap-cli quick-scan --self-contained --start-options "-config api.disablekey=true" http://localhost:3000 || true'
            }
        }
    }
}
