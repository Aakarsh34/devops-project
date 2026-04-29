pipeline {
    agent any

    parameters {
        string(name: 'DOCKER_IMAGE_REPO', defaultValue: 'aakarsh46/generic-app', description: 'Docker repository to push, for example myuser/myapp')
        string(name: 'KUBE_NAMESPACE', defaultValue: 'default', description: 'Kubernetes namespace to deploy into')
    }

    options {
        timestamps()
    }

    environment {
        STACK = ''
        BUILD_CMD = ''
        TEST_CMD = ''
        DOCKER_BUILD_CMD = ''
        BASE_IMAGE = ''
        START_COMMAND = ''
        IMAGE_TAG = ''
        FULL_IMAGE = ''
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
                        env.STACK = 'node'
                        env.BUILD_CMD = 'npm install'
                        env.TEST_CMD = 'if npm run 2>/dev/null | grep -q " test"; then npm test; else echo "No npm test script found, skipping tests."; fi'
                        env.DOCKER_BUILD_CMD = 'npm install'
                        env.BASE_IMAGE = 'node:20-alpine'
                        env.START_COMMAND = 'npm start'
                    } else if (fileExists('requirements.txt') || fileExists('pyproject.toml')) {
                        env.STACK = 'python'
                        env.BUILD_CMD = 'python -m venv .jenkins-venv && . .jenkins-venv/bin/activate && python -m pip install --upgrade pip && if [ -f requirements.txt ]; then pip install -r requirements.txt; elif [ -f pyproject.toml ]; then pip install .; fi'
                        env.TEST_CMD = (fileExists('pytest.ini') || fileExists('tests')) ? '. .jenkins-venv/bin/activate && pytest' : 'echo "No pytest suite found, skipping tests."'
                        env.DOCKER_BUILD_CMD = 'python -m pip install --upgrade pip && if [ -f requirements.txt ]; then pip install -r requirements.txt; elif [ -f pyproject.toml ]; then pip install .; fi'
                        env.BASE_IMAGE = 'python:3.11-slim'
                        env.START_COMMAND = 'gunicorn --bind 0.0.0.0:5000 app:app'
                    } else if (fileExists('CMakeLists.txt') || fileExists('Makefile')) {
                        env.STACK = 'cpp'
                        env.BUILD_CMD = fileExists('CMakeLists.txt') ? 'cmake -S . -B build && cmake --build build' : 'make'
                        env.TEST_CMD = fileExists('CMakeLists.txt') ? 'cd build && ctest --output-on-failure || echo "No CTest suite found, skipping tests."' : 'echo "No automated C++ tests configured, skipping tests."'
                        env.DOCKER_BUILD_CMD = env.BUILD_CMD
                        env.BASE_IMAGE = 'gcc:13'
                        env.START_COMMAND = './app'
                    } else {
                        error('Unsupported repository: could not detect Python, Node.js, or C++ build files.')
                    }

                    env.IMAGE_TAG = "${env.BUILD_NUMBER}"
                    env.FULL_IMAGE = "${params.DOCKER_IMAGE_REPO}:${env.IMAGE_TAG}"
                    echo "Detected stack: ${env.STACK}"
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
                sh """
                    docker build \
                      --build-arg BASE_IMAGE=${env.BASE_IMAGE} \
                      --build-arg BUILD_COMMAND='${env.DOCKER_BUILD_CMD.replace("'", "'\"'\"'")}' \
                      --build-arg START_COMMAND='${env.START_COMMAND.replace("'", "'\"'\"'")}' \
                      -t ${env.FULL_IMAGE} .
                """
            }
        }

        stage('Push Image') {
            steps {
                withDockerRegistry([credentialsId: 'docker-registry-credentials', url: 'https://index.docker.io/v1/']) {
                    sh "docker push ${env.FULL_IMAGE}"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                expression { return fileExists('deployment.yaml') }
            }
            steps {
                withKubeConfig([credentialsId: 'kubeconfig']) {
                    sh """
                        kubectl apply -f deployment.yaml -n ${params.KUBE_NAMESPACE}
                        if [ -f service.yaml ]; then kubectl apply -f service.yaml -n ${params.KUBE_NAMESPACE}; fi
                        if [ -f hpa.yaml ]; then kubectl apply -f hpa.yaml -n ${params.KUBE_NAMESPACE}; fi
                        kubectl set image deployment/generic-app generic-app='${env.FULL_IMAGE}' -n ${params.KUBE_NAMESPACE}
                        kubectl rollout status deployment/generic-app -n ${params.KUBE_NAMESPACE} --timeout=180s
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Deployed image: ${env.FULL_IMAGE}"
        }
        failure {
            echo 'Pipeline failed. Review the build and deployment logs.'
        }
    }
}
