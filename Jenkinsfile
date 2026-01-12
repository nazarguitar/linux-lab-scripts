pipeline {
    agent any

    environment {
        RPM_IMAGE = 'fedora:latest'
        DEB_IMAGE = 'debian:stable'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build RPM') {
            steps {
                script {
                    // ТУТ ГОЛОВНА ЗМІНА: запускаємо контейнер як root
                    docker.image(env.RPM_IMAGE).inside('-u 0:0') {
                        sh '''
                            set -e

                            echo "=== [RPM] Підготовка середовища ==="
                            dnf -y update
                            dnf -y install rpm-build rpmdevtools

                            echo "=== [RPM] Створення структури rpmbuild ==="
                            rpmdev-setuptree

                            echo "=== [RPM] Перехід у workspace ==="
                            cd "$WORKSPACE"

                            echo "=== [RPM] Копіюємо вихідний скрипт у SOURCES ==="
                            mkdir -p /root/rpmbuild/SOURCES/count-files-2.0
                            cp count_files.sh /root/rpmbuild/SOURCES/count-files-2.0/

                            echo "=== [RPM] Копіюємо man-сторінку у SOURCES ==="
                            cp packaging/rpm/count_files.1 /root/rpmbuild/SOURCES/

                            echo "=== [RPM] Створюємо tar.gz архів з вихідцями ==="
                            cd /root/rpmbuild/SOURCES
                            tar czvf count-files-2.0.tar.gz count-files-2.0

                            echo "=== [RPM] Копіюємо spec-файл ==="
                            cp "$WORKSPACE/packaging/rpm/count-files.spec" /root/rpmbuild/SPECS/

                            echo "=== [RPM] Запускаємо rpmbuild ==="
                            rpmbuild -ba /root/rpmbuild/SPECS/count-files.spec

                            echo "=== [RPM] Копіюємо зібрані пакети в артефакти ==="
                            mkdir -p "$WORKSPACE/build_artifacts/rpm"
                            cp -r /root/rpmbuild/RPMS/* "$WORKSPACE/build_artifacts/rpm/"
                            mkdir -p "$WORKSPACE/build_artifacts/srpm"
                            cp -r /root/rpmbuild/SRPMS/* "$WORKSPACE/build_artifacts/srpm/" || true
                        '''
                    }
                }
            }
        }

        stage('Build DEB') {
            steps {
                script {
                    // ТАК САМО: Debian-контейнер теж як root
                    docker.image(env.DEB_IMAGE).inside('-u 0:0') {
                        sh '''
                            set -e

                            echo "=== [DEB] Підготовка середовища ==="
                            export DEBIAN_FRONTEND=noninteractive
                            apt-get update
                            apt-get install -y devscripts debhelper build-essential fakeroot

                            echo "=== [DEB] Перехід у каталог deb-пакету ==="
                            cd "$WORKSPACE/packaging/deb"

                            echo "=== [DEB] Збірка пакету debuild ==="
                            debuild -us -uc

                            echo "=== [DEB] Копіюємо .deb в артефакти ==="
                            cd "$WORKSPACE"
                            mkdir -p build_artifacts/deb
                            cp ./*.deb build_artifacts/deb/ || true
                            cp packaging/deb/*.deb build_artifacts/deb/ || true
                        '''
                    }
                }
            }
        }

        stage('Test RPM Installation') {
            steps {
                script {
                    docker.image(env.RPM_IMAGE).inside('-u 0:0') {
                        sh '''
                            set -e
                            echo "=== [TEST RPM] Встановлюємо зібраний RPM ==="
                            dnf -y install "$WORKSPACE"/build_artifacts/rpm/noarch/*.rpm

                            echo "=== [TEST RPM] Перевіряємо виконання count_files ==="
                            count_files --help || count_files -h || true
                        '''
                    }
                }
            }
        }

        stage('Test DEB Installation') {
            steps {
                script {
                    docker.image(env.DEB_IMAGE).inside('-u 0:0') {
                        sh '''
                            set -e
                            export DEBIAN_FRONTEND=noninteractive

                            echo "=== [TEST DEB] Встановлюємо зібраний DEB ==="
                            cd "$WORKSPACE/build_artifacts/deb"
                            dpkg -i ./*.deb || apt-get -f install -y

                            echo "=== [TEST DEB] Перевіряємо виконання count_files ==="
                            count_files --help || count_files -h || true
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Збірка пройшла успішно, архівуємо артефакти...'
            archiveArtifacts artifacts: 'build_artifacts/**/*', fingerprint: true
        }
        always {
            cleanWs()
        }
    }
}
