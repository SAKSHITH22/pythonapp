pipeline {
    agent any

    environment {
        IMAGE = "sakshith123/pythonapp"
        AWS_REGION = "us-east-1"
        CLUSTER_NAME = "sakshith_01-cluster"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/SAKSHITH22/pythonapp.git'
            }
        }

        stage('Set Dynamic Tag') {
            steps {
                script {
                    def timestamp = new Date().format('yyyyMMdd-HHmm')
                    env.TAG = "v${env.BUILD_ID}-${timestamp}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $IMAGE:$TAG ."
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push $IMAGE:$TAG
                    '''
                }
            }
        }

        stage('Update Deployment YAML') {
            steps {
                sh "sed -i 's|image:.*|image: $IMAGE:$TAG|' deployment.yaml"
            }
        }

        stage('Configure AWS & Kubeconfig') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds'
                ]]) {
                    sh '''
                        aws eks update-kubeconfig --name $CLUSTER_NAME --region $AWS_REGION
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds'
                ]]) {
                    sh '''
                        kubectl apply -f deployment.yaml
                        kubectl apply -f service.yaml
                        kubectl rollout status deployment/pythonapp-deployment --timeout=180s
                    '''
                }
            }
        }

        stage('Print Public URL') {
    steps {
        withCredentials([[
            $class: 'AmazonWebServicesCredentialsBinding',
            credentialsId: 'aws-creds'
        ]]) {
            sh '''
                PUBLIC_URL=$(kubectl get svc python-app-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
                echo "Your application is live at: http://$PUBLIC_URL"
            '''
        }
    }
}

    }
}
