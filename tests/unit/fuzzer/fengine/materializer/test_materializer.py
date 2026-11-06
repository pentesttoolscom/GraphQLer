import unittest
from unittest.mock import MagicMock

from graphqler import config
from graphqler.fuzzer.engine.materializers.regular_payload_materializer import RegularPayloadMaterializer


def _input_object(type_name: str) -> dict:
    return {"kind": "INPUT_OBJECT", "name": type_name, "ofType": None, "type": type_name}


def _list_of(field: dict) -> dict:
    return {"kind": "LIST", "name": None, "ofType": field, "type": None}


class TestMaterializer(unittest.TestCase):
    def test_recursive_input_object_expansions_are_capped(self):
        api = MagicMock()
        api.input_objects = {
            "Filter": {
                "inputFields": {
                    "not": _input_object("Filter"),
                    "and": _list_of(_input_object("Filter")),
                    "or": _list_of(_input_object("Filter")),
                    "flag": {"kind": "SCALAR", "name": "Boolean", "ofType": None, "type": "Boolean"},
                }
            }
        }
        query = {"inputs": {"where": _input_object("Filter")}, "hardDependsOn": {}, "softDependsOn": {}}

        materializer = RegularPayloadMaterializer(api, fail_on_hard_dependency_not_met=False)
        inputs = materializer.materialize_inputs(query, query["inputs"], MagicMock(), max_depth=config.MAX_INPUT_DEPTH)

        self.assertEqual(inputs.count("flag:"), config.MAX_INPUT_OBJECT_CYCLES)
