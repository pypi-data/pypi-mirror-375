import copy

from logs.log_handler import logger
from modules.utils.helper import rotate_list_left


class InfoDB:
    def __init__(self, list_field, key_main, max_embedding_flag, max_embedding) -> None:
        logger.debug("Init InfoDB")
        self.key_main = key_main
        self.list_field = list_field
        self.max_embedding_flag = max_embedding_flag
        self.max_embedding = max_embedding

        self.info_db = {}
        self.future_index = -1
        self.current_index = 0

    def get_object_info(self, key_main, shorter=False):
        if key_main not in self.info_db:
            logger.error(f"key_main: {key_main} not in info_db")
            return {}
        result = copy.deepcopy(self.info_db[key_main])
        if shorter:
            del result["index_embedding"]
        return result

    def get_embedding_index(self, key_main):
        if key_main not in self.info_db:
            logger.error(f"{key_main} not found in info_db")
            return []
        return self.info_db[key_main]["index_embedding"]

    def add(self, key_main, list_field):
        self.current_index = self.future_index
        process_index = []
        for idx, key in enumerate(key_main):
            # key = str(key)
            if key not in self.info_db:
                self.info_db[key] = {}
                self.info_db[key]["index_embedding"] = []
            # update new info
            pre_index_embedding = self.info_db[key]["index_embedding"]
            self.info_db[key] = {
                self.list_field[i]: list_field[idx][i]
                for i in range(len(self.list_field))
            }
            self.info_db[key]["index_embedding"] = pre_index_embedding

            self.future_index += 1
            if not self.max_embedding_flag:
                self.info_db[key]["index_embedding"].append(self.future_index)
                process_index.append(self.future_index)
            else:
                if len(self.info_db[key]["index_embedding"]) >= self.max_embedding:
                    process_index.append(self.info_db[key]["index_embedding"][0])
                    self.info_db[key]["index_embedding"] = rotate_list_left(
                        self.info_db[key]["index_embedding"], 1
                    )
                    self.future_index -= 1
                else:
                    self.info_db[key]["index_embedding"].append(self.future_index)
                    process_index.append(self.future_index)
        return process_index, self.current_index

    def delete(self, key_main):
        # key_main = str(key_main)
        if key_main not in self.info_db:
            logger.error(f"{key_main} not found in info_db")
            return []
        embedding_index = self.get_embedding_index(key_main)
        del self.info_db[key_main]
        return embedding_index

    def replace(self, key_main, object_info=None, new_key_main=None):
        # key_main = str(key_main)
        if object_info is not None:
            if key_main not in self.info_db:
                logger.error(f"{key_main} not found in info_db")
                return False
            pre_index_embedding = self.info_db[key_main]["index_embedding"].copy()
            self.info_db[key_main] = {
                self.list_field[i]: object_info[i] for i in range(len(self.list_field))
            }
            self.info_db[key_main]["index_embedding"] = pre_index_embedding
        if new_key_main is not None:
            self.info_db[new_key_main] = copy.deepcopy(self.info_db[key_main])
            self.delete(key_main)
        return True

    def get_list_field_by_key_main(self, key_main):
        return self.info_db[key_main]
