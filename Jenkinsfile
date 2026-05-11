pipeline {
    agent any

    environment {
        DOCKERHUB_USER  = 'aphikap'
        IMAGE_NAME      = 'aradin-converter'
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        FULL_IMAGE      = "${DOCKERHUB_USER}/${IMAGE_NAME}"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r app/requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    cd app && pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    docker build -t ${FULL_IMAGE}:${IMAGE_TAG} -t ${FULL_IMAGE}:latest ./app
                """
            }
        }

        stage('Push to Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh """
                        echo \$DH_PASS | docker login -u \$DH_USER --password-stdin
                        docker push ${FULL_IMAGE}:${IMAGE_TAG}
                        docker push ${FULL_IMAGE}:latest
                        docker logout
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    set -e
                    cd terraform
                    terraform init -input=false
                    if ! terraform state list 2>/dev/null | grep -q "kubernetes_namespace.aradin"; then
                        terraform import -input=false kubernetes_namespace.aradin aradin || true
                    fi
                    terraform apply -auto-approve
                '''
                sh """
                    ansible-galaxy collection install community.docker --force >/dev/null
                    pip3 install --break-system-packages --quiet docker requests
                    ansible-playbook -i ansible/inventory ansible/playbook.yml \\
                        --extra-vars "image=${FULL_IMAGE}:${IMAGE_TAG} skip_monitoring=true"
                """
                sh """
                    kubectl apply -f k8s/
                    kubectl set image deployment/aradin-converter aradin-converter=${FULL_IMAGE}:${IMAGE_TAG} -n aradin
                    kubectl rollout status deployment/aradin-converter -n aradin --timeout=120s
                """
            }
        }
    }

    post {
        success { echo "Deployed ${FULL_IMAGE}:${IMAGE_TAG}" }
        failure { echo "Pipeline failed at stage: ${env.STAGE_NAME}" }
        always  { sh 'docker image prune -f || true' }
    }
}
