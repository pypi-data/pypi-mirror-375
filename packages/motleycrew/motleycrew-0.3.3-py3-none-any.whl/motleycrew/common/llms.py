"""Helper functions to initialize Language Models (LLMs) from different frameworks."""

from typing import Optional

from motleycrew.common import Defaults, LLMFramework, LLMProvider
from motleycrew.common.exceptions import LLMProviderNotSupported
from motleycrew.common.utils import ensure_module_is_installed


def langchain_openai_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an OpenAI LLM client for use with Langchain.

    Args:
        llm_name: Name of the LLM in OpenAI API.
    """
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=llm_name, **kwargs)


def llama_index_openai_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an OpenAI LLM client for use with LlamaIndex.

    Args:
        llm_name: Name of the LLM in OpenAI API.
    """

    ensure_module_is_installed("llama_index")
    from llama_index.llms.openai import OpenAI

    return OpenAI(model=llm_name, **kwargs)


def langchain_anthropic_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an Anthropic LLM client for use with Langchain.

    Args:
        llm_name: Name of the LLM in Anthropic API.
    """

    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=llm_name, **kwargs)


def llama_index_anthropic_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an Anthropic LLM client for use with LlamaIndex.

    Args:
        llm_name: Name of the LLM in Anthropic API.
    """
    ensure_module_is_installed("llama_index")
    from llama_index.llms.anthropic import Anthropic

    return Anthropic(model=llm_name, **kwargs)


def langchain_replicate_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize a Replicate LLM client for use with Langchain.

    Args:
        llm_name: Name of the LLM in Replicate API.
    """
    from langchain_community.llms import Replicate

    model_kwargs = kwargs.pop("model_kwargs", {})
    return Replicate(model=llm_name, model_kwargs=model_kwargs, **kwargs)


def llama_index_replicate_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize a Replicate LLM client for use with LlamaIndex.

    Args:
        llm_name: Name of the LLM in Replicate API.
    """
    ensure_module_is_installed("llama_index")
    from llama_index.llms.replicate import Replicate

    return Replicate(model=llm_name, **kwargs)


def langchain_together_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize a Together LLM client for use with Langchain.

    Args:
        llm_name: Name of the LLM in Together API.
    """
    from langchain_together import ChatTogether

    return ChatTogether(model=llm_name, **kwargs)


def llama_index_together_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize a Together LLM client for use with LlamaIndex.

    Args:
        llm_name: Name of the LLM in Together API.
    """
    ensure_module_is_installed("llama_index")
    from llama_index.llms.together import TogetherLLM

    return TogetherLLM(model=llm_name, **kwargs)


def langchain_groq_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize a Groq LLM client for use with Langchain.

    Args:
        llm_name: Name of the LLM in Groq API.
    """
    from langchain_groq import ChatGroq

    return ChatGroq(model=llm_name, **kwargs)


def llama_index_groq_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize a Groq LLM client for use with LlamaIndex.

    Args:
        llm_name: Name of the LLM in Groq API.
    """
    ensure_module_is_installed("llama_index")
    from llama_index.llms.groq import Groq

    return Groq(model=llm_name, **kwargs)


def langchain_ollama_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an Ollama LLM client for use with Langchain.

    Args:
        llm_name: Name of the LLM in Ollama API.
    """
    from langchain_ollama.chat_models import ChatOllama

    return ChatOllama(model=llm_name, **kwargs)


def llama_index_ollama_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an Ollama LLM client for use with LlamaIndex.

    Args:
        llm_name: Name of the LLM in Ollama API.
    """
    ensure_module_is_installed("llama_index")
    from llama_index.llms.ollama import Ollama

    return Ollama(model=llm_name, **kwargs)


def langchain_azure_openai_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an Azure OpenAI LLM client for use with Langchain.

    Args:
        llm_name: Name of the LLM in Azure OpenAI API.
    """
    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(model=llm_name, **kwargs)


def llama_index_azure_openai_llm(
    llm_name: str = Defaults.DEFAULT_LLM_NAME,
    **kwargs,
):
    """Initialize an Azure OpenAI LLM client for use with LlamaIndex.

    Args:
        llm_name: Name of the LLM in Azure OpenAI API.
    """
    ensure_module_is_installed("llama_index")
    from llama_index.llms.azure_openai import AzureOpenAI

    if "azure_deployment" in kwargs:
        kwargs["engine"] = kwargs.pop("azure_deployment")

    if "engine" not in kwargs:
        raise ValueError(
            "For using Azure OpenAI with LlamaIndex, you must specify an engine/deployment name."
        )

    return AzureOpenAI(model=llm_name, **kwargs)


LLM_MAP = {
    (LLMFramework.LANGCHAIN, LLMProvider.OPENAI): langchain_openai_llm,
    (LLMFramework.LLAMA_INDEX, LLMProvider.OPENAI): llama_index_openai_llm,
    (LLMFramework.LANGCHAIN, LLMProvider.ANTHROPIC): langchain_anthropic_llm,
    (LLMFramework.LLAMA_INDEX, LLMProvider.ANTHROPIC): llama_index_anthropic_llm,
    (LLMFramework.LANGCHAIN, LLMProvider.REPLICATE): langchain_replicate_llm,
    (LLMFramework.LLAMA_INDEX, LLMProvider.REPLICATE): llama_index_replicate_llm,
    (LLMFramework.LANGCHAIN, LLMProvider.TOGETHER): langchain_together_llm,
    (LLMFramework.LLAMA_INDEX, LLMProvider.TOGETHER): llama_index_together_llm,
    (LLMFramework.LANGCHAIN, LLMProvider.GROQ): langchain_groq_llm,
    (LLMFramework.LLAMA_INDEX, LLMProvider.GROQ): llama_index_groq_llm,
    (LLMFramework.LANGCHAIN, LLMProvider.OLLAMA): langchain_ollama_llm,
    (LLMFramework.LLAMA_INDEX, LLMProvider.OLLAMA): llama_index_ollama_llm,
    (LLMFramework.LANGCHAIN, LLMProvider.AZURE_OPENAI): langchain_azure_openai_llm,
    (LLMFramework.LLAMA_INDEX, LLMProvider.AZURE_OPENAI): llama_index_azure_openai_llm,
}


def init_llm(
    llm_framework: str,
    llm_provider: Optional[str] = None,
    llm_name: Optional[str] = None,
    **kwargs,
):
    """Initialize an LLM client for use with the specified framework and family.

    Args:
        llm_framework: Framework of the LLM client.
        llm_provider: Provider of the LLM.
        llm_name: Name of the LLM.
    """
    llm_provider = llm_provider or Defaults.DEFAULT_LLM_PROVIDER
    llm_name = llm_name or Defaults.DEFAULT_LLM_NAME

    func = LLM_MAP.get((llm_framework, llm_provider), None)
    if func is not None:
        return func(llm_name=llm_name, **kwargs)

    raise LLMProviderNotSupported(llm_framework=llm_framework, llm_provider=llm_provider)
