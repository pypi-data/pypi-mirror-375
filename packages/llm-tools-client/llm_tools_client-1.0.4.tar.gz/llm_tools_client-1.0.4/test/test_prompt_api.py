from llm_tools_client import ApiClient, Configuration
from llm_tools_client.api import PromptControllerApi
from llm_tools_client.models.prompt_request_dto import PromptRequestDto

# 1. API 서버 설정
config = Configuration(host="http://localhost:8080/llm-tools/v1")
client = ApiClient(config)

# 2. API 객체 생성
api = PromptControllerApi(client)

# 3. API 호출 (예시)
try:
    print("GET 테스트")
    result = api.get_prompt_list(query="", page=1, size=10)
    print("Prompt 리스트 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_prompt_detail(name="test", version="test", prompt_id="test", prompt_version_id="test")
    print("Prompt 상세 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_prompt_version_list(prompt_id="test")
    print("Prompt 버전 리스트 조회 결과 : ", result)
    print("--------------------------------")
    result = api.check_duplicate_name(name="test")
    print("Prompt 명 중복 확인 결과 : ", result)
    print("--------------------------------")
    result = api.check_duplicate_version(version="test")
    print("Prompt 버전 중복 확인 결과 : ", result)
    print("--------------------------------")
    
    # print("POST 테스트")
    # result = api.save_prompt(prompt_request_dto=PromptRequestDto(name="test", version="test", description="test", content="test"))
    # print("Prompt 생성 결과 : ", result)
    # print("--------------------------------")
    # result = api.update_prompt(prompt_request_dto=PromptRequestDto(name="test", version="test", description="test", content="test"))
    # print("Prompt 수정 결과 : ", result)
    # print("--------------------------------")
    # result = api.delete_prompt(prompt_id="test")
    # print("Prompt 삭제 결과 : ", result)
    # print("--------------------------------")
    

except Exception as e:
    print("API 호출 실패:", e)
