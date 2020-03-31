FROM python:3.8 as base

#----------Compile image-------

FROM base as compile-image

RUN apt-get update -y \
    && apt-get install -y build-essential libssl-dev automake pkg-config libtool libffi-dev libsecp256k1-dev

WORKDIR /temp

RUN python -m venv env

RUN echo "/proto" >> env/lib/python3.8/site-packages/addpath.pth

ENV PATH="/temp/env/bin:$PATH"

COPY requirements.txt .

RUN pip install -U pip setuptools wheel\
    && pip install -r requirements.txt

WORKDIR /proto

RUN wget https://raw.githubusercontent.com/lightningnetwork/lnd/v0.9.2-beta/lnrpc/rpc.proto

RUN git clone https://github.com/googleapis/googleapis.git

RUN python -m grpc_tools.protoc --python_out=./build --purerpc_out=./build/. -I. rpc.proto

RUN touch build/__init__.py

RUN ls -a /proto/build

#------build image --------

FROM base as build-image

# RUN apk add --no-cache libstdc++

WORKDIR /app

COPY --from=compile-image /temp/env /env

COPY --from=compile-image /proto/build /proto

ENV PATH="/env/bin:$PATH"


RUN ls -a /app

RUN ls -a /proto

EXPOSE 5000

COPY keys.json .

CMD [ "python", "-m", "uvicorn",  "app:APP", "--host", "0.0.0.0", "--port", "5001", "--log-level", "info", "--reload", "--reload-dir", "/app"]
