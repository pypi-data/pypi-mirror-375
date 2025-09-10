import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def rotate_list_right(lst, n):
    length = len(lst)
    n = n % length  # Đảm bảo n không lớn hơn độ dài của list

    rotated_list = lst[-n:] + lst[:-n]
    return rotated_list


def rotate_list_left(lst, n):
    length = len(lst)
    n = n % length  # Đảm bảo n không lớn hơn độ dài của list

    rotated_list = lst[n:] + lst[:n]
    return rotated_list


class Vector:
    @staticmethod
    def is_normalized(vector):
        norm = np.linalg.norm(vector)
        return np.isclose(norm, 1.0)

    @staticmethod
    def normalize_vector(vector):
        """
        Chuẩn hóa vector.

        Tham số:
            vector (array-like): Vector cần được chuẩn hóa.

        Trả về:
            normalized_vector (numpy.ndarray): Vector đã được chuẩn hóa.
        """
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    @staticmethod
    def convert_embedding(embedding):
        """
        Chuyển đổi embedding và chuẩn hóa các vector.

        Tham số:
            embedding (list): Danh sách các vector embedding.

        Trả về:
            normalized_embedding (numpy.ndarray): Embedding đã được chuyển đổi và chuẩn hóa.
        """
        embedding = np.array(
            [np.array(embedding_).astype(np.float32) for embedding_ in embedding.copy()]
        )

        # Chuẩn hóa từng vector trong embedding
        normalized_embedding = np.array(
            [Vector.normalize_vector(vector) for vector in embedding]
        )

        return normalized_embedding


class Zones:
    @staticmethod
    def check_point_in_zones(point, zones):
        for zone in zones:
            if Polygon(zone).contains(Point(point)):
                return True
        return False

    @staticmethod
    def filter_bbox_in_zone(zone, metadata):
        idxs_del = []
        for idx, obj in enumerate(metadata["objects"]):
            bbox = obj["bbox"]
            point = [int((bbox[0] + bbox[2]) / 2), int(bbox[3])]
            if not Zones.check_point_in_zones(point, zone):
                idxs_del.append(idx)
        for idx in idxs_del:
            del metadata["objects"][idx]
        return metadata
