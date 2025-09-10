from __future__ import annotations

import asyncio
from typing import Any, List, Optional, Sequence, Union

from langchain.agents import AgentExecutor
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.config import merge_configs
from langchain_core.runnables.history import (
    GetSessionHistoryCallable,
    RunnableWithMessageHistory,
)

from motleycrew.agents.mixins import LangchainOutputHandlingAgentMixin
from motleycrew.agents.parent import MotleyAgentParent
from motleycrew.common import MotleyAgentFactory, MotleySupportedTool, logger
from motleycrew.tracking import add_default_callbacks_to_langchain_config


class LangchainMotleyAgent(MotleyAgentParent, LangchainOutputHandlingAgentMixin):
    """MotleyCrew wrapper for Langchain agents."""

    def __init__(
        self,
        description: str | None = None,
        name: str | None = None,
        prompt: str | ChatPromptTemplate | None = None,
        agent_factory: MotleyAgentFactory[AgentExecutor] | None = None,
        tools: Sequence[MotleySupportedTool] | None = None,
        force_output_handler: bool = False,
        chat_history: bool | GetSessionHistoryCallable = True,
        input_as_messages: bool = False,
        runnable_config: RunnableConfig | None = None,
        verbose: bool = False,
    ):
        """
        Args:
            description: Description of the agent.

                Unlike the prompt prefix, it is not included in the prompt.
                The description is only used for describing the agent's purpose
                when giving it as a tool to other agents.

            name: Name of the agent.
                The name is used for identifying the agent when it is given as a tool
                to other agents, as well as for logging purposes.

                It is not included in the agent's prompt.

            prompt: Prompt to the agent.

                If a string, it will be used as a prompt.
                If a string containing f-string-style placeholders, it will be used as a prompt template.
                If a ChatPromptTemplate, it will be used as a prompt template.

            agent_factory: Factory function to create the agent.
                The factory function should accept a dictionary of tools and return
                an AgentExecutor instance.

                See :class:`motleycrew.common.types.MotleyAgentFactory` for more details.

                Alternatively, you can use the :meth:`from_agent` method
                to wrap an existing AgentExecutor.

            tools: Tools to add to the agent.

            force_output_handler: Whether to force the agent to return through an output handler.
                If True, at least one tool must have return_direct set to True.

            chat_history: Whether to use chat history or not.
                If `True`, uses `InMemoryChatMessageHistory`.
                If a callable is passed, it is used to get the chat history by session_id.

                See :class:`langchain_core.runnables.history.RunnableWithMessageHistory`
                for more details.

            input_as_messages: Whether the agent expects a list of messages as input instead of a single string.

            runnable_config: Default Langchain config to use when invoking the agent.
                It can be used to add callbacks, metadata, etc.

            verbose: Whether to log verbose output.
        """
        super().__init__(
            prompt=prompt,
            description=description,
            name=name,
            agent_factory=agent_factory,
            tools=tools,
            force_output_handler=force_output_handler,
            verbose=verbose,
        )

        if chat_history is True:
            chat_history = InMemoryChatMessageHistory()
            self.get_session_history_callable = lambda _: chat_history
        else:
            self.get_session_history_callable = chat_history

        self.input_as_messages = input_as_messages
        self.runnable_config = runnable_config

        self._create_agent_error_tool()

    def materialize(self):
        """Materialize the agent and wrap it in RunnableWithMessageHistory if needed."""
        if self.is_materialized:
            return

        super().materialize()
        assert isinstance(self._agent, AgentExecutor)

        if self.get_output_handlers():
            assert self._agent_error_tool
            self._agent.tools += [self._agent_error_tool]

            object.__setattr__(
                self._agent.agent, "plan", self.agent_plan_decorator(self._agent.agent.plan)
            )
            if hasattr(self._agent.agent, "aplan"):
                object.__setattr__(
                    self._agent.agent, "aplan", self.agent_aplan_decorator(self._agent.agent.aplan)
                )

            object.__setattr__(
                self._agent,
                "_take_next_step",
                self.take_next_step_decorator(self._agent._take_next_step),
            )
            if hasattr(self._agent, "_atake_next_step"):
                object.__setattr__(
                    self._agent,
                    "_atake_next_step",
                    self.take_next_step_decorator(self._agent._atake_next_step),
                )

            for tool in self.agent.tools:
                if tool.return_direct:
                    object.__setattr__(
                        tool,
                        "_run",
                        self._run_tool_direct_decorator(tool._run),
                    )
                    object.__setattr__(
                        tool,
                        "run",
                        self.run_tool_direct_decorator(tool.run),
                    )
                    if hasattr(tool, "_arun"):
                        object.__setattr__(
                            tool,
                            "_arun",
                            self._run_tool_direct_decorator(tool._arun),
                        )
                    if hasattr(tool, "arun"):
                        object.__setattr__(
                            tool,
                            "arun",
                            self.run_tool_direct_decorator(tool.arun),
                        )

        if self.get_session_history_callable:
            logger.info("Wrapping agent in RunnableWithMessageHistory")

            if isinstance(self._agent, RunnableWithMessageHistory):
                return
            self._agent = RunnableWithMessageHistory(
                runnable=self._agent,
                get_session_history=self.get_session_history_callable,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

    def _prepare_config(self, config: RunnableConfig) -> RunnableConfig:
        config = merge_configs(self.runnable_config, config)
        config = add_default_callbacks_to_langchain_config(config)
        if self.get_session_history_callable:
            config["configurable"] = config.get("configurable") or {}
            config["configurable"]["session_id"] = (
                config["configurable"].get("session_id") or "default"
            )
        return config

    def invoke(
        self,
        input: Optional[Union[str, dict, List[BaseMessage]]] = None,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        config = self._prepare_config(config)
        
        # Check if input is already messages - if so, pass them through directly
        if isinstance(input, list) and all(isinstance(m, BaseMessage) for m in input):
            prompt = self._prepare_for_invocation(
                input=input, prompt_as_messages=True
            )
        else:
            prompt = self._prepare_for_invocation(
                input=input, prompt_as_messages=self.input_as_messages
            )

        output = self.agent.invoke({"input": prompt}, config, **kwargs)
        return output.get("output") or output

    async def ainvoke(
        self,
        input: Optional[Union[str, dict, List[BaseMessage]]] = None,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        config = self._prepare_config(config)
        
        # Check if input is already messages - if so, pass them through directly
        if isinstance(input, list) and all(isinstance(m, BaseMessage) for m in input):
            prompt = await asyncio.to_thread(
                self._prepare_for_invocation,
                input=input,
                prompt_as_messages=True,
            )
        else:
            prompt = await asyncio.to_thread(
                self._prepare_for_invocation,
                input=input,
                prompt_as_messages=self.input_as_messages,
            )

        output = await self.agent.ainvoke({"input": prompt}, config, **kwargs)
        return output.get("output") or output

    @staticmethod
    def from_agent(
        agent: AgentExecutor,
        description: str | None = None,
        prompt: str | ChatPromptTemplate | None = None,
        tools: Sequence[MotleySupportedTool] | None = None,
        runnable_config: RunnableConfig | None = None,
        verbose: bool = False,
    ) -> "LangchainMotleyAgent":
        """Create a LangchainMotleyAgent from a :class:`langchain.agents.AgentExecutor` instance.

        Using this method, you can wrap an existing AgentExecutor
        without providing a factory function.

        Args:
            agent: AgentExecutor instance to wrap.

            prompt: Prompt for the agent.

                If a string, it will be used as a prompt.
                If a string containing f-string-style placeholders, it will be used as a prompt template.
                If a ChatPromptTemplate, it will be used as a prompt template.

            description: Description of the agent.

                Unlike the prompt prefix, it is not included in the prompt.
                The description is only used for describing the agent's purpose
                when giving it as a tool to other agents.

            tools: Tools to add to the agent.

            runnable_config: Default Langchain config to use when invoking the agent.
                It can be used to add callbacks, metadata, etc.

            verbose: Whether to log verbose output.
        """
        # TODO: do we really need to unite the tools implicitly like this?
        # TODO: confused users might pass tools both ways at the same time
        # TODO: and we will silently unite them, which can have side effects (e.g. doubled tools)
        # TODO: besides, getting tools can be tricky for other frameworks (e.g. LlamaIndex)
        if tools or agent.tools:
            tools = list(tools or []) + list(agent.tools or [])

        wrapped_agent = LangchainMotleyAgent(
            prompt=prompt,
            description=description,
            tools=tools,
            runnable_config=runnable_config,
            verbose=verbose,
        )
        wrapped_agent._agent = agent
        return wrapped_agent
