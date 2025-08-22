FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    poppler-utils ghostscript \
    libstdc++6 libgomp1 libgcc-s1 zlib1g \
    bash coreutils procps ca-certificates curl git \
    texlive-full \
    time \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /work
