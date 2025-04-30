pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'simple-todo-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        APP_PORT = '8080'
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
    withSonarQubeEnv('SonarQube') {
      withCredentials([string(credentialsId: 'sqa_7df16d680b5187bcd44e8b324327aca0dbe3d24b', variable: 'SONAR_TOKEN')]) {
        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
          sh '''
          sonar-scanner \
            -Dsonar.projectKey=simple-todo-app \
            -Dsonar.sources=. \
            -Dsonar.host.url=http://localhost:9000 \
            -Dsonar.login=$SONAR_TOKEN
          '''
        }
      }
    }
    waitForQualityGate abortPipeline: true
  }
}
        
        stage('SCA - Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '--scan ./ --format HTML --out dependency-check-report.html', odcInstallation: 'OWASP-Dependency-Check'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: './',
                    reportFiles: 'dependency-check-report.html',
                    reportName: 'Dependency Check Report'
                ])
                echo 'Dependency check complete'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                echo 'Docker image built'
            }
        }
        
        stage('Container Security Scan') {
            steps {
                sh """
                docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                  aquasec/trivy image \
                  --format template \
                  --template '@/contrib/html.tpl' \
                  --output trivy-report.html \
                  ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: './',
                    reportFiles: 'trivy-report.html',
                    reportName: 'Trivy Security Report'
                ])
                echo 'Container security scan complete'
            }
        }
        
        stage('Deploy for Testing') {
            steps {
                sh "docker stop ${DOCKER_IMAGE} || true"
                sh "docker rm ${DOCKER_IMAGE} || true"
                sh "docker run -d --name ${DOCKER_IMAGE} -p ${APP_PORT}:8080 ${DOCKER_IMAGE}:${DOCKER_TAG}"
                echo 'Application deployed for testing'
            }
        }
        
        stage('DAST - OWASP ZAP Scan') {
            steps {
                sh """
                docker run --rm -v \$(pwd):/zap/wrk/:rw owasp/zap2docker-stable zap-baseline.py \
                  -t http://host.docker.internal:${APP_PORT} \
                  -r zap-report.html
                """
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: './',
                    reportFiles: 'zap-report.html',
                    reportName: 'ZAP Security Report'
                ])
                echo 'DAST scan complete'
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution complete'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}