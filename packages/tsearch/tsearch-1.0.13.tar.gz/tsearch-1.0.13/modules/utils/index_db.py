from logs.log_handler import logger


class IndexDB:
    def __init__(self) -> None:
        logger.debug("Init IndexDB")
        self.index_db = {}

    def add(self, index, key):
        self.index_db[index] = key

    def process_add(self, process_index, key_main):
        for i, index in enumerate(process_index):
            self.add(index, key_main[i])

    def get_key_main(self, index):
        return self.index_db[index]

    def delete(self, index):
        if index not in self.index_db:
            logger.error(f"{index} not found in index_db")
            return False
        del self.index_db[index]
        return True

    def replace(self, indexs, new_key_main):
        for index in indexs:
            self.index_db[index] = new_key_main
