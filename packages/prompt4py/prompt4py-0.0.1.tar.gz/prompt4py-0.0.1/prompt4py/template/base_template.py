from abc import abstractmethod
from typing_extensions import Any


class BaseTemplate:
    def __init__(self):
        super().__init__()
        self._context: Any = ''
        self._role: Any = ''
        self._instruction: Any = ''
        self._objective: Any = ''
        self._capability: Any = ''
        self._constraint: Any = ''
        self._output_dtype: Any = ''
        self._output_format: Any = ''
        self._output_example: Any = ''
        self._output_language: Any = ''

    @abstractmethod
    def render(self, parse_markdown: bool) -> str: ...

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value: Any):
        self._context = value

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value: Any):
        self._role = value

    @property
    def instruction(self):
        return self._instruction

    @instruction.setter
    def instruction(self, value: Any):
        self._instruction = value

    @property
    def objective(self):
        return self._objective

    @objective.setter
    def objective(self, value: Any):
        self._objective = value

    @property
    def capability(self):
        return self._capability

    @capability.setter
    def capability(self, value: Any):
        self._capability = value

    @property
    def constraint(self):
        return self._constraint

    @constraint.setter
    def constraint(self, value: Any):
        self._constraint = value

    @property
    def output_dtype(self):
        return self._output_dtype

    @output_dtype.setter
    def output_dtype(self, value: Any):
        self._output_dtype = value

    @property
    def output_format(self):
        return self._output_format

    @output_format.setter
    def output_format(self, value: Any):
        self._output_format = value

    @property
    def output_example(self):
        return self._output_example

    @output_example.setter
    def output_example(self, value: Any):
        self._output_example = value

    @property
    def output_language(self):
        return self._output_language

    @output_language.setter
    def output_language(self, value: Any):
        self._output_language = value
