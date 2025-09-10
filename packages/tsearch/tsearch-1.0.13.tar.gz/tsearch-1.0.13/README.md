# MySearch

## Giới thiệu
**MySearch** là một module tìm kiếm dựa trên FAISS (Facebook AI Similarity Search) để thực hiện tìm kiếm vector hiệu quả. Hệ thống hỗ trợ tìm kiếm theo khoảng cách cosine và L2, đồng thời quản lý dữ liệu thông qua các lớp hỗ trợ như `IndexDB`, `FaissDB`, `InfoDB`.

## Tính năng chính
- Thêm vector embedding vào FAISS.
- Tìm kiếm các vector gần nhất dựa trên chỉ số khoảng cách.
- Xóa vector khỏi cơ sở dữ liệu FAISS.
- Cập nhật hoặc thay thế vector embedding.
- Kiểm tra tính nhất quán của cơ sở dữ liệu.

## Cấu trúc thư mục
```
.
├── logs/
│   ├── log_handler.py  # Xử lý ghi log
├── modules/
│   ├── utils/
│   │   ├── checker.py  # Kiểm tra tính hợp lệ của dữ liệu
│   │   ├── faiss_db.py  # Quản lý FAISS
│   │   ├── helper.py  # Hỗ trợ xử lý vector
│   │   ├── index_db.py  # Quản lý index của vector
│   │   ├── info_db.py  # Quản lý thông tin đối tượng
├── my_search.py  # Lớp chính MySearch
├── README.md  # Tài liệu này
```

## Cài đặt
Yêu cầu Python 3.8 trở lên và các thư viện:
```bash
pip install faiss-cpu numpy
```

## Hướng dẫn sử dụng

### Khởi tạo MySearch
```python
from my_search import MySearch

search_engine = MySearch(distance_type="cosin", element=512)
```

### Tạo collection
```python
list_field = ["id", "name", "vector"]
key_main = "id"
search_engine.create_collection(list_field, key_main)
```

### Thêm dữ liệu vào FAISS
```python
embedding = [[0.1, 0.2, 0.3, ..., 0.512]]  # Danh sách embedding có kích thước 512
list_field = [{"id": 1, "name": "Object1", "vector": embedding[0]}]

search_engine.add(embedding, list_field)
```

### Tìm kiếm
```python
query_vector = [0.1, 0.2, 0.3, ..., 0.512]
result = search_engine.search(query_vector, result_of_num=5)
print(result)
```

### Xóa dữ liệu
```python
search_engine.delete(key_mains=[1])
```

### Cập nhật dữ liệu
```python
new_vector = [0.2, 0.3, 0.4, ..., 0.512]
search_engine.replace(key_mains=[1], embeddings=[new_vector], indexs=[0])
```

## Cấu trúc lớp
### **MySearch**
- `add(embedding, list_field)`: Thêm một hoặc nhiều vector embedding vào FAISS.
- `search(embedding, result_of_num)`: Tìm kiếm vector gần nhất.
- `delete(key_mains)`: Xóa vector theo khóa chính.
- `replace(key_mains, embeddings, indexs, new_key_mains)`: Thay thế hoặc cập nhật vector.
- `create_collection(list_field, key_main)`: Tạo tập dữ liệu mới.

## Cấu trúc dữ liệu
- **IndexDB**: Lưu trữ ánh xạ giữa index FAISS và khóa chính (`key_main`).
- **FaissDB**: Quản lý cơ sở dữ liệu FAISS và thực hiện truy vấn.
- **InfoDB**: Quản lý thông tin đối tượng liên quan đến embedding.

## Ghi log
Module sử dụng `logger` để ghi lại quá trình hoạt động. Log được lưu trong thư mục `logs/`.

## Đóng góp
Mọi đóng góp vui lòng gửi pull request hoặc mở issue trên GitHub.

## Giấy phép
Dự án này sử dụng giấy phép MIT.

