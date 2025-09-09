# NOTE: this is copied form nci-cidc-ngs-pipeline-api==0.1.25 which is archived

import os
from json import load


# __author__ = """NCI"""
# __email__ = "nci-cidc-tools-admin@mail.nih.gov"
# __version__ = "0.1.25"


_API_ENDING = "_output_API.json"
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_SCHEMA_PATH = os.path.join(_BASE_DIR, "output_API.schema.json")


try:
    with open(_SCHEMA_PATH, "r", encoding="UTF") as f:
        METASCHEMA = load(f)
except Exception as e:  # pylint: disable=broad-except
    raise Exception(f"Failed loading json {_SCHEMA_PATH}") from e

OUTPUT_APIS = {}
for dname, _, files in os.walk(_BASE_DIR):
    for fname in files:
        if fname.endswith(_API_ENDING):
            analysis = fname[: -len(_API_ENDING)]
            with open(os.path.join(dname, fname), "rb") as f:
                OUTPUT_APIS[analysis] = load(f)
