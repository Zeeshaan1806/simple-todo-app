pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'simple-todo-app'
        TRIVY_REPORT = 'trivy-report.html'
        ZAP_REPORT = 'zap-report.html'
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Wait for SonarQube') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    script {
                        echo "Waiting for SonarQube to become healthy..."
                        retry(5) {
                            sleep 10
                            def health = sh(
                                script: '''
                                    curl -s -u $SONAR_TOKEN: http://localhost:9000/api/system/health | grep -o '"health":"GREEN"'
                                ''',
                                returnStatus: true
                            )
                            if (health != 0) {
                                error("SonarQube is not ready yet.")
                            }
                        }
                    }
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                        sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=simple-todo-app \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=http://localhost:9000 \
                          -Dsonar.login=$SONAR_TOKEN
                        '''
                    }
                }
                waitForQualityGate abortPipeline: true
            }
        }

        stage('SCA - Dependency Check') {
            steps {
                sh '''
                dependency-check.sh --project "simple-todo-app" \
                  --format HTML --out dependency-check-report \
                  --scan .
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE .'
            }
        }

        stage('Container Security Scan - Trivy') {
            steps {
                sh '''
                trivy image --format template --template "@/contrib/html.tpl" \
                  -o $TRIVY_REPORT $DOCKER_IMAGE
                '''
            }
        }

        stage('Run App for Testing') {
            steps {
                sh '''
                docker run -d -p 5000:5000 --name test-container $DOCKER_IMAGE
                sleep 10
                '''
            }
        }

        stage('DAST - OWASP ZAP Scan') {
            steps {
                sh '''
                zap-baseline.py -t http://localhost:5000 -r $ZAP_REPORT || true
                '''
            }
        }
    }

    post {
        always {
            // Clean up the test container
            sh '''
            docker stop test-container || true
            docker rm test-container || true
            '''

            // Publish reports
            publishHTML([
                reportDir: 'dependency-check-report',
                reportFiles: 'dependency-check-report.html',
                reportName: 'OWASP Dependency Check'
            ])
            publishHTML([
                reportDir: '.',
                reportFiles: "$TRIVY_REPORT",
                reportName: 'Trivy Scan'
            ])
            publishHTML([
                reportDir: '.',
                reportFiles: "$ZAP_REPORT",
                reportName: 'ZAP Baseline Scan'
            ])
        }
    }
}
