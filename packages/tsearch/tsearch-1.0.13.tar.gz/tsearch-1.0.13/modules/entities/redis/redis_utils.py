import json

import cv2
import numpy as np
import redis
import simplejpeg
from logs.log_handler import logger


class RedisUtils:
    _pre_last_id = {}

    def __init__(self):
        logger.info("Init Redis_utils")

    @staticmethod
    def create_connection(host, port, decode=False):
        """Initial redis and pub"""
        if decode:
            conn = redis.Redis(
                host=host, port=port, decode_responses=True, charset="utf-8"
            )
        else:
            conn = redis.Redis(host=host, port=port)
        if not conn.ping():
            raise Exception(f"Redis unavailable. Redis config: {host} - {port}")
        logger.debug("Connect Redis successfully.")
        return conn

    @staticmethod
    def image2bytes(image, method="simplejpeg", quality=95):
        if method == "cv2":
            # Check if the image is a NumPy array
            if isinstance(image, np.ndarray):
                # Convert the NumPy array to a binary format (e.g., JPEG or PNG)
                # In reality, you would use a suitable image encoding method.
                image_bytes = cv2.imencode(".jpg", image)[1].tobytes()
            raise ValueError("Input must be a NumPy array representing an image")
        elif method == "simplejpeg":
            image_bytes = simplejpeg.encode_jpeg(image, quality=quality, colorspace="BGR")
        return image_bytes

    @staticmethod
    def bytes2image(image_bytes, method="cv2"):
        if method == "cv2":
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
        return image

    @classmethod
    def get_last(cls, conn, topic, camera_id):
        """Gets latest from ai service"""
        try:
            if camera_id not in cls._pre_last_id:
                cls._pre_last_id[camera_id] = 0
            # getting the latest tracking data from Redis.
            p = conn.pipeline()
            p.xrevrange(topic, count=1)  # Latest tracking
            p_tuple = p.execute()
            msg = p_tuple[0]
            if msg:
                last_id = msg[0][0]
                if last_id == cls._pre_last_id[camera_id]:
                    return None, None
                cls._pre_last_id[camera_id] = last_id
                json_data = json.loads(msg[0][1][b"metadata"])
                frame_bytes = msg[0][1][b"frame"]
                return json_data, frame_bytes
            return None, None
        except Exception as e:
            logger.exception(f"Failed to get last data: {e}")
            return None, None

    @classmethod
    def get_last_ai_service(cls, conn, topic):
        """Gets latest from ai service"""
        try:
            dict_frame = {}
            # getting the latest tracking data from Redis.
            p = conn.pipeline()
            p.xrevrange(topic, count=1)  # Latest tracking
            p_tuple = p.execute()
            msg = p_tuple[0]
            if msg:
                last_id = msg[0][0]
                if last_id == cls._pre_last_id:
                    return None, None
                cls._pre_last_id = last_id
                # logger.debug(msg)
                json_data = json.loads(msg[0][1]["data"])
                for camera_id in list(json_data.keys()):
                    json_data[camera_id] = json_data[camera_id]
                    dict_frame[camera_id] = json_data[camera_id]["frame"]
                    del json_data[camera_id]["frame"]
                return json_data, dict_frame
            return None, None
        except Exception as e:
            logger.exception(f"Failed to get last data: {e}")
            return None, None

    def get_message_by_xreadgroup(conn, topic, group_name, consumer_name):
        response = conn.xreadgroup(group_name, consumer_name, {topic: ">"}, count=1)
        try:
            if response:
                for topic, data in response:
                    last_id, messages = data[0]

                    last_id = str(str(last_id.decode("utf-8")).split("-")[0])

                    data_json = messages["json".encode("utf-8")]
                    metadatas = json.loads(data_json)

                    camera_id = messages["camera_id".encode("utf-8")].decode("utf-8")

                    frame_bytes = messages["frame".encode("utf-8")]

                    conn.xack(
                        topic,
                        group_name,
                        *[message_id for _, data in response for message_id, _ in data],
                    )

                    return metadatas, frame_bytes
            else:
                return None, None
        except KeyboardInterrupt:
            return None, None
        except redis.exceptions.ResponseError as e:
            return None, None
