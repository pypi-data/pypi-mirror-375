import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, StructuredTool

from motleycrew.common import AuxPrompts
from motleycrew.tools import DirectOutput, MotleyTool


class LangchainOutputHandlingAgentMixin:
    """A mixin for Langchain-based agents that support output handlers."""

    _agent_error_tool: Optional[BaseTool] = None
    get_output_handlers: Callable[[], List[MotleyTool]] = None
    force_output_handler: bool = False
    aux_prompts: AuxPrompts = AuxPrompts()

    def _create_agent_error_tool(self) -> BaseTool:
        """Create a tool that will force the agent to retry if it attempts to return the output
        bypassing tools.
        """

        def return_error_message(message: str, error_message: str) -> str:
            return error_message

        self._agent_error_tool = StructuredTool.from_function(
            name="agent_error_tool",
            description="",
            func=return_error_message,
        )

    def _create_error_action(self, message: str, error_message: str) -> AgentAction:
        return AgentAction(
            tool=self._agent_error_tool.name,
            tool_input={
                "message": message,
                "error_message": error_message,
            },
            log=f"\nError in agent behavior, forcing retry: {error_message}\n",
        )

    def _is_error_action(self, action: AgentAction) -> bool:
        """Checks whether the action of the agent error tool"""
        return bool(isinstance(action, AgentAction) and action.tool == self._agent_error_tool.name)

    def agent_plan_decorator(self, func: Callable):
        """Decorator for Agent.plan() method that intercepts AgentFinish events"""

        output_handlers = self.get_output_handlers()
        output_handler_names = set(handler.name for handler in output_handlers)

        def wrapper(
            intermediate_steps: List[Tuple[AgentAction, str]],
            callbacks: "Callbacks" = None,
            **kwargs: Any,
        ) -> Union[AgentAction, AgentFinish]:
            additional_notes = []

            to_remove_steps = []
            for intermediate_step in intermediate_steps:
                action, action_output = intermediate_step
                if self._is_error_action(action):
                    # Add the interaction telling the LLM that it errored
                    additional_notes.append(("ai", action.tool_input["message"]))
                    additional_notes.append(("system", action_output))
                    to_remove_steps.append(intermediate_step)

            for to_remove_step in to_remove_steps:
                intermediate_steps.remove(to_remove_step)

            if additional_notes:
                kwargs["additional_notes"] = additional_notes

            step = func(intermediate_steps, callbacks, **kwargs)

            if isinstance(step, AgentAction):
                step = [step]

            if output_handlers:
                if isinstance(step, AgentFinish):
                    if self.force_output_handler:
                        # Attempted to return output directly, blocking
                        return self._create_error_action(
                            message=step.log,
                            error_message=self.aux_prompts.get_direct_output_error_message(
                                output_handlers
                            ),
                        )
                    else:
                        return step
                try:
                    step = list(step)
                except TypeError:
                    return step  # Not an iterable, so we can't check for output handlers

                if len(step) <= 1:
                    return step  # At most one action in the step

                # Check whether there is at least one output handler in the step
                for action in step:
                    if action.tool in output_handler_names:
                        # Attempted to call multiple output handlers or included other tool calls, blocking
                        return self._create_error_action(
                            message=step.log,
                            error_message=self.aux_prompts.get_ambiguous_output_handler_call_error_message(
                                current_output_handler=action.tool, output_handlers=output_handlers
                            ),
                        )
            return step

        return wrapper

    def agent_aplan_decorator(self, func: Callable):
        """Decorator for Agent.aplan() method that intercepts AgentFinish events"""

        output_handlers = self.get_output_handlers()
        output_handler_names = set(handler.name for handler in output_handlers)

        async def wrapper(
            intermediate_steps: List[Tuple[AgentAction, str]],
            callbacks: "Callbacks" = None,
            **kwargs: Any,
        ) -> Union[AgentAction, AgentFinish]:
            additional_notes = []

            to_remove_steps = []
            for intermediate_step in intermediate_steps:
                action, action_output = intermediate_step
                if self._is_error_action(action):
                    additional_notes.append(("ai", action.tool_input["message"]))
                    additional_notes.append(("system", action_output))
                    to_remove_steps.append(intermediate_step)

            for to_remove_step in to_remove_steps:
                intermediate_steps.remove(to_remove_step)

            if additional_notes:
                kwargs["additional_notes"] = additional_notes

            step = await func(intermediate_steps, callbacks, **kwargs)

            if isinstance(step, AgentAction):
                step = [step]

            if output_handlers:
                if isinstance(step, AgentFinish) and self.force_output_handler:
                    return self._create_error_action(
                        message=step.log,
                        error_message=self.aux_prompts.get_direct_output_error_message(
                            output_handlers
                        ),
                    )
                try:
                    step = list(step)
                except TypeError:
                    return step

                if len(step) <= 1:
                    return step

                for action in step:
                    if action.tool in output_handler_names:
                        return self._create_error_action(
                            message=step.log,
                            error_message=self.aux_prompts.get_ambiguous_output_handler_call_error_message(
                                current_output_handler=action.tool, output_handlers=output_handlers
                            ),
                        )
            return step

        return wrapper

    def take_next_step_decorator(self, func: Callable):
        """
        Decorator for ``AgentExecutor._take_next_step()`` and ``AgentExecutor._atake_next_step()`` methods
        that catches DirectOutput exceptions.
        """

        async def async_wrapper(
            name_to_tool_map: Dict[str, BaseTool],
            color_mapping: Dict[str, str],
            inputs: Dict[str, str],
            intermediate_steps: List[Tuple[AgentAction, str]],
            run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
        ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:
            try:
                step = await func(
                    name_to_tool_map, color_mapping, inputs, intermediate_steps, run_manager
                )
            except DirectOutput as direct_ex:
                message = str(direct_ex.output)
                return AgentFinish(
                    return_values={"output": direct_ex.output},
                    messages=[AIMessage(content=message)],
                    log=message,
                )
            return step

        def sync_wrapper(
            name_to_tool_map: Dict[str, BaseTool],
            color_mapping: Dict[str, str],
            inputs: Dict[str, str],
            intermediate_steps: List[Tuple[AgentAction, str]],
            run_manager: Optional[CallbackManagerForChainRun] = None,
        ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:
            try:
                step = func(
                    name_to_tool_map, color_mapping, inputs, intermediate_steps, run_manager
                )
            except DirectOutput as direct_ex:
                message = str(direct_ex.output)
                return AgentFinish(
                    return_values={"output": direct_ex.output},
                    messages=[AIMessage(content=message)],
                    log=message,
                )
            return step

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    def _run_tool_direct_decorator(self, func: Callable):
        """Decorator of the tool's _run and _arun methods, for intercepting a DirectOutput exception"""

        async def async_wrapper(*args, config: RunnableConfig, **kwargs):
            try:
                result = await func(*args, **kwargs, config=config)
            except DirectOutput as direct_exc:
                return direct_exc
            return result

        def sync_wrapper(*args, config: RunnableConfig, **kwargs):
            try:
                result = func(*args, **kwargs, config=config)
            except DirectOutput as direct_exc:
                return direct_exc
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    def run_tool_direct_decorator(self, func: Callable):
        """Decorator of the tool's run and arun methods, for intercepting a DirectOutput exception"""

        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if isinstance(result, DirectOutput):
                raise result
            return result

        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, DirectOutput):
                raise result
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
