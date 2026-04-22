pipeline {
    agent any

    parameters {
        string(name: 'DOCKER_IMAGE_REPO', defaultValue: 'your-dockerhub-username/generic-app', description: 'Docker repository to push, for example myuser/myapp')
        string(name: 'KUBE_NAMESPACE', defaultValue: 'default', description: 'Kubernetes namespace to deploy into')
    }

    environment {
        REGISTRY = 'docker.io'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        DEPLOYMENT_NAME = 'generic-app'
        CONTAINER_NAME = 'app'
        APP_REPO = "${env.GIT_URL ?: ''}"
    }

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Detect Stack') {
            steps {
                script {
                    if (fileExists('package.json')) {
                        env.APP_STACK = 'node'
                        env.BUILD_CMD = 'npm install'
                        env.TEST_CMD = sh(script: "node -e \"const p=require('./package.json');process.exit(p.scripts && p.scripts.test ? 0 : 1)\"", returnStatus: true) == 0 ? 'npm test' : ''
                        env.DOCKER_BASE = 'node:20-alpine'
                        env.START_CMD = 'npm start'
                    } else if (fileExists('requirements.txt') || fileExists('pyproject.toml')) {
                        env.APP_STACK = 'python'
                        env.BUILD_CMD = ". .jenkins-venv/bin/activate 2>/dev/null || true; python -m venv .jenkins-venv && . .jenkins-venv/bin/activate && python -m pip install --upgrade pip && if [ -f requirements.txt ]; then pip install -r requirements.txt; elif [ -f pyproject.toml ]; then pip install .; fi"
                        env.TEST_CMD = fileExists('pytest.ini') || fileExists('tests') ? '. .jenkins-venv/bin/activate && pytest' : ''
                        env.DOCKER_BASE = 'python:3.11-slim'
                        env.START_CMD = 'gunicorn --bind 0.0.0.0:5000 app:app'
                    } else if (fileExists('Makefile') || fileExists('CMakeLists.txt') || sh(script: "ls *.cpp >/dev/null 2>&1", returnStatus: true) == 0) {
                        env.APP_STACK = 'cpp'
                        env.BUILD_CMD = 'if [ -f Makefile ]; then make; elif [ -f CMakeLists.txt ]; then cmake -S . -B build && cmake --build build; fi'
                        env.TEST_CMD = 'if [ -f Makefile ]; then make test || true; elif [ -d build ]; then ctest --test-dir build --output-on-failure || true; fi'
                        env.DOCKER_BASE = 'ubuntu:22.04'
                        env.START_CMD = './app'
                    } else {
                        error('Unsupported repository type. Add package.json, requirements.txt/pyproject.toml, Makefile, CMakeLists.txt, or a custom Dockerfile.')
                    }

                    echo "Detected stack: ${env.APP_STACK}"
                }
            }
        }

        stage('Build') {
            steps {
                sh "${env.BUILD_CMD}"
            }
        }

        stage('Test') {
            when {
                expression { return env.TEST_CMD?.trim() }
            }
            steps {
                sh "${env.TEST_CMD}"
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    def imageRef = "${env.REGISTRY}/${params.DOCKER_IMAGE_REPO}:${env.IMAGE_TAG}"
                    sh """
                        docker build \
                          --build-arg BASE_IMAGE=${env.DOCKER_BASE} \
                          --build-arg BUILD_COMMAND='${env.BUILD_CMD.replace("'", "'\\''")}' \
                          --build-arg START_COMMAND='${env.START_CMD.replace("'", "'\\''")}' \
                          -t ${imageRef} .
                    """
                    env.BUILT_IMAGE = imageRef
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    withDockerRegistry(credentialsId: 'docker-registry-credentials', url: 'https://index.docker.io/v1/') {
                        sh "docker push ${env.BUILT_IMAGE}"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withKubeConfig(credentialsId: 'kubeconfig') {
                    sh """
                        kubectl apply -f deployment.yaml -n ${params.KUBE_NAMESPACE}
                        kubectl apply -f service.yaml -n ${params.KUBE_NAMESPACE}
                        kubectl apply -f hpa.yaml -n ${params.KUBE_NAMESPACE}
                        kubectl apply -f prometheus.yaml -n ${params.KUBE_NAMESPACE}
                        kubectl apply -f grafana.yaml -n ${params.KUBE_NAMESPACE}
                        kubectl set image deployment/${env.DEPLOYMENT_NAME} ${env.CONTAINER_NAME}=${env.BUILT_IMAGE} -n ${params.KUBE_NAMESPACE}
                        kubectl rollout status deployment/${env.DEPLOYMENT_NAME} -n ${params.KUBE_NAMESPACE} --timeout=120s
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Deployment completed for ${env.BUILT_IMAGE}"
        }
        failure {
            echo 'Pipeline failed. Review the build and deployment logs.'
        }
    }
}
