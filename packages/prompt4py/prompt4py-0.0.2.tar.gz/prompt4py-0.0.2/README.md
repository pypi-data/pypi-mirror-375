# *Prompt4Py*

*Programmatic prompt template for Python.*

## Installation

```
pip install -U prompt4py
```

## Quick Start

1. Create a prompt template

    ```python
    from prompt4py import GeneralTemplate

    # Create your prompt template
    prompt_template = GeneralTemplate()
    prompt_template.role = 'An NER machine'
    prompt_template.objective = 'Extract all {{entity_type}} from CONTEXT.'
    prompt_template.instruction = {
        1: 'Think deeply on every entities in CONTEXT',
        2: 'Extract all {{entity_type}}',
        3: 'Output the entities you have extracted'
    }
    prompt_template.constraint = 'Do not include any markdown grams'
    prompt_template.capability = 'Extract entities'
    prompt_template.context = '{{ent_1}}, {{ent_2}}, {{ent_3}}'
    prompt_template.output_dtype = 'str'
    prompt_template.output_format = 'jsonl'
    prompt_template.output_example = str([
        {
            'entity_type': '{{example_entity_type_1}}',
            'entity_text': '{{example_entity_text_1}}'
        }
    ])
    ```

2. Render the template

    ```python
    # Render the template
    prompt = prompt_template.render(entity_type='PERSON', ent_1='John Lennon', ent_2='Joe Biden', ent_3='Charlemagne',
                                    example_entity_type_1='PERSON', example_entity_text_1='Elizabeth')
    print(prompt)
    ```

    the prompt would be rendered like this:

    ```markdown
    ## _TIMESTAMP
    [82159.8475038]
    ## ROLE
    An NER machine
    ## OBJECTIVE
    Extract all PERSON from CONTEXT.
    ## INSTRUCTION
    - **1**: Think deeply on every entities in CONTEXT 
    - **2**: Extract all PERSON 
    - **3**: Output the entities you have extracted 
    ## CONSTRAINT
    Do not include any markdown grams
    ## CAPABILITY
    Extract entities
    ## CONTEXT
    John Lennon, Joe Biden, Charlemagne
    ## OUTPUT_DATATYPE
    str
    ## OUTPUT_FORMAT
    jsonl
    ## OUTPUT_EXAMPLE
    [{'entity_type': 'PERSON', 'entity_text': 'Elizabeth'}]
    ```

3. Invoke a chatbot / causal language model

    You would get response like below:

    ```
    {"entity_type": "PERSON", "entity_text": "John Lennon"}
    {"entity_type": "PERSON", "entity_text": "Joe Biden"}
    {"entity_type": "PERSON", "entity_text": "Charlemagne"}
    ```
