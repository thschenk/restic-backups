FROM alpine:3.9

RUN apk add --update --no-cache ca-certificates wget fuse openssh-client python3 bzip2 && \
    pip3 install schedule && \
    wget https://github.com/restic/restic/releases/download/v0.9.5/restic_0.9.5_linux_amd64.bz2 && \
    bzip2 -d restic_0.9.5_linux_amd64.bz2 && \
    mv restic_0.9.5_linux_amd64 /usr/bin/restic && \
    chmod 777 /usr/bin/restic


COPY /app /app
WORKDIR /app

ENTRYPOINT ["python3", "/app"]
CMD ["run"]
