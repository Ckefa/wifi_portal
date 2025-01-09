pipeline {
    agent any

    stages {
        stage('Start') {
            steps {
                echo 'Starting pipeline'
            }
        }
        stage('Build') {
            steps {
                echo 'Building docker image'
                sh 'docker build -t captive_portal_image .'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying The app'
                sh 'docker-compose up -d'
            }
        }
    }
}
