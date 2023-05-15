FROM debian:10
ENV REPO_NAME=KscNextcloud
ENV GIT_LINK="https://github.com/Devil666face/${REPO_NAME}.git"
RUN apt-get update -y && \
    apt-get install -y \
      gcc make patchelf wget tar git libsqlite3-0
RUN git clone "${GIT_LINK}"
WORKDIR /${REPO_NAME}
RUN .dev/init.sh
RUN ./venv/bin/pip install nuitka
CMD ["/bin/bash", "-c", ".dev/build.sh"]
