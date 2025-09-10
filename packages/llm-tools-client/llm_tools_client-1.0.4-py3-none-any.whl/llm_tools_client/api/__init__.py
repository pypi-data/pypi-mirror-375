# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from llm_tools_client.api.category_controller_api import CategoryControllerApi
    from llm_tools_client.api.fewshot_controller_api import FewshotControllerApi
    from llm_tools_client.api.model_controller_api import ModelControllerApi
    from llm_tools_client.api.prompt_controller_api import PromptControllerApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from llm_tools_client.api.category_controller_api import CategoryControllerApi
from llm_tools_client.api.fewshot_controller_api import FewshotControllerApi
from llm_tools_client.api.model_controller_api import ModelControllerApi
from llm_tools_client.api.prompt_controller_api import PromptControllerApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
