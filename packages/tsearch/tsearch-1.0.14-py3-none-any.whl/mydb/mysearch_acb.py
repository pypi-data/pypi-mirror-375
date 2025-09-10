import faiss
import numpy as np

import sys
import os

# Thêm đường dẫn của thư mục chứa file main.py vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.loader import CFG
from logs.log_handler import logger
from utils.helper import rotate_list_left
from utils.helper import Vector
from utils.checker import Checker
from utils.info_db import InfoDB
from utils.index_db import IndexDB
from utils.faiss_db import FaissDB


class MySearch:
    def __init__(
        self,
        distance_type,
        element,
        max_embedding_flag=False,
        max_embedding=5,
        search_thresh=0.6,
    ):
        print("MySearch inited!")
        self.distance_type = distance_type
        self.element = element
        self.max_embedding_flag = max_embedding_flag
        self.max_embedding = max_embedding
        self.search_thresh = search_thresh
        self.key_main = None
        if self.distance_type not in CFG.distance_type:
            logger.error(f"Distance type not in {CFG.distance_type}")
            return None

    def create_collection(self, list_field, key_main):
        if self.key_main is not None:
            logger.info("Collection exited")
            return None
        elif key_main not in list_field:
            logger.info(f"{self.key_main} not in {list_field:}")
            return None
        self.key_main = key_main
        self.list_field = list_field
        self.key_main_index = list_field.index(key_main)
        self.info_db = InfoDB(
            list_field, key_main, self.max_embedding_flag, self.max_embedding
        )
        self.faiss_db = FaissDB(self.element, self.distance_type)
        self.index_db = IndexDB()
        self.checker = Checker(self)

    def _extrac_list_field_to_key_main(self, list_field):
        key_main = []
        for data in list_field:
            key_main.append(str(data[self.key_main_index]))
        return key_main

    def add(self, embedding, list_field):
        """
        embedding : list(list) or list
        list_field : list of fields
        """
        key_main = self._extrac_list_field_to_key_main(list_field)
        if not self.checker.check_condition_add(embedding, list_field, key_main):
            return []
        # embedding = Vector.convert_embedding(embedding)
        process_index, current_index = self.info_db.add(key_main, list_field)
        self.faiss_db.process_add(process_index, embedding, current_index)
        if not self.checker.check_post_add_faiss_db():
            return []
        # if not self.checker.check_pre_add_index_db(index_add):
        #     return []
        self.index_db.process_add(process_index, key_main)
        if not self.checker.check_post_add_index_db():
            return []
        if not self.checker.check_all_db():
            return []
        logger.info("Add embedding successful")
        return process_index

    def search(self, embedding, result_of_num):
        """
        Tìm kiếm các embedding gần giống với một embedding cho trước.

        Parameters:
            embedding (numpy.ndarray or list): Embedding đầu vào cần được tìm kiếm.
            result_of_num (int): Số lượng kết quả tìm kiếm được trả về cho mỗi embedding.

        Returns:
            list: Danh sách các kết quả của việc tìm kiếm. Mỗi phần tử trong danh sách tương ứng với một embedding và
                chứa các kết quả tìm kiếm cho embedding đó.
                Mỗi phần tử của danh sách kết quả cho một embedding là một danh sách chứa các thông tin của các đối tượng
                tìm thấy và có khoảng cách gần nhất đến embedding đầu vào.
                Trong trường hợp không có kết quả nào được tìm thấy hoặc khoảng cách quá lớn, phần tử tương ứng sẽ là None.
        """
        embedding = Vector.convert_embedding(embedding)
        result_batch_embedding = []
        for embedding_ in embedding:
            result_one_embedding = []
            D, I = self.faiss_db.search(embedding_, result_of_num)
            for index, distance in zip(I, D):
                if index == -1:
                    break
                if distance < self.search_thresh:
                    result_one_embedding.append(None)
                    continue
                key_main_result = self.index_db.get_key_main(index)
                object_info_result = self.info_db.get_object_info(key_main_result)
                object_info_result["score"] = distance
                result_one_embedding.append(object_info_result)
            result_batch_embedding.append(result_one_embedding)
        return result_batch_embedding

    def delete(self, key_mains):
        for key_main in key_mains:
            embedding_index = self.info_db.delete(key_main)
            if not len(embedding_index):
                return False
            for index in embedding_index:
                result = self.index_db.delete(index)
                if not result:
                    return False
                self.faiss_db.delete(index)
                if not self.checker.check_all_db():
                    return False
        return True

    def replace(self, key_mains, object_infos=None, embeddings=None, indexs=None):
        if object_infos is not None:
            for key_main, object_info in zip(key_mains, object_infos):
                result = self.info_db.replace(key_main, object_info)
                if not result:
                    return False
        if embeddings is not None:
            if indexs is None:
                logger.error("Indexs is required ")
                return False
            embeddings = Vector.convert_embedding(embeddings)
            for key_main, embedding, index in zip(key_mains, embeddings, indexs):
                embedding_index = self.info_db.get_embedding_index(key_main)
                if not len(embedding_index):
                    logger.error("No embedding in info db")
                    return False
                if index not in embedding_index:
                    logger.error("Index of keymain not in keymain'embedding index")
                    return False
                self.faiss_db.replace(embedding, index)
        return True
