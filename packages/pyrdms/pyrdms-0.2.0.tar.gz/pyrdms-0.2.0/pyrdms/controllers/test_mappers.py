from .mappers import Proto2Py, Py2Proto

import json

from pyrdms.proto import rdm_pb2_grpc as rdm_pb2_grpc
from pyrdms.proto import rdm_pb2 as rdm_pb2

from pyrdms.core.entities import DomainModelMeta, DomainFunctionMeta

def test_map_meta():
    meta = DomainModelMeta(
        name="some_domain_model",
        domain_functions={
            "test1": DomainFunctionMeta(
                name="test1",
                args=[bool,int,str,list],
                ret=bool,
            )
        }
    )

    proto = Py2Proto.map_meta(meta)

    assert proto.name == meta.name
    assert proto.descriptors["test1"].name == "test1"
    assert proto.descriptors["test1"].return_value == rdm_pb2.LOGICAL
    assert len(proto.descriptors["test1"].arguments) == 4
    assert proto.descriptors["test1"].arguments[0] == rdm_pb2.LOGICAL
    assert proto.descriptors["test1"].arguments[1] == rdm_pb2.NUMERICAL
    assert proto.descriptors["test1"].arguments[2] == rdm_pb2.STRING
    assert proto.descriptors["test1"].arguments[3] == rdm_pb2.LIST

def test_map_int():
    val = Py2Proto.map(1)
    assert val.type == rdm_pb2.NUMERICAL
    assert val.value.numerical_value == 1.0

    assert Proto2Py.map(val) == 1.0

def test_map_float():
    val = Py2Proto.map(1.23)
    assert val.type == rdm_pb2.NUMERICAL
    assert abs(val.value.numerical_value - 1.23) < 1e-9

    assert abs(Proto2Py.map(val) - 1.23) < 1e-9

def test_map_str():
    val = Py2Proto.map("123")
    assert val.type == rdm_pb2.STRING
    assert val.value.string_value == "123"

    assert Proto2Py.map(val) == "123"

def test_map_bool():
    val1 = Py2Proto.map(None)
    val2 = Py2Proto.map(True)

    assert val1.type == rdm_pb2.LOGICAL
    assert val1.value.logical_value == rdm_pb2.NONE

    assert val2.type == rdm_pb2.LOGICAL
    assert val2.value.logical_value == rdm_pb2.TRUE

    assert Proto2Py.map(val1) == None
    assert Proto2Py.map(val2) == True

def test_map_list():
    some_list = [1, True, "123"]

    val = Py2Proto.map(some_list)

    assert val.type == rdm_pb2.LIST
    assert len(val.list_of_values.data) == 3

    assert val.list_of_values.data[0].type == rdm_pb2.NUMERICAL
    assert val.list_of_values.data[1].type == rdm_pb2.LOGICAL
    assert val.list_of_values.data[2].type == rdm_pb2.STRING

    assert val.list_of_values.data[0].value.numerical_value == 1.0
    assert val.list_of_values.data[1].value.logical_value == rdm_pb2.TRUE
    assert val.list_of_values.data[2].value.string_value == "123" 

    assert Proto2Py.map(val) == some_list

def test_map_list_of_lists():
    some_list = [1, True, "123", [1, True, "123"]]

    val = Py2Proto.map(some_list)

    assert val.type == rdm_pb2.LIST
    assert len(val.list_of_values.data) == 4

    assert val.list_of_values.data[0].type == rdm_pb2.NUMERICAL
    assert val.list_of_values.data[1].type == rdm_pb2.LOGICAL
    assert val.list_of_values.data[2].type == rdm_pb2.STRING

    assert val.list_of_values.data[0].value.numerical_value == 1.0
    assert val.list_of_values.data[1].value.logical_value == rdm_pb2.TRUE
    assert val.list_of_values.data[2].value.string_value == "123" 

    assert val.list_of_values.data[3].type == rdm_pb2.LIST
    assert len(val.list_of_values.data[3].list_of_values.data) == 3

    assert val.list_of_values.data[3].list_of_values.data[0].type == rdm_pb2.NUMERICAL
    assert val.list_of_values.data[3].list_of_values.data[1].type == rdm_pb2.LOGICAL
    assert val.list_of_values.data[3].list_of_values.data[2].type == rdm_pb2.STRING

    assert val.list_of_values.data[3].list_of_values.data[0].value.numerical_value == 1.0
    assert val.list_of_values.data[3].list_of_values.data[1].value.logical_value == rdm_pb2.TRUE
    assert val.list_of_values.data[3].list_of_values.data[2].value.string_value == "123" 

    assert Proto2Py.map(val) == some_list

def test_map_dict():
    data = json.loads("""{
  "basicTypes": {
    "string": "Hello, World!",
    "number": 42,
    "float": 3.14159,
    "negative": -7.5,
    "booleanTrue": true,
    "booleanFalse": false,
    "nullValue": null
  },
  "unicodeStrings": {
    "emoji": "Hello 🌍 World! 🚀",
    "mixedUnicode": "中文 Español Français العربية"
  },
  "edgeCases": {
    "emptyString": "",
    "zero": 0,
    "negativeZero": -0,
    "largeNumber": 1.23456789e+30,
    "smallNumber": 1.23456789e-30,
    "maxSafeInteger": 9007199254740991,
    "minSafeInteger": -9007199254740991
  },
  "complexStructures": {
    "nestedObject": {
      "level1": {
        "level2": {
          "level3": "deep value",
          "array": [1, 2, 3]
        }
      }
    },
    "mixedArray": [
      "string",
      42,
      true,
      false,
      null,
      {"object": "in array"},
      ["nested", "array"]
    ],
    "emptyArrays": {
      "emptyArray": [],
      "emptyObject": {}
    }
  },
  "specialKeys": {
    "": "empty key",
    "key with spaces": "value",
    "key-with-dashes": "value",
    "key_with_underscores": "value",
    "keyWithCamelCase": "value",
    "KeyWithPascalCase": "value",
    "123numeric": "numeric first",
    "special!@#$%^&*()": "special chars in key"
  },
  "boundaryValues": {
    "maxDecimals": 0.1234567890123456,
    "scientificNotation": [1e10, 1e-10, -1e10, -1e-10],
    "infinityLike": 1.7976931348623157e+308
  },
  "dateTimeFormats": {
    "isoDate": "2023-12-25T10:30:00.000Z",
    "dateOnly": "2023-12-25",
    "timeOnly": "10:30:00",
    "withTimezone": "2023-12-25T10:30:00+01:00"
  },
  "escapeSequences": {
    "backslashes": "\\\\backslashes\\\\",
    "unicodeEscape": "\\u00A9 Copyright \\u2764"
  },
  "deepStructure": {
    "very": {
      "deeply": {
        "nested": {
          "object": {
            "with": {
              "many": {
                "levels": {
                  "of": {
                    "nesting": "final value",
                    "array": [
                      {
                        "nestedInArray": {
                          "anotherLevel": "array value"
                        }
                      }
                    ]
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "largeArray": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
  "booleanArray": [true, false, true, false],
  "nullArray": [null, null, null],
  "mixedEmpty": [null, "", 0, false, [], {}]
}""")
    
    assert Proto2Py.map(Py2Proto.map(data)) == data