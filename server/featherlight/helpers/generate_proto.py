"""generate proto files"""
import os
import pkg_resources
from tempfile import TemporaryDirectory
import importlib
import wget
from dulwich import porcelain
from grpc_tools import protoc

# RUN python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=./build/ --python_grpc_out=./build/ -I. rpc.proto

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath("main.py")), 'featherlight')
print(ROOT_DIR)


def protos_exist():
    return os.path.exists(os.path.join(ROOT_DIR, 'rpc_pb2.py'))


def compile_protos():
    if protos_exist():
        return None
    with TemporaryDirectory() as temp:
        print("cloning googleapis")
        porcelain.clone(
            "https://github.com/googleapis/googleapis.git",
            target=os.path.join(temp, "googleapis"),
            depth=1,
        )
        print("downloading lnd rpc.proto")
        wget.download(
            "https://raw.githubusercontent.com/lightningnetwork/lnd/v0.10.0-beta/lnrpc/rpc.proto",
            temp,
        )

        os.chdir(temp)

        proto_include = pkg_resources.resource_filename("grpc_tools", "_proto")
        print("compiling proto")
        protoc.main(
            [
                "grpc_tools.protoc",
                "-I{}".format(proto_include),
                "--proto_path=googleapis:.",
                f"--python_out={ROOT_DIR}",
                f"--grpc_python_out={ROOT_DIR}",
                "rpc.proto",
            ]
        )
        print("done")
