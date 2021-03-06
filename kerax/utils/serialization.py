from typing import Dict, Any

import dill
import msgpack


def save_module(file_name: str, **config):
    """
    Serializes the module with the specified file name into MessagePack format.
    :param file_name: The name of the file (without the extension).
    :param config: Properties of the module to be serialized.
    """
    serialized_config: Dict[str, Any] = {}
    for k, v in config.items():
        item_dill: bytes = dill.dumps(v)
        item_msgpack: bytes = msgpack.packb(item_dill, use_bin_type=True)
        serialized_config[k] = item_msgpack

    with open(f"{file_name}.msgpack", "wb") as f:
        serialized_data: bytes = msgpack.packb(serialized_config)
        f.write(serialized_data)


def load_module(file_name: str) -> Dict[str, Any]:
    """
    Deserializes the module with the specified file name from MessagePack format.
    :param file_name: The name of the file (without the extension).
    :return: properties of the deserialized module in a dictionary form.
    """
    with open(f"{file_name}.msgpack", "rb") as f:
        deserialized_data: bytes = f.read()
        deserialized_config: Dict[str, Any] = msgpack.unpackb(deserialized_data)
        for k in list(deserialized_config):
            item_dill: bytes = msgpack.unpackb(deserialized_config.pop(k))
            deserialized_config[k.decode("utf-8")] = dill.loads(item_dill)
    return deserialized_config
