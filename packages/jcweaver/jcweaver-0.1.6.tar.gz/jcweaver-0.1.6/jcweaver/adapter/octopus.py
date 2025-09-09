import os

from jcweaver.adapter.BaseAdapter import BaseAdapter
from jcweaver.core.const import DataType
from jcweaver.core.logger import logger


class OctopusAdapter(BaseAdapter):
    def __init__(self):
        self.output = ""

    def before_task(self, inputs, context: dict):
        logger.info("execute before task")

    def after_task(self, outputs, context: dict):
        logger.info("execute after task")

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DataType.DATASET:
            data_path = os.environ.get("dataset_input")
            if not data_path:
                logger.error("dataset_input is not set")
                return ""
            return os.path.join(data_path, file_path)

        if data_type == DataType.MODEL:
            data_path = os.environ.get("model_input")
            if not data_path:
                logger.error("model_input is not set")
                return ""
            return os.path.join(data_path, file_path)

        if data_type == DataType.CODE:
            data_path = os.environ.get("code_input")
            if not data_path:
                logger.error("code_input is not set")
                return ""
            return os.path.join(data_path, file_path)
        logger.error(f"Unknown data type for input: {data_type}")
        return ""

    def output_prepare(self, data_type: str, file_path: str):
        data_path = os.environ.get("output",  "./output")

        if not os.path.exists(data_path):
            logger.info(f"create output directory: {data_path}")
            os.makedirs(data_path)

        return os.path.join(data_path, file_path)
