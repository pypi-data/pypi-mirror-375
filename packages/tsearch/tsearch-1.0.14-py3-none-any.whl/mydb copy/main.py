from logs.log_handler import logger
from config.loader import cfg
from modules.entities.redis.redis_utils import RedisUtils
from mysearch import MySearch
import numpy as np
import random


def generate_metadata():
    metadata = []
    for _ in range(500):
        GB = random.randint(1, 3)
        person_id = random.randint(1, 10)
        person_name = f"Person_{person_id}"
        tracking_id = random.randint(1, 100)
        vector = np.random.rand(512).tolist()  # Vector đã được chuẩn hóa
        metadata.append(
            {
                "GB": GB,
                "person_name": person_name,
                "person_id": person_id,
                "tracking_id": tracking_id,
                "vector": vector,
            }
        )
    return metadata


def main(db, metadata):
    my_search = MySearch(distance_type="cosin", element=512, max_embedding_flag=True)
    list_field = ["GB", "person_name", "person_id", "tracking_id"]
    my_search.create_collection(list_field=list_field, key_main="GB")
    add_count = 0
    search_count = 0
    while True:
        for data in metadata:
            list_field = [
                data["GB"],
                data["person_name"],
                data["person_id"],
                data["tracking_id"],
            ]
            print(list_field)
            if add_count < 100:
                my_search.add([data["vector"], data["vector"]], [list_field, list_field])
                print(my_search.index_db.index_db)
                print(my_search.info_db.info_db)
                print(my_search.faiss_db.index_faiss.ntotal)
                print(len(my_search.index_db.index_db))
                print(len(my_search.info_db.info_db))
                print("*" * 20)
            else:
                result = my_search.search(data["vector"], 5)
                # result = my_search.delete([1])
                # result = my_search.replace([1], object_infos=[list_field])
                # result = my_search.replace([1], embeddings=[data["vector"]], indexs=[1])
                # if not result:
                #     break
                print(result)
                break
            add_count += 1
        break


if __name__ == "__main__":
    num_vectors = 500
    vector_length = 128
    list1 = np.random.rand(num_vectors, vector_length)
    metadata = generate_metadata()
    # print(metadata)
    main(list1, metadata)
