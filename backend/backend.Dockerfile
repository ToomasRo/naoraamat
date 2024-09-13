FROM python:3.10.2 AS builder

WORKDIR /app

RUN <<EOF
apt update
apt install -y --no-install-recommends \
    build-essential \
    git \
    cmake \
    make \
    ffmpeg \
    libsm6 \
    libxext6
EOF


# COPY /usr/share/config/certs /usr/share/ca-certificates
# COPY /usr/share/config/certs/elastic/elastic.crt /usr/share/ca-certificates/elastic.crt
# RUN update-ca-certificates

CMD [ "echo", "pwd" ]
COPY requirements.txt ./

RUN useradd -ms /bin/sh -u 1001 app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# COPY ./app ./app
COPY --chown=app:app ./app ./app
COPY --chown=app:app ./utils ./utils
FROM builder AS dev-envs


# RUN <<EOF
# useradd -s /bin/bash app
# groupadd docker
# usermod -aG docker vscode
# EOF
# # install Docker tools (cli, buildx, compose)
# COPY --from=gloursdocker/docker / /

# USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-cli -y
    