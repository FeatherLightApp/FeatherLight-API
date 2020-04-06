FROM python:3.8-slim-buster as base

#----------Compile image-------

FROM base as compile-image

# RUN apk update \
#     && apk add --no-cache build-base gcc

WORKDIR /temp

RUN python -m venv env

RUN echo "/proto" >> env/lib/python3.8/site-packages/addpath.pth

ENV PATH="/temp/env/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /proto

RUN apt-get update && apt-get install -y wget git

RUN wget https://raw.githubusercontent.com/lightningnetwork/lnd/v0.9.2-beta/lnrpc/rpc.proto

RUN git clone https://github.com/googleapis/googleapis.git


RUN mkdir build && ls -a

RUN python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=./build/ --python_grpc_out=./build/ -I. rpc.proto

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

CMD [ "python", "-m", "uvicorn",  "app:APP", "--host", "0.0.0.0", "--port", "5001", "--log-level", "info", "--reload", "--reload-dir", "/app"]
