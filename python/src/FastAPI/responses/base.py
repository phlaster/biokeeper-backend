from typing import Any, Type
from fastapi import status
from pydantic import BaseModel

class BasicResponse(BaseModel):
    @classmethod
    def generate_response_example(cls) -> dict[str, Any]:
        # Получаем схему модели и извлекаем примеры
        schema = cls.model_json_schema()
        response_example = dict()
        response_example['msg'] = schema['properties']['msg'].get('example'),
        if 'data' in schema['properties'].keys():
            response_example['data'] = schema['properties']['data'].get('example')
        return response_example

class BasicConflictResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_409_CONFLICT

class BasicNotFoundResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_404_NOT_FOUND

class BasicForbiddenResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_403_FORBIDDEN

def generate_examples(*models: Type[BasicResponse]):
    examples = dict()

    for model in models:
        example_data = model.generate_response_example()
        examples[model.__name__] = {
            'summary': example_data['msg'],
            'value': example_data
        }

    return examples

def generate_responses(*models: Type[BasicResponse]):
    responses = dict()
    confilict_models = [model for model in models if model.get_status_code() == status.HTTP_409_CONFLICT]
    not_found_models = [model for model in models if model.get_status_code() == status.HTTP_404_NOT_FOUND]
    forbidden_models = [model for model in models if model.get_status_code() == status.HTTP_403_FORBIDDEN]

    if confilict_models:
        responses['409'] = {
            'description': 'Conflict',
            'content': {
                'application/json': {
                    'examples': generate_examples(*confilict_models)
                }
            }
        }
    
    if not_found_models:
        responses['404'] = {
            'description': 'Not found',
            'content': {
                'application/json': {
                    'examples': generate_examples(*not_found_models)
                }
            }
        }

    if forbidden_models:
        responses['403'] = {
            'description': 'Forbidden',
            'content': {
                'application/json': {
                    'examples': generate_examples(*forbidden_models)
                }
            }
        }

    return responses

