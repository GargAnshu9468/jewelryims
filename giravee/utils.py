from django.db import models


def parse_fields_from_request(data, model_cls):
    valid_fields = {f.name for f in model_cls._meta.fields}
    parsed = {}

    for key, value in data.items():
        if key in valid_fields:
            field = model_cls._meta.get_field(key)

            if isinstance(field, models.IntegerField):
                parsed[key] = int(value) if value else 0

            elif isinstance(field, models.DecimalField):
                parsed[key] = float(value) if value else 0

            elif isinstance(field, models.BooleanField):
                parsed[key] = value.lower() in ['true', '1']

            else:
                parsed[key] = value

    return parsed
