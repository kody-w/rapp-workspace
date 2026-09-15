"""Closed total evaluator: no imports, I/O, callbacks, dynamic code or ambient state."""


def evaluate(operation, value, field):
    if operation == "identity-octets":
        if type(value) is not bytes or len(value) > 65536:
            raise ValueError("finite-octets-required")
        return value
    if operation == "json-field":
        if type(value) is not dict or len(value) > 128 or type(field) is not str:
            raise ValueError("bounded-object-required")
        if field not in value:
            raise ValueError("missing-required-field")
        return value[field]
    raise ValueError("effect-or-unknown-operation-disabled")
