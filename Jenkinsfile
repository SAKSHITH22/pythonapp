pipeline {
    agent any

    environment {
        IMAGE_NAME = "pythonapp"
        AWS_REGION = "us-east-1"
        CLUSTER_NAME = "sakshith_01-cluster"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/SAKSHITH22/pythonapp.git'
            }
        }

        stage('Set Image Tag') {
            steps {
                script {
                    def timestamp = new Date().format('yyyyMMdd-HHmm')
                    env.TAG = "v${env.BUILD_ID}-${timestamp}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $IMAGE_NAME:$TAG ."
            }
        }

        stage('Ensure ECR Repo & Get URI') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                        export AWS_DEFAULT_REGION=$AWS_REGION

                        # Create ECR repo if it does not exist
                        aws ecr describe-repositories --repository-names $IMAGE_NAME || \
                        aws ecr create-repository --repository-name $IMAGE_NAME

                        # Get ECR URI
                        ECR_URI=$(aws ecr describe-repositories --repository-names $IMAGE_NAME --query "repositories[0].repositoryUri" --output text)
                        echo "ECR_URI=$ECR_URI" > ecr_env.sh
                    '''
                    sh 'source ecr_env.sh'
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                        source ecr_env.sh
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                        export AWS_DEFAULT_REGION=$AWS_REGION

                        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI
                        docker tag $IMAGE_NAME:$TAG $ECR_URI:$TAG
                        docker push $ECR_URI:$TAG
                    '''
                }
            }
        }

        stage('Update deployment.yaml') {
            steps {
                sh '''
                    source ecr_env.sh
                    sed -i "s|image:.*|image: $ECR_URI:$TAG|" deployment.yaml
                '''
            }
        }

        stage('Configure kubeconfig') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                        export AWS_DEFAULT_REGION=$AWS_REGION

                        aws eks update-kubeconfig --name $CLUSTER_NAME --region $AWS_REGION
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl apply -f deployment.yaml
                    kubectl apply -f service.yaml
                    kubectl rollout status deployment/pythonapp-deployment --timeout=180s
                '''
            }
        }

        stage('Print Public URL') {
            steps {
                sh '''
                    PUBLIC_URL=$(kubectl get svc python-app-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
                    echo "Your application is live at: http://$PUBLIC_URL"
                '''
            }
        }
    }
}
