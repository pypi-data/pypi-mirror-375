from typing import Callable, Optional, Type, TypeVar

from pydantic import BaseModel

from motleycrew.tools.tool import MotleyTool

T = TypeVar("T", bound=BaseModel)


class StructuredPassthroughTool(MotleyTool):
    """
    A tool that enforces a certain output shape, raising an error if the output is not as expected.
    """

    def __init__(
        self,
        schema: Type[T],
        name: str = "structured_passthrough_tool",
        description: str = "A tool that checks output validity.",
        post_process: Optional[Callable] = None,
        return_direct: bool = True,
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            args_schema=schema,
            return_direct=return_direct,
            **kwargs
        )

        self.schema = schema
        self.post_process = post_process

    def run(self, **kwargs) -> T:
        """
        Run the tool with the provided inputs.
        """
        # Validate the input against the schema
        validated_input = self.schema(**kwargs)

        if self.post_process:
            # Apply the post-processing function if provided
            validated_input = self.post_process(validated_input)

        # Return the validated input
        return validated_input
