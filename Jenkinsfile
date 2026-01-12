pipeline {
    agent any

    environment {
        PACKAGE_NAME = 'count-files'
        PACKAGE_VERSION = '1.0'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'ls -la'
            }
        }

        stage('Test Script') {
            steps {
                sh 'chmod +x count_files.sh'
                sh 'bash -n count_files.sh'
                sh './count_files.sh'
            }
        }

        stage('Build RPM') {
            agent {
                docker {
                    image 'fedora:latest'
                    args '-u root'
                }
            }
            steps {
                sh '''
          dnf install -y rpm-build rpmdevtools

          rpmdev-setuptree

          # Директорії для двох версій
          mkdir -p /root/rpmbuild/SOURCES/count-files-1.0
          mkdir -p /root/rpmbuild/SOURCES/count-files-2.0

          cp count_files.sh /root/rpmbuild/SOURCES/count-files-1.0/

          cp count_files.sh /root/rpmbuild/SOURCES/count-files-2.0/
          cp count_files.conf /root/rpmbuild/SOURCES/count-files-2.0/
          cp packaging/rpm/count_files.1 /root/rpmbuild/SOURCES/count-files-2.0/

          # 4. Зібрати архіви, як вимагає spec-файл
          cd /root/rpmbuild/SOURCES
          tar czf count-files-1.0.tar.gz count-files-1.0
          tar czf count-files-2.0.tar.gz count-files-2.0

          cd "$WORKSPACE"
          cp packaging/rpm/count-files.spec /root/rpmbuild/SPECS/

          rpmbuild -ba /root/rpmbuild/SPECS/count-files.spec

          mkdir -p "$WORKSPACE/artifacts/rpm"
          cp /root/rpmbuild/RPMS/*/*.rpm "$WORKSPACE/artifacts/rpm/" || true
          cp /root/rpmbuild/SRPMS/*.src.rpm "$WORKSPACE/artifacts/rpm/" || true
        '''
            }
        }

        stage('Build DEB') {
            agent {
                docker {
                    image 'ubuntu:latest'
                    args '-u root'
                }
            }
            steps {
                sh '''
                    apt-get update
                    apt-get install -y build-essential debhelper devscripts
                    mkdir -p build/${PACKAGE_NAME}-${PACKAGE_VERSION}
                    cp count_files.sh build/${PACKAGE_NAME}-${PACKAGE_VERSION}/
                    cp -r packaging/deb/debian build/${PACKAGE_NAME}-${PACKAGE_VERSION}/
                    cd build/${PACKAGE_NAME}-${PACKAGE_VERSION}
                    dpkg-buildpackage -us -uc -b
                    cp ../*.deb ${WORKSPACE}/
                '''
            }
        }

        stage('Test RPM Installation') {
            agent {
                docker {
                    image 'oraclelinux:8'
                    args '-u root'
                }
            }
            steps {
                sh '''
                    rpm -ivh ${PACKAGE_NAME}-*.rpm
                    count_files
                    rpm -e ${PACKAGE_NAME}
                '''
            }
        }

        stage('Test DEB Installation') {
            agent {
                docker {
                    image 'ubuntu:latest'
                    args '-u root'
                }
            }
            steps {
                sh '''
                    dpkg -i ${PACKAGE_NAME}_*.deb || apt-get install -f -y
                    count_files
                    apt-get remove -y ${PACKAGE_NAME}
                '''
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: '*.rpm, *.deb'
            echo 'Build completed successfully!'
        }
        failure {
            echo 'Build failed!'
        }
        always {
            cleanWs()
        }
    }
}
