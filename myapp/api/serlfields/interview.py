import base64

from rest_framework.serializers import Field


class BinaryField(Field):
    """
    Binary objects are represented in Base64. This field provides proper
    conversions between representations and internal values.
    """

    def to_representation(self, value):
        return base64.b64encode(value)

    def to_internal_value(self, data):
        return base64.b64decode(data)
