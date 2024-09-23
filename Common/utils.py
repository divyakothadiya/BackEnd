from rest_framework.exceptions import ValidationError
def check_empty_fields(data):
    for field, value in data.items():
        if not str(value):
            raise ValidationError({field: "This field may not be empty."})
        