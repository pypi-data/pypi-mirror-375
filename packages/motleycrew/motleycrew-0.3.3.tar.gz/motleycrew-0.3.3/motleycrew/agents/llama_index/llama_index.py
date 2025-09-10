from __future__ import annotations

import asyncio
import uuid
from typing import Any, Optional, Sequence

try:
    from llama_index.core.agent import AgentRunner
    from llama_index.core.agent.types import TaskStep, TaskStepOutput
    from llama_index.core.chat_engine.types import AgentChatResponse, ChatResponseMode
except ImportError:
    AgentRunner = None
    ChatResponseMode = None
    TaskStep = None
    TaskStepOutput = None
    AgentChatResponse = None

from deprecated import deprecated
from langchain_core.runnables import RunnableConfig

from motleycrew.agents.parent import MotleyAgentParent
from motleycrew.common import AuxPrompts, MotleyAgentFactory, MotleySupportedTool
from motleycrew.common.utils import ensure_module_is_installed
from motleycrew.tools import DirectOutput


@deprecated("LlamaIndexMotleyAgent is deprecated and will be removed in the next major release.")
class LlamaIndexMotleyAgent(MotleyAgentParent):
    """MotleyCrew wrapper for LlamaIndex agents."""

    def __init__(
        self,
        prompt: str | None = None,
        description: str | None = None,
        name: str | None = None,
        agent_factory: MotleyAgentFactory[AgentRunner] | None = None,
        tools: Sequence[MotleySupportedTool] | None = None,
        force_output_handler: bool = False,
        verbose: bool = False,
    ):
        """
        Args:
            prompt: Prompt for the agent.

                If a string, it will be used as a prompt.
                If a string containing f-string-style placeholders, it will be used as a prompt template.

            description: Description of the agent.

                Unlike the prompt prefix, it is not included in the prompt.
                The description is only used for describing the agent's purpose
                when giving it as a tool to other agents.

            name: Name of the agent.
                The name is used for identifying the agent when it is given as a tool
                to other agents, as well as for logging purposes.

                It is not included in the agent's prompt.

            agent_factory: Factory function to create the agent.
                The factory function should accept a dictionary of tools and return
                an AgentRunner instance.

                See :class:`motleycrew.common.types.MotleyAgentFactory` for more details.

                Alternatively, you can use the :meth:`from_agent` method
                to wrap an existing AgentRunner.

            tools: Tools to add to the agent.

            force_output_handler: Whether to force the agent to return through an output handler.
                If True, at least one tool must have return_direct set to True.

            output_handler: Output handler for the agent.

            verbose: Whether to log verbose output.
        """
        super().__init__(
            description=description,
            prompt=prompt,
            name=name,
            agent_factory=agent_factory,
            tools=tools,
            force_output_handler=force_output_handler,
            verbose=verbose,
        )

        self.direct_output = None
        self.aux_prompts = AuxPrompts()

    def _propagate_error_step(self, task_id: str, message: str):
        error_step = TaskStep(
            task_id=task_id,
            step_id=str(uuid.uuid4()),
            input=message,
        )

        step_queue = self._agent.state.get_step_queue(task_id)
        step_queue.clear()
        step_queue.extend([error_step])

    def _run_step_decorator(self):
        """Decorator for the ``AgentRunner._run_step`` method that catches DirectOutput exceptions.

        It also blocks plain output and forces the use of the output handler tool if necessary.

        Note that as of now, LlamaIndex agents only allow one tool call per step,
        so we don't need to worry about ambiguous output handler calls.
        """
        ensure_module_is_installed("llama_index")

        output_handlers = self.get_output_handlers()

        def decorator(func):
            def wrapper(
                task_id: str,
                step: Optional[TaskStep] = None,
                input: Optional[str] = None,
                mode: ChatResponseMode = ChatResponseMode.WAIT,
                **kwargs: Any,
            ):

                try:
                    cur_step_output = func(task_id, step, input, mode, **kwargs)
                except DirectOutput as output_exc:
                    self.direct_output = output_exc
                    output = AgentChatResponse(str(output_exc.output))
                    task_step = TaskStep(task_id=task_id, step_id=str(uuid.uuid4()))
                    cur_step_output = TaskStepOutput(
                        output=output, is_last=True, next_steps=[], task_step=task_step
                    )
                    return cur_step_output

                if not output_handlers:
                    return cur_step_output

                if cur_step_output.is_last and self.force_output_handler:
                    cur_step_output.is_last = False
                    self._propagate_error_step(
                        task_id=cur_step_output.task_step.task_id,
                        message=self.aux_prompts.get_direct_output_error_message(
                            output_handlers=output_handlers
                        ),
                    )

                return cur_step_output

            return wrapper

        return decorator

    def materialize(self):
        super(LlamaIndexMotleyAgent, self).materialize()
        self._agent._run_step = self._run_step_decorator()(self._agent._run_step)

    def invoke(
        self,
        input: dict,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        prompt = self._prepare_for_invocation(input=input, prompt_as_messages=False)

        output = self.agent.chat(prompt)

        if self.direct_output is not None:
            return self.direct_output.output

        return output.response

    async def ainvoke(
        self,
        input: dict,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        prompt = await asyncio.to_thread(
            self._prepare_for_invocation, input=input, prompt_as_messages=False
        )

        output = await self.agent.achat(prompt)

        if self.direct_output is not None:
            return self.direct_output.output

        return output.response

    @staticmethod
    def from_agent(
        agent: AgentRunner,
        description: Optional[str] = None,
        prompt: Optional[str] = None,
        tools: Sequence[MotleySupportedTool] | None = None,
        verbose: bool = False,
    ) -> "LlamaIndexMotleyAgent":
        """Create a LlamaIndexMotleyAgent from a :class:`llama_index.core.agent.AgentRunner`
        instance.

        Using this method, you can wrap an existing AgentRunner
        without providing a factory function.

        Args:
            agent: AgentRunner instance to wrap.

            prompt: Prompt for the agent.

                If a string, it will be used as a prompt.
                If a string containing f-string-style placeholders, it will be used as a prompt template.

            description: Description of the agent.

                Unlike the prompt prefix, it is not included in the prompt.
                The description is only used for describing the agent's purpose
                when giving it as a tool to other agents.

            tools: Tools to add to the agent.

            verbose: Whether to log verbose output.
        """
        ensure_module_is_installed("llama_index")
        wrapped_agent = LlamaIndexMotleyAgent(
            description=description, prompt=prompt, tools=tools, verbose=verbose
        )
        wrapped_agent._agent = agent
        return wrapped_agent
