pipeline {
    agent any

    environment {
        APP_NAME   = "canary-app"
        BUILD_VER  = "2.0.${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Starting Canary deployment version ${BUILD_VER}"
            }
        }

        stage('Build Canary image') {
            steps {
                echo "Building canary image..."
                sh "docker build -t ${APP_NAME}:canary ."
                sh "docker tag ${APP_NAME}:canary ${APP_NAME}:${BUILD_VER}"
                echo "Canary image built!"
            }
        }

        stage('Deploy Canary at 10%') {
            steps {
                echo "Deploying canary at 10% traffic..."
                sh "docker stop canary || true"
                sh "docker rm canary || true"
                sh """
                    docker run -d \
                        --name canary \
                        --network canary-demo_network \
                        -e APP_VERSION=${BUILD_VER} \
                        -e APP_VARIANT=canary \
                        -p 5002:5000 \
                        ${APP_NAME}:canary
                """
                sh "sleep 3"
                sh '''
                    docker exec nginx-canary sh -c "cat > /etc/nginx/conf.d/default.conf << NGINX
upstream active {
    server stable:5000 weight=9;
    server canary:5000 weight=1;
}
server {
    listen 80;
    location / {
        proxy_pass http://active;
    }
}
NGINX"
                '''
                sh "docker exec nginx-canary nginx -s reload"
                echo "Canary deployed at 10% traffic!"
            }
        }

        stage('Health check at 10%') {
            steps {
                echo "Health checking canary at 10%..."
                sh "sleep 3"
                sh """
                    docker exec canary python3 -c "
import urllib.request, json
res = urllib.request.urlopen('http://localhost:5000/health')
data = json.loads(res.read())
print('Canary health:', data)
assert data['status'] == 'healthy'
assert data['variant'] == 'canary'
print('Health check at 10% PASSED!')
"
                """
                echo "Canary is healthy at 10%!"
            }
        }

        stage('Promote Canary to 50%') {
            steps {
                echo "Promoting canary to 50% traffic..."
                sh '''
                    docker exec nginx-canary sh -c "cat > /etc/nginx/conf.d/default.conf << NGINX
upstream active {
    server stable:5000 weight=5;
    server canary:5000 weight=5;
}
server {
    listen 80;
    location / {
        proxy_pass http://active;
    }
}
NGINX"
                '''
                sh "docker exec nginx-canary nginx -s reload"
                echo "Canary promoted to 50% traffic!"
            }
        }

        stage('Health check at 50%') {
            steps {
                echo "Health checking canary at 50%..."
                sh "sleep 3"
                sh """
                    docker exec canary python3 -c "
import urllib.request, json
res = urllib.request.urlopen('http://localhost:5000/health')
data = json.loads(res.read())
print('Canary health:', data)
assert data['status'] == 'healthy'
print('Health check at 50% PASSED!')
"
                """
                echo "Canary is healthy at 50%!"
            }
        }

        stage('Promote Canary to 100%') {
            steps {
                echo "Promoting canary to 100% traffic..."
                sh '''
                    docker exec nginx-canary sh -c "cat > /etc/nginx/conf.d/default.conf << NGINX
upstream active {
    server canary:5000 weight=1;
}
server {
    listen 80;
    location / {
        proxy_pass http://active;
    }
}
NGINX"
                '''
                sh "docker exec nginx-canary nginx -s reload"
                echo "Canary is now serving 100% traffic!"
            }
        }

        stage('Decommission Stable') {
            steps {
                echo "Decommissioning stable..."
                sh "docker stop stable || true"
                sh "docker rm stable || true"
                sh "docker tag ${APP_NAME}:canary ${APP_NAME}:stable"
                sh """
                    docker run -d \
                        --name stable \
                        --network canary-demo_network \
                        -e APP_VERSION=${BUILD_VER} \
                        -e APP_VARIANT=stable \
                        -p 5001:5000 \
                        ${APP_NAME}:stable
                """
                echo "Canary promoted to stable. Ready for next deployment!"
            }
        }
    }

    post {
        success {
            echo "Canary deployment SUCCESS! Version ${BUILD_VER} is fully live."
        }
        failure {
            echo "Canary deployment FAILED — rolling back to stable!"
            sh "docker stop canary || true"
            sh "docker rm canary || true"
            sh '''
                docker exec nginx-canary sh -c "cat > /etc/nginx/conf.d/default.conf << NGINX
upstream active {
    server stable:5000 weight=1;
}
server {
    listen 80;
    location / {
        proxy_pass http://active;
    }
}
NGINX" || true
            '''
            sh "docker exec nginx-canary nginx -s reload || true"
            echo "Rolled back! Stable is serving 100% traffic."
        }
        always {
            echo "Pipeline complete."
        }
    }
}
