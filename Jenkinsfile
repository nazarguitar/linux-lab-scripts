pipeline {
    agent any

    environment {
        RPM_IMAGE   = 'fedora:latest'
        DEB_IMAGE   = 'debian:stable-slim'

        APP_NAME    = 'count-files'
        RPM_VERSION = '2.0'
        DEB_VERSION = '1.0'
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
                    docker.image(env.RPM_IMAGE).inside('-u 0:0') {
                        sh '''
                            set -e

                            echo "=== [RPM] Встановлюємо інструменти ==="
                            dnf install -y rpm-build rpmdevtools

                            echo "=== [RPM] Налаштовуємо rpmbuild tree ==="
                            rpmdev-setuptree

                            SRC_ROOT=/root/rpmbuild/SOURCES
                            SPEC_ROOT=/root/rpmbuild/SPECS

                            cd "$SRC_ROOT"

                            echo "=== [RPM] Готуємо вихідні каталоги ==="
                            rm -rf "${APP_NAME}-1.0" "${APP_NAME}-${RPM_VERSION}"
                            mkdir -p "${APP_NAME}-1.0" "${APP_NAME}-${RPM_VERSION}"

                            # Скрипт
                            cp "$WORKSPACE/count_files.sh" "${APP_NAME}-1.0/"
                            cp "$WORKSPACE/count_files.sh" "${APP_NAME}-${RPM_VERSION}/"

                            # Конфіг тільки для 2.0
                            cp "$WORKSPACE/count_files.conf" "${APP_NAME}-${RPM_VERSION}/"

                            # Файли, які spec бере напряму із SOURCES
                            cp "$WORKSPACE/count_files.conf" "$SRC_ROOT/"
                            cp "$WORKSPACE/packaging/rpm/count_files.1" "$SRC_ROOT/"

                            echo "=== [RPM] Створюємо tar.gz для 1.0 та ${RPM_VERSION} ==="
                            tar czvf "${APP_NAME}-1.0.tar.gz" "${APP_NAME}-1.0"
                            tar czvf "${APP_NAME}-${RPM_VERSION}.tar.gz" "${APP_NAME}-${RPM_VERSION}"

                            echo "=== [RPM] Копіюємо spec-файл ==="
                            cp "$WORKSPACE/packaging/rpm/${APP_NAME}.spec" "$SPEC_ROOT/"

                            echo "=== [RPM] Запускаємо rpmbuild ==="
                            rpmbuild -ba "$SPEC_ROOT/${APP_NAME}.spec"

                            echo "=== [RPM] Копіюємо RPM у build_artifacts ==="
                            mkdir -p "$WORKSPACE/build_artifacts/rpm"
                            cp /root/rpmbuild/RPMS/noarch/*.rpm "$WORKSPACE/build_artifacts/rpm/" || true
                            cp /root/rpmbuild/SRPMS/*.src.rpm "$WORKSPACE/build_artifacts/rpm/" || true
                        '''
                    }
                }
            }
        }

        stage('Build DEB') {
            steps {
                script {
                    docker.image(env.DEB_IMAGE).inside('-u 0:0') {
                        sh '''
                            set -e

                            echo "=== [DEB] Встановлюємо інструменти для збірки ==="
                            apt-get update
                            apt-get install -y build-essential devscripts debhelper fakeroot

                            echo "=== [DEB] Готуємо вихідні файли для orig.tar.gz ==="
                            cd "$WORKSPACE"

                            TMP_SRC="/tmp/${APP_NAME}-${DEB_VERSION}"
                            rm -rf "$TMP_SRC"
                            mkdir -p "$TMP_SRC"

                            # Скрипт і конфіг
                            cp count_files.sh "$TMP_SRC/"
                            cp count_files.conf "$TMP_SRC/"

                            # Метадані пакету Debian
                            rm -rf "$TMP_SRC/debian"
                            cp -r packaging/deb/debian "$TMP_SRC/debian"

                            echo "=== [DEB] Створюємо ${APP_NAME}_${DEB_VERSION}.orig.tar.gz ==="
                            cd /tmp
                            tar czvf "$WORKSPACE/packaging/${APP_NAME}_${DEB_VERSION}.orig.tar.gz" "${APP_NAME}-${DEB_VERSION}"

                            echo "=== [DEB] Переходимо в каталог deb-пакету ==="
                            cd "$WORKSPACE/packaging/deb"

                            echo "=== [DEB] Збірка пакету debuild ==="
                            debuild -us -uc

                            echo "=== [DEB] Копіюємо зібрані DEB-файли в артефакти ==="
                            cd "$WORKSPACE"
                            mkdir -p build_artifacts/deb
                            cp ../${APP_NAME}_${DEB_VERSION}-*.deb      build_artifacts/deb/ 2>/dev/null || true
                            cp ../${APP_NAME}_${DEB_VERSION}-*.changes build_artifacts/deb/ 2>/dev/null || true
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
                            echo "=== [TEST RPM] Встановлюємо RPM і перевіряємо виконання ==="
                            cd "$WORKSPACE/build_artifacts/rpm"

                            dnf install -y ${APP_NAME}-${RPM_VERSION}-*.rpm

                            echo "=== [TEST RPM] Запускаємо count_files ==="
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
                            echo "=== [TEST DEB] Встановлюємо DEB і перевіряємо виконання ==="
                            apt-get update
                            cd "$WORKSPACE/build_artifacts/deb"

                            apt-get install -y ./${APP_NAME}_${DEB_VERSION}-*.deb

                            echo "=== [TEST DEB] Запускаємо count_files ==="
                            count_files --help || count_files -h || true
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'build_artifacts/**/*', fingerprint: true, allowEmptyArchive: true
        }
    }
}
