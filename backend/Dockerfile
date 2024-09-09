FROM python:3.10.2 AS builder

WORKDIR /app

RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends \
    build-essential \
    git \
    cmake \
    make

EOF

COPY Pipfile ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install pipenv 
RUN pipenv install

COPY ./app ./app


FROM builder AS dev-envs


RUN <<EOF
useradd -s /bin/bash -m vscode
groupadd docker
usermod -aG docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /

CMD ["pipenv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
