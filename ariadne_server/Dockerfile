FROM python:3.8 as base

#----------Compile image-------

FROM base as compile-image

RUN apt-get update -y \
    && apt-get install -y build-essential libssl-dev automake pkg-config libtool libffi-dev libsecp256k1-dev

WORKDIR /temp

RUN python -m venv env

ENV PATH="/temp/env/bin:$PATH"

COPY requirements.txt .

RUN pip install -U pip setuptools wheel \
    && pip install secp256k1 \
    && pip install -r requirements.txt


#------build image --------

FROM base as build-image

# RUN apk add --no-cache libstdc++

WORKDIR /app

COPY --from=compile-image /temp/env /env

ENV PATH="/env/bin:$PATH"

COPY rpc.proto .

COPY googleapis ./googleapis

RUN ls -a /app

RUN python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto

EXPOSE 5000

COPY keys.json .

RUN echo "from src.app import APP" >> main.py && touch __init__.py

CMD [ "python", "-m", "uvicorn",  "main:APP", "--host", "0.0.0.0", "--port", "5001", "--log-level", "info", "--reload", "--reload-dir", "/app"]
