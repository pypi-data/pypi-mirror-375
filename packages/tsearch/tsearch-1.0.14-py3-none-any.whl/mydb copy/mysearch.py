import os
import sys

import faiss
import numpy as np

current_directory = os.getcwd()
sys.path.append(current_directory)
from logs.log_handler import logger
from modules.utils.checker import Checker
from modules.utils.faiss_db import FaissDB
from modules.utils.helper import Vector, rotate_list_left
from modules.utils.index_db import IndexDB
from modules.utils.info_db import InfoDB


class CFG:
    distance_type = ["cosin", "L2"]


class MySearch:
    def __init__(
        self,
        distance_type="cosin",
        element=512,
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

        self.deleted_num = 0

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

    def preprocess_data(self, embedding):
        if len(embedding) == self.element:
            embedding = [embedding]
        embedding = Vector.convert_embedding(embedding)
        return embedding

    def ensure_list(self, obj):
        if isinstance(obj, list):
            return obj
        else:
            return [obj]

    def _extrac_list_field_to_key_main(self, list_field):
        key_main = []
        for data in list_field:
            key_main.append(data[self.key_main_index])
        return key_main

    def _test_all(self, process_index):
        logger.debug(f"process_index: {process_index}")
        logger.debug(f"Deleted num: {self.deleted_num}")
        logger.debug(f"tổng số vector: {self.get_num_vector()}")
        logger.debug(
            f"Số index : {len(self.index_db.index_db)} - {self.index_db.index_db}"
        )
        logger.debug(f"Số info db : {self.info_db.info_db}")
        self.checker.check_all_db()

    def add(self, embedding, list_field):
        """
        embedding : list(list(embeeding)) or list
        list_field : list of fields
        """
        logger.debug("Before add")
        self._test_all(0)
        embedding = self.preprocess_data(embedding)
        if not self.checker.check_pre_add(embedding, list_field):
            return []
        key_main = self._extrac_list_field_to_key_main(list_field)
        if not self.checker.check_condition_add(embedding, list_field, key_main):
            return []
        # embedding = Vector.convert_embedding(embedding)
        process_index, current_index = self.info_db.add(key_main, list_field)
        self.faiss_db.process_add(process_index, embedding, current_index)
        self._test_all(process_index)
        if not self.checker.check_post_add_faiss_db():
            return []
        # if not self.checker.check_pre_add_index_db(index_add):
        #     return []
        self.index_db.process_add(process_index, key_main)
        if not self.checker.check_post_add_index_db():
            return []
        if not self.checker.check_all_db():
            return []
        logger.debug("After add")
        self._test_all(0)
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
        embedding = self.preprocess_data(embedding)
        # embedding = Vector.convert_embedding(embedding)
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
        key_mains = self.ensure_list(key_mains)
        for key_main in key_mains:
            key_main_info = self.get_list_field_by_key_main(key_main)
            self.deleted_num += len(key_main_info["index_embedding"])
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
        self.checker.check_all_db()
        return True

    def replace(
        self,
        key_mains,
        object_infos=None,
        embeddings=None,
        indexs=None,
        new_key_mains=None,
    ):
        # TODO: Check len key_mains vs object_infos
        key_mains = self.ensure_list(key_mains)
        if object_infos is not None:
            object_infos = self.ensure_list(object_infos)
            for key_main, object_info in zip(key_mains, object_infos):
                # key_main = str(key_main)
                result = self.info_db.replace(key_main=key_main, object_info=object_info)
                if not result:
                    return False
        if embeddings is not None:
            embeddings = self.preprocess_data(embeddings)
            indexs = self.ensure_list(indexs)
            if indexs is None:
                logger.error("Indexs is required ")
                return False
            embeddings = Vector.convert_embedding(embeddings)
            logger.debug(f"key_mains: {key_mains}")
            logger.debug(f"info_db:{self.info_db.info_db}")
            for key_main, embedding, index in zip(key_mains, embeddings, indexs):
                # key_main = str(key_main)
                embedding_index = self.info_db.get_embedding_index(key_main)
                if not len(embedding_index):
                    logger.error("No embedding in info db")
                    return False
                if index not in embedding_index:
                    logger.debug(f"embedding_index: {embedding_index}")
                    logger.debug(f"index: {index}")
                    logger.error("Index of keymain not in keymain'embedding index")
                    return False
                self.faiss_db.replace(embedding, index)
        # Chưa test
        if new_key_mains is not None:
            new_key_mains = self.ensure_list(new_key_mains)
            for key_main, new_key_main in zip(key_mains, new_key_mains):
                embedding_index = self.info_db.get_embedding_index(key_main)
                self.index_db.replace(embedding_index, new_key_main)
                self.info_db.replace(key_main=key_main, new_key_main=new_key_main)

        logger.debug("Replace successful")
        return True

    def get_num_vector(self):
        return self.faiss_db.get_num_vector()

    def check_exits_key_main(self, key_main):
        return key_main in self.info_db.info_db

    def get_list_field_by_key_main(self, key_main):
        return self.info_db.get_list_field_by_key_main(key_main)
