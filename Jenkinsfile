pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["9999999"]
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker
      readOnly: true
  volumes:
  - name: docker-config
    secret:
      secretName: docker-registry-config-peng
      items:
      - key: .dockerconfigjson
        path: config.json
            """
        }
    }

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_USERNAME = 'bernalp'
        APP_NAME = 'my-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Image') {
            steps {
                container('kaniko') {
                    sh """
                        /kaniko/executor \
                        --dockerfile=Dockerfile \
                        --context=. \
                        --destination=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:${BUILD_NUMBER} \
                        --destination=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:latest
                    """
                }
            }
        }
    }
}
