from abc import ABCMeta


class RequireHasAttrs(ABCMeta):
    def __new__(cls, name, bases, classdict, required_attrs):
        is_abstract = any(getattr(v, "__isabstractmethod__", None) for v in classdict.values())

        # Check if all required attributes are defined in the class being created
        if not is_abstract:
            missing_attrs = [attr for attr in required_attrs if attr not in classdict]
            if missing_attrs:
                raise TypeError(f"Class '{name}' must define attributes: {missing_attrs}")

        return super().__new__(cls, name, bases, classdict)
