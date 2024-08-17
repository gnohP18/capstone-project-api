# How to use

## Reference

### 1. Basic query

```json
POST /tam-cam/_search
{
    "query": {
        "match" : {
            "query" : "Bống bống!"
        }
    }
}
```

### 2. Multi field search

```json
POST /tam-cam/_search
{
    "query": {
        "multi_match" : {
            "query" : "bà lầm nhẩm",
            "fields": ["page_id", "words"]
        }
    }
}
# Sử dụng "fields" để thêm các trường
# example "fields": "_all", "some_field", ...
```

### 3. Boosting

```json
# Mục đích: Tăng trọng số của query search cho gần với kết quả nhất.
POST /tam-cam/_search
{
    "query": {
        "multi_match" : {
            "query" : "bà lầm nhẩm",
            "fields": ["page_id", "words"]
        }
    }
}

```

### 4. Fuzzy query

```json
Khải niệm về Levenshtein distance giữa chuỗi S1 và chuỗi S2 là số bước ít nhất biến chuỗi S1 thành chuỗi S2 thông qua 3 phép biến đổi là:
- Xoá 1 ký tự.
- Thêm 1 ký tự.
Thay ký tự này bằng ký tự khác. Ví dụ: Khoảng cách Levenshtein giữa 2 chuỗi "kitten" và "sitting" là 3, vì phải dùng ít nhất 3 lần biến đổi.
kitten -> sitten (thay "k" bằng "s") sitten -> sittin (thay "e" bằng "i") sittin -> sitting (thêm ký tự "g")

POST /tam-cam/_search
{
    "query": {
        "multi_match" : {
            "query" : "bà lầm nhẩm",
            "fields": ["_all"],
            "fuzziness": "AUTO"
        }
    }
}
```

### 5. Wildcard query

```json
# Mục đích: search theo template

POST /tam-cam/_search
{
    "query": {
        "wildcard" : {
            "words" : "t*"
        }
    },
}
```

### Query operation - Toán tử search

`must`

```json
Tất cả các điều kiện phải khớp, thoả mãn.

POST /tam-cam/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "keyword1",
            "fields": ["*"]  // Tìm kiếm trong tất cả các trường
          }
        },
        {
          "multi_match": {
            "query": "keyword2",
            "fields": ["*"]
          }
        }
      ]
    }
  }
}

```

`should`

```json
Cho phép các điều kiện thoả mãn hoặc không, ưu tiên các điều kiện có điểm số cao hơn. Nếu không có must thì ít nhất 1 should là true thì docs mới được trả về

POST /tam-cam/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "multi_match": {
            "query": "keyword1",
            "fields": ["*"]
          }
        },
        {
          "multi_match": {
            "query": "keyword2",
            "fields": ["*"]
          }
        }
      ],
      "minimum_should_match": 1  // Ít nhất 1 điều kiện `should` phải đúng
    }
  }
}
```
