#!/usr/bin/env python3

import json
from abc import abstractmethod

from loguru import logger

from provisioner_shared.components.runtime.errors.cli_errors import FailedToSerializeConfiguration


class SerializationBase:

    dict_obj: dict

    # TODO: make dict_obj optional with default {} value
    @abstractmethod
    def __init__(self, dict_obj: dict) -> None:
        self.dict_obj = dict_obj
        # print the actual class name
        try:
            # print(f"Creating {self.__class__.__name__} with dict_obj: {dict_obj}")
            if dict_obj is None:
                logger.warning(f"Python dict obj is empty. type: {type(self)}")
                return
            self._try_parse_config(dict_obj)
        except Exception as ex:
            raise FailedToSerializeConfiguration(f"Failed to serialize configuration. ex: {ex}")

    @abstractmethod
    def _try_parse_config(self, dict_obj: dict) -> None:
        pass

    def to_json(self) -> str:
        # return json.dumps(self, default=lambda o: o.__dict__, indent=4)
        return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items() if k != "dict_obj"}, indent=4)

    @abstractmethod
    def merge(self, other: "SerializationBase") -> "SerializationBase":
        """
        Merge this serialization class with another
        """
        return self

    def maybe_get(self, dict_path: str):
        """
        Try to get the value from a nested dictionary by a sequence of keys.

        :param keys: A dot-separated string of keys.
        :return: The primitive value if it exists, None otherwise.
        """
        temp_dict = self.dict_obj
        dict_path = dict_path.split(".")
        for key in dict_path:
            if isinstance(temp_dict, dict) and key in temp_dict:
                temp_dict = temp_dict[key]
            else:
                return None

        # Only return if it's a primitive value
        if isinstance(temp_dict, (str, int, float, bool)) or temp_dict is None:
            return temp_dict
        return None
