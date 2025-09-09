import json
from copy import deepcopy
from datetime import UTC, date, datetime, time
from itertools import starmap
from typing import Annotated, Any, Callable, Collection, Optional, Type, Union, get_args, get_origin

from pydantic import BaseModel

from youtrack_sdk.entities import Issue, IssueCustomFieldType
from youtrack_sdk.exceptions import YouTrackNotFound


def deep_update(dest: dict, *mappings: dict) -> dict:
    """Recursively updates `dest` with `mappings`.

    Unlike the standard dict union operator, this supports substructures and checks matching value types.
    """
    result = deepcopy(dest)

    for source in mappings:
        for key, value in source.items():
            if (key in result) and (type(result[key]) is not type(value)):
                raise TypeError(
                    f"Destination type '{type(result[key])}' differs from source type '{type(value)}' for key '{key}'",
                )

            if (key in result) and isinstance(value, dict):
                result[key] = deep_update(result[key], value)
            elif (key in result) and isinstance(value, list):
                if len(result[key]) != len(value):
                    raise TypeError(
                        f"Destination list length '{len(result[key])}' differs from "
                        f"source list length '{len(value)}' for key '{key}'",
                    )
                result[key] = list(starmap(deep_update, zip(result[key], value)))
            else:
                result[key] = value

    return result


def model_to_field_names(model: Type[BaseModel] | Union[Type[BaseModel]]) -> Optional[str]:
    """Parses model and returns field names as a comma separated string.

    If a field has an alias, it will be used as a field name. If a field accepts different type(s),
    they will be parsed recursively and found field names combined to remove duplicates.
    Field names from a referenced models will be mentioned as a subset of an original field in parentheses::

        id,name,value(id,period(id,minutes,presentation),description)
    """

    def model_to_fields(m: Type[BaseModel]) -> dict:
        model_schema = m.model_json_schema(ref_template="{model}")
        definitions = model_schema.get("$defs", {})

        def schema_to_fields(schema: dict) -> dict:
            def type_to_fields(field_type: dict) -> dict:
                if "$ref" in field_type:
                    return schema_to_fields(definitions[field_type["$ref"]])
                elif field_type.get("type") == "array":
                    return type_to_fields(field_type["items"])
                elif sub_types := field_type.get("anyOf", field_type.get("allOf", field_type.get("oneOf"))):
                    return deep_update({}, *map(type_to_fields, sub_types))
                else:
                    return {}

            return {name: type_to_fields(value) for name, value in schema["properties"].items()}

        return schema_to_fields(model_schema)

    def fields_to_csv(fields: dict) -> str:
        return ",".join(
            f"{field_name}({field_value})" if (field_value := fields_to_csv(value)) else field_name
            for field_name, value in fields.items()
        )

    # Extract origin type from annotated type
    if get_origin(model) is Annotated:
        model = get_args(model)[0]

    # `get_args` returns a sequence of the types included in the union type
    # or an empty sequence if the `model` is a base type
    models = get_args(model) or (model,)
    fields_dict = deep_update({}, *map(model_to_fields, models))

    return fields_to_csv(fields_dict) or None


def obj_to_dict(obj: Optional[BaseModel]) -> Optional[dict]:
    """
    Converts pydantic model instance to dictionary including nested fields.
    Unset fields or fields without default values will be omitted.
    """
    # `exclude_none=True` on its own is not sufficient, because it should be possible
    # to set a field to None explicitly (e.g. to unassign a ticket).
    # `exclude_unset=True` on its own is not sufficient, because the default value
    # for $type fields should be used to simplify the creation of request objects.
    return obj and deep_update(
        obj.model_dump(by_alias=True, exclude_unset=True),
        obj.model_dump(by_alias=True, exclude_none=True),
    )


class YouTrackTimestampEncoder(json.JSONEncoder):
    def default(self, obj):
        def to_youtrack_timestamp(dt: datetime) -> int:
            return int(dt.timestamp() * 1000)

        match obj:
            case datetime():
                return to_youtrack_timestamp(obj)
            case date():
                return to_youtrack_timestamp(datetime.combine(obj, time(hour=12, tzinfo=UTC)))
            case _:
                return json.JSONEncoder.default(self, obj)


def custom_json_dumps(obj: Any) -> str:
    return json.dumps(obj, cls=YouTrackTimestampEncoder, allow_nan=False)


def obj_to_json(obj: Optional[BaseModel]) -> str:
    return custom_json_dumps(obj_to_dict(obj))


class NonSingleValueError(Exception):
    pass


def get_single_value[T](values: Collection[T]) -> T:
    try:
        (value,) = values
    except ValueError as e:
        raise NonSingleValueError(f"single element expected, found: {values}") from e
    return value


def get_issue_custom_field(issue: Issue, field_name: str) -> IssueCustomFieldType:
    return get_single_value(tuple(filter(lambda field: field.name == field_name, issue.custom_fields)))


def exists(getter: Callable, *args, **kwargs) -> bool:
    try:
        getter(*args, **kwargs)
    except YouTrackNotFound:
        return False
    else:
        return True
