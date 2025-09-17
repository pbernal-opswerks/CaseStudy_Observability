pipeline {
  agent any

  environment {
    REGISTRY = "academyopswerks"
    APP_NAME = "shift-scheduler"
    IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT[0..6]}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Push Image') {
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
            sh """
              echo $PASS | docker login -u $USER --password-stdin
              docker build -t $REGISTRY/$APP_NAME:$IMAGE_TAG .
              docker push $REGISTRY/$APP_NAME:$IMAGE_TAG
              docker logout || true
            """
          }
        }
      }
    }
  }
}
