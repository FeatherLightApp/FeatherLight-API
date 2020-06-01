"""generate proto files"""
import os
import sys
from pathlib import Path
import pkg_resources
from tempfile import TemporaryDirectory
import importlib 
import wget
from dulwich import porcelain
from grpc_tools import protoc

# RUN python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=./build/ --python_grpc_out=./build/ -I. rpc.proto

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath('app.py')), 'featherlight')

def protos_exist():
    return importlib.util.find_spec("featherlight.proto") is not None



def compile_protos():
    if protos_exist():
        sys.exit('protos already exist')
    with TemporaryDirectory() as temp:
        print('cloning repo')
        porcelain.clone('https://github.com/googleapis/googleapis.git', target=os.path.join(temp, 'googleapis'), depth=1)
        print('repo cloned')
        wget.download('https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto', temp)
        

        protopath = os.path.join(ROOT_DIR, 'proto')
        if not os.path.exists(protopath):
            os.mkdir(protopath)
        Path(os.path.join(protopath, '__init__.py')).touch()
        os.chdir(temp)

        proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')

        protoc.main([
            'grpc_tools.protoc',
            '-I{}'.format(proto_include),
            f'--proto_path=googleapis:.',
            f'--python_out={protopath}',
            f'--grpc_python_out={protopath}',
            'rpc.proto'
        ])








