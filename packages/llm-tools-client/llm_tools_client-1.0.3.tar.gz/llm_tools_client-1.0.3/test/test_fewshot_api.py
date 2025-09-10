from llm_tools_client import ApiClient, Configuration
from llm_tools_client.api import FewshotControllerApi
from llm_tools_client.models.fewshot_request_dto import FewshotRequestDto

# 1. API 서버 설정
config = Configuration(host="http://localhost:8080/llm-tools/v1")
client = ApiClient(config)

# 2. API 객체 생성
api = FewshotControllerApi(client)

# 3. API 호출 (예시)
try:
    print("GET 테스트")
    result = api.get_fewshot_list(query="", page=1, size=10)
    print("Fewshot 리스트 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_fewshot_detail(name="test", version="test", fewshot_id="test", fewshot_version_id="test")
    print("Fewshot 상세 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_fewshot_version_list(fewshot_id="test")
    print("Fewshot 버전 리스트 조회 결과 : ", result)
    print("--------------------------------")
    result = api.check_duplicate_name1(name="test")
    print("Fewshot 명 중복 확인 결과 : ", result)
    print("--------------------------------")
    result = api.check_duplicate_version1(version="test")
    print("Fewshot 버전 중복 확인 결과 : ", result)
    print("--------------------------------")
    
    # print("POST 테스트")
    # result = api.save_fewshot(fewshot_request_dto=FewshotRequestDto(name="test", version="test", description="test", category_id="test", pairs=[]))
    # print("Fewshot 생성 결과 : ", result)
    # print("--------------------------------")
    # result = api.update_fewshot(fewshot_request_dto=FewshotRequestDto(name="test", version="test", description="test", category_id="test", pairs=[]))
    # print("Fewshot 수정 결과 : ", result)
    # print("--------------------------------")
    # result = api.delete_fewshot(fewshot_id="test")
    # print("Fewshot 삭제 결과 : ", result)
    # print("--------------------------------")
    
    
except Exception as e:
    print("API 호출 실패:", e)
