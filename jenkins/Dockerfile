FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
    && apt-get install -y curl docker.io \
    && curl -fsSL -o /usr/local/bin/kubectl https://dl.k8s.io/release/v1.30.2/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

USER jenkins
