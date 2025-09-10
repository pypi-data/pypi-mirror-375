from asyncio import iscoroutinefunction
from functools import wraps
from typing import Optional, Literal
from pydantic import BaseModel
from .exceptions import FieldValidationError


class Alpha:
    """
    Field Alpha Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        mode: Literal['upper', 'lower', 'mixed'] = 'mixed',
        message: Optional[str] = None,
    ):
        """Field Alpha Validation Decorator

        Args:
            field_name (str): Field name that need to be validate.
            mode (Literal["upper", "lower", "mixed"]): Validation mode. Options: 'upper' (only uppercase), 'lower' (only lowercase), 'mixed' (both upper and lower). Defaults to 'mixed'.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.
        """
        self.field_name = field_name
        self.mode = mode
        self.message = message

    def _validate_alpha(self, value: str) -> bool:
        """
        Verify whether the string conforms to the alphabetic pattern requirements.

        Args:
            value (str): The string to be verified.

        Returns:
            bool: Verify whether it has passed.
        """
        if not isinstance(value, str):
            return False

        if not value.isalpha():
            return False

        if self.mode == 'upper':
            return value.isupper()
        elif self.mode == 'lower':
            return value.islower()
        else:  # mixed mode
            return True

    def _get_default_message(self) -> str:
        """
        Obtain the default error message.

        Returns:
            str: Default error message.
        """
        mode_messages = {
            'upper': f'{self.field_name} must contain only uppercase letters.',
            'lower': f'{self.field_name} must contain only lowercase letters.',
            'mixed': f'{self.field_name} must contain only letters.',
        }
        return mode_messages[self.mode]

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if field_value is not None and not self._validate_alpha(field_value):
                        raise FieldValidationError(
                            model_name=validate_model.__class__.__name__,
                            field_name=self.field_name,
                            field_value=field_value,
                            validator=self.__class__.__name__,
                            message=self.message if self.message else self._get_default_message(),
                        )
                return await func(*args, **kwargs)

            return wrapper

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if field_value is not None and not self._validate_alpha(field_value):
                        raise FieldValidationError(
                            model_name=validate_model.__class__.__name__,
                            field_name=self.field_name,
                            field_value=field_value,
                            validator=self.__class__.__name__,
                            message=self.message if self.message else self._get_default_message(),
                        )
                return func(*args, **kwargs)

            return wrapper
