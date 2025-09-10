from llm_tools_client import ApiClient, Configuration
from llm_tools_client.api import ModelControllerApi
from llm_tools_client.models.model_request_dto import ModelRequestDto



# 1. API 서버 설정
config = Configuration(host="http://localhost:8080/llm-tools/v1")
client = ApiClient(config)

# 2. API 객체 생성
api = ModelControllerApi(client)

# 3. API 호출 (예시)
try:
    print("GET 테스트")
    result = api.get_model_list(query="", page=1, size=10)
    print("Model 리스트 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_model_detail(model_id="test")
    print("Model 상세 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_model_type()
    print("Model 타입 리스트 조회 결과 : ", result)
    print("--------------------------------")
    result = api.get_provider()
    print("Provider 리스트 조회 결과 : ", result)
    print("--------------------------------")
    
    # print("POST 테스트")
    # result = api.save_model(model_request_dto=ModelRequestDto(model_name="test", display_name="test", model_type="test", model_description="test", provider="test", deployment_type="test", endpoint="test", identifier="test", api_key="test", endpoint_description="test", languages=["test"], tasks=["test"], license="test", readme="test", model_size="test", quantization=True, user_id="test"))
    # print("Model 생성 결과 : ", result)
    # print("--------------------------------")
    # result = api.update_model(model_request_dto=ModelRequestDto(model_name="test", display_name="test", model_type="test", model_description="test", provider="test", deployment_type="test", endpoint="test", identifier="test", api_key="test", endpoint_description="test", languages=["test"], tasks=["test"], license="test", readme="test", model_size="test", quantization=True, user_id="test"))
    # print("Model 수정 결과 : ", result)
    # print("--------------------------------")
    # result = api.delete_model(model_id="test")
    # print("Model 삭제 결과 : ", result)
    # print("--------------------------------")
    
except Exception as e:
    print("API 호출 실패:", e)
