import json
import re
import time

from prompt4py.template.base_template import BaseTemplate
from prompt4py.util.json2markdown import json_to_markdown, json_replace

_VAR_LEFT = '{{'
_VAR_RIGHT = '}}'
_VAR_PATTERN = re.compile(r'{{(\w+)}}')


class GeneralTemplate(BaseTemplate):
    def __init__(self):
        super().__init__()

    def render(self, markdown: bool = True, **kwargs) -> str:
        _prompt_object = {
            '_timestamp'.upper(): f'[{time.perf_counter()}]',
            'role'.upper(): self.role,
            'objective'.upper(): self.objective,
            'instruction'.upper(): self.instruction,
            'constraint'.upper(): self.constraint,
            'capability'.upper(): self.capability,
            'context'.upper(): self.context,
            'output_language'.upper(): self.output_language,
            'output_datatype'.upper(): self.output_dtype,
            'output_format'.upper(): self.output_format,
            'output_example'.upper(): self.output_example
        }
        for k in list(_prompt_object.keys()):
            if len(str(_prompt_object[k])) < 1:
                del _prompt_object[k]
        for k, v in kwargs.items():
            if not isinstance(k, str):
                k = str(k)
            if not isinstance(v, str):
                v = str(v)
            _prompt_object = json_replace(_prompt_object, f'{_VAR_LEFT}{k}{_VAR_RIGHT}', v)
        json_str = json.dumps(_prompt_object, ensure_ascii=False)
        _vars_left_to_fill = _VAR_PATTERN.findall(json_str)
        if len(_vars_left_to_fill) > 0:
            _vars_str = ', '.join([f'"{_}"' for _ in _vars_left_to_fill])
            raise TypeError(f'render() missing {len(_vars_left_to_fill)} required arguments: {_vars_str}')
        if markdown:
            return json_to_markdown(json_data=_prompt_object)
        return json_str
