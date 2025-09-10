import faiss
import numpy as np
from logs.log_handler import logger


class FaissDB:
    def __init__(self, element, distance_type) -> None:
        logger.debug("Init FaissDB")
        self.element = element
        self.distance_type = distance_type
        self.index_faiss = self.create_index()

    def create_index(self):
        index_faiss = None
        if self.distance_type == "cosin":
            index_faiss = faiss.IndexFlatIP(self.element)
            index_faiss = faiss.IndexIDMap(index_faiss)
        if self.distance_type == "L2":
            quantizer = faiss.IndexFlatL2(self.element)
            index_faiss = faiss.IndexIVFFlat(
                quantizer, self.element, 1, faiss.METRIC_INNER_PRODUCT
            )
            # index_faiss = faiss.IndexIVFFlat(quantizer, element, 1, faiss.METRIC_L2)
        return index_faiss

    def add(self, embedding, index=None):
        if self.distance_type == "cosin":

            self.index_faiss.add_with_ids(np.array([embedding]), np.array([index]))
        if self.distance_type == "L2":
            if not self.index_faiss.is_trained:
                self.index_faiss.train(embedding)
            self.index_faiss.add(embedding)

    def process_add(self, process_index, embedding, current_index):
        for idx, index in enumerate(process_index):
            if index > current_index:
                self.add(embedding[idx], index)
            else:
                self.index_faiss.remove_ids(np.array([index]))
                self.add(embedding[idx], index)

    def delete(self, index):
        self.index_faiss.remove_ids(np.array([index]))

    def replace(self, new_vector, replace_index):
        self.index_faiss.remove_ids(np.array([replace_index]))
        logger.debug(new_vector.shape)
        new_vector = np.array([new_vector])
        self.index_faiss.add_with_ids(new_vector, np.array([replace_index]))

    def search(self, embedding, result_of_num):
        D, I = self.index_faiss.search(np.array([embedding]), result_of_num)
        return D[0], I[0]

    def get_num_vector(self):
        return self.index_faiss.ntotal
