

class MyAvroMessage:
    schema_str = """
                {
                   "namespace": "my.test",
                   "name": "value",
                   "type": "record",
                   "fields" : [ { "name" : "name", "type" : "string" } ]
                }
                """

    def __init__(self, name=None, type=None) -> None:
        super().__init__()
        self.name = name
        self.type = type

    def to_dict(value, ctx):
        """
        Returns a dict representation of a User instance for serialization.
        Args:
            user (User): User instance.
            ctx (SerializationContext): Metadata pertaining to the serialization
                operation.
        Returns:
            dict: Dict populated with user attributes to be serialized.
        """
        # User._address must not be serialized; omit from dict
        return dict(name=value.name, type=value.type)
