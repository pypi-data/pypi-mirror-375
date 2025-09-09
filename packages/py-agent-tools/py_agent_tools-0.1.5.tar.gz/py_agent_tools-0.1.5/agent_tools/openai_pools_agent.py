from openai import AsyncOpenAI
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError, UserError
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_tools.agent_base import AgentBase, ModelNameBase
from agent_tools.credential_pool_base import CredentialPoolBase, ModelCredential
from agent_tools.provider_config import AccountCredential
from agent_tools.wechat_alert import agent_exception_handler


class OpenAIPoolsModelName(ModelNameBase):
    GPT_4O = "gpt-4o"
    O4_MINI = "o4-mini"


class OpenAIPoolsAgent(AgentBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_source = getattr(self, "config_source", None)

    def create_client(self) -> AsyncOpenAI:
        if self.credential is None:
            raise ValueError("Credential is not initialized")

        # 准备默认头部
        default_headers = {}

        # 如果指定了config_source，添加X-Config-Source头部
        if self.config_source:
            default_headers["X-Config-Source"] = self.config_source

        return AsyncOpenAI(
            api_key=self.credential.api_key,
            base_url=self.credential.base_url,
            timeout=self.timeout,
            default_headers=default_headers,
        )

    def create_model(self) -> OpenAIModel:
        if self.credential is None:
            raise ValueError("Credential is not initialized")
        client = self.create_client()
        return OpenAIModel(
            model_name=self.credential.model_name,
            provider=OpenAIProvider(openai_client=client),
        )

    def embedding(self, input: str, dimensions: int = 1024):
        raise NotImplementedError("OpenAIPoolsAgent does not support embedding")

    @classmethod
    async def create_with_config_source(
        cls, credential: ModelCredential, model_settings=None, config_source: str = None
    ):
        agent = await cls.create(credential=credential, model_settings=model_settings)
        agent.config_source = config_source
        return agent

    @agent_exception_handler()
    async def validate_credential(self) -> bool:
        "重写"
        agent = self.create_agent()
        try:
            await self.runner.run(agent, 'this is a test, just echo "hello"', stream=False)
            return True
        except (ModelHTTPError, AgentRunError, UserError):
            raise
        except Exception:
            return False


async def validate_fn(credential: ModelCredential) -> bool:
    agent = await OpenAIPoolsAgent.create(credential=credential)
    return await agent.validate_credential()


class OpenAIPoolsCredentialPool(CredentialPoolBase):
    def __init__(
        self,
        model_provider: str,
        target_model: OpenAIPoolsModelName,
        account_credentials: list[AccountCredential],
    ):
        super().__init__(
            model_provider=model_provider,
            target_model=target_model,
            account_credentials=account_credentials,
            validate_fn=validate_fn,
        )


if __name__ == "__main__":
    pass
