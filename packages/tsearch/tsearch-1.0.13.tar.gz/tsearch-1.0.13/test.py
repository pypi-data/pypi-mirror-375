import numpy as np
import time
import json
from modules.entities.redis.redis_utils import RedisUtils


# Function to send vector to Redis using xadd
def send_vector_to_redis(vector, topic):
    conn.xadd(topic, {"vector": json.dumps(vector.tolist())})


num_vectors = 500
vector_length = 512
list1 = np.random.rand(num_vectors, vector_length)
list2 = np.random.rand(num_vectors, vector_length)
conn = RedisUtils.create_connection(host="localhost", port=6379)
count = 0
while True:
    for vector in list1:
        count += 1
        print(count)
        send_vector_to_redis(vector, "test")
        time.sleep(1)
