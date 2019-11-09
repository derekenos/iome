FROM docker:19.03.3

RUN apk update && \
    apk upgrade && \
    apk add \
    git \
    make \
    openssh \
    docker-compose

WORKDIR /app
RUN git clone https://github.com/derekenos/iome.git .
WORKDIR dev_kits/v1

ENTRYPOINT ["make"]
