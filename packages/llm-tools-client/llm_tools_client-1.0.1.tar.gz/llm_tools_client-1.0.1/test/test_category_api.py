from llm_tools_client import ApiClient, Configuration
from llm_tools_client.api import CategoryControllerApi 

# 1. API 서버 설정
config = Configuration(host="http://localhost:8080/llm-tools/v1")
client = ApiClient(config)

# 2. API 객체 생성
api = CategoryControllerApi(client)

# 3. API 호출 (예시)
try:
    result = api.get_category_detail(category_id="f09db937-97cb-4435-a5d9-fa588140fee2")
    print("Category 상세 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_category_list(query="")
    print("Category 리스트 조회 결과 : ", result)

except Exception as e:
    print("API 호출 실패:", e)
