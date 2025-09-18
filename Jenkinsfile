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
                - name: kubectl
                  image: alpine/k8s:1.28.13
                  command: ["sleep"]
                  args: ["9999999"]
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
        NAMESPACE = 'my-app-namespace'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                container('kaniko') {
                    sh """
                        /kaniko/executor \
                          --dockerfile=Dockerfile \
                          --context=. \
                          --destination=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:${IMAGE_TAG} \
                          --destination=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:latest \
                          --cache=true \
                          --cache-repo=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/cache
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh """
                        # Ensure namespace exists
                        kubectl apply -f k8s/namespace.yaml

                        # Inject built image with tag into deployment before applying
                        sed "s|bernal/my-app:latest|${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:${IMAGE_TAG}|g" k8s/deployment.yaml > k8s/deployment-temp.yaml

                        # Apply manifests
                        kubectl -n ${NAMESPACE} apply -f k8s/deployment-temp.yaml
                        kubectl -n ${NAMESPACE} apply -f k8s/service.yaml
                        kubectl -n ${NAMESPACE} apply -f k8s/servicemonitor.yaml

                        # Wait for rollout to finish
                        kubectl rollout status deployment/my-webapp -n ${NAMESPACE}
                    """
                }
            }
        }
    }
}
