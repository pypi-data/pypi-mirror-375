import os
from typing import List, Type, Union

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

try:
    from aider.linter import Linter
except ImportError:
    Linter = None

from motleycrew.common.utils import ensure_module_is_installed
from motleycrew.tools import MotleyTool


class PythonLinterTool(MotleyTool):
    """Python code verification tool"""

    def __init__(
        self,
        return_direct: bool = False,
        handle_exceptions: bool | List[Type[Exception]] = False,
    ):
        ensure_module_is_installed("aider")

        langchain_tool = create_python_linter_tool()
        super().__init__(
            tool=langchain_tool,
            return_direct=return_direct,
            handle_exceptions=handle_exceptions,
        )


class PythonLinterInput(BaseModel):
    """Input for the PythonLinterTool."""

    code: str = Field(description="Python code for linting")
    file_name: str = Field(description="file name for the code", default="code.py")


def create_python_linter_tool() -> StructuredTool:
    def lint(code: str, file_name: str = None) -> Union[str, None]:
        # create temp python file
        temp_file_name = file_name or "code.py"
        _, file_ext = os.path.splitext(temp_file_name)
        if file_ext != ".py":
            raise ValueError("The file extension must be .py")

        with open(temp_file_name, "w") as f:
            f.write(code)

        # lint code
        try:
            linter = Linter()
            return linter.lint(temp_file_name)
        except Exception as e:
            return str(e)
        finally:
            os.remove(temp_file_name)

    return StructuredTool.from_function(
        func=lint,
        name="python_linter",
        description="Tool for validating Python code",
        args_schema=PythonLinterInput,
    )
