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
        NAMESPACE = 'production'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/pbernal-opswerks/CaseStudy_Observability.git'
            }
        }
        
        stage('Build Image') {
            steps {
                container('kaniko') {
                    sh """
                        /kaniko/executor \\
                            --dockerfile=Dockerfile \\
                            --context=. \\
                            --destination=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:${IMAGE_TAG} \\
                            --destination=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:latest \\
                            --cache=true \\
                            --cache-repo=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/cache
                    """
                }
            }
        }
        
        stage('Deploy') {
            steps {
                container('kubectl') {
                    sh """
                        if ! kubectl get deployment ${APP_NAME} -n ${NAMESPACE}; then
                          kubectl create deployment ${APP_NAME} \
                            --image=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:${IMAGE_TAG} \
                            -n ${NAMESPACE}
                        else
                          kubectl set image deployment/${APP_NAME} \
                            ${APP_NAME}=${DOCKER_REGISTRY}/${DOCKER_USERNAME}/${APP_NAME}:${IMAGE_TAG} \
                            -n ${NAMESPACE}
                        fi

                        kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE}
                    """
                }
            }
        }
    }
}
