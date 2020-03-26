import json


class HexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj.hex())
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
