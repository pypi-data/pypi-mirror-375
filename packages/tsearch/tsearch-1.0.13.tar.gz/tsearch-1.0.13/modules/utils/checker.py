from logs.log_handler import logger


class Checker:
    def __init__(self, search):
        self.search = search

    def check_pre_add(self, embedding, list_field):
        if len(embedding) != len(list_field) and len(embedding[0]) != len(list_field):
            logger.error(
                f"Num of vector differance num of list_field, vector is {len(embedding)} or {len(embedding[0])}, list_field is {len(list_field)}"
            )
        return len(embedding) == len(list_field)

    ##################################################################################################
    def sub_check_condition_add(self, embedding, list_field):
        condition_add = True
        if len(embedding) != self.search.element:
            logger.error(
                f"Vector with mismatched elements, vector is {len(embedding)}, element is {self.search.element}"
            )
            condition_add = False
        if len(list_field) != len(self.search.list_field):
            logger.error("Number of fields in list_field is different when create")
            logger.info(f"list_field of current: {list_field}")
            logger.info(f"list_field of create: {self.search.list_field}")
            condition_add = False
        return condition_add

    def check_condition_add(self, embedding, list_field, key_main):
        if len(embedding) != len(list_field) != len(key_main):
            logger.error("The lengths of embedding, list_field, key_main do not match")
            return False
        return self.sub_check_condition_add(embedding[0], list_field[0])

    ##################################################################################################
    # def check_pre_add_index_db(self, index_add):
    #     for i in range(len(index_add)):
    #         if index_add[i] in self.search.index_db:
    #             logger.error(f"Index add : {index_add} exited in index_db")
    #             return False
    #     return True
    ##################################################################################################
    def check_post_add_index_db(self):
        if len(self.search.index_db.index_db) != self.search.faiss_db.index_faiss.ntotal:
            logger.error("The lengths of index_db and index_faiss do not match")
            return False
        return True

    ##################################################################################################
    def check_post_add_faiss_db(self):
        if (
            self.search.info_db.future_index - self.search.deleted_num + 1
            != self.search.faiss_db.index_faiss.ntotal
        ):
            logger.error("current_index and total vector do not match")
            return False
        return True

    ##################################################################################################
    def check_all_db(self):
        count_index_in_info_db = 0
        for value in self.search.info_db.info_db.values():
            count_index_in_info_db += len(value["index_embedding"])
        if (
            count_index_in_info_db
            != self.search.faiss_db.index_faiss.ntotal
            != len(self.search.index_db.index_db)
        ):
            logger.error(
                "The lengths of index_info, index_db and index_faiss do not match"
            )
            return False
        return True
