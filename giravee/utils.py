from django.db.models import Func
from datetime import datetime
from django.db import models


class Trim(Func):
    function = 'TRIM'
    arity = 1


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

            elif isinstance(field, models.DateField):
                parsed[key] = datetime.strptime(value, "%Y-%m-%d").date() if value else None

            else:
                parsed[key] = value

    return parsed
