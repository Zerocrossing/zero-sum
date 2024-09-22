from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Callable, Dict, List


class Subscribable:
    def __init__(self):
        # Dictionary to store callbacks for each attribute
        self._subscriptions: Dict[str, List[Callable[[Any, Any], None]]] = {}

    def on_change(self, field_reference: Any, callback: Callable[[Any, Any], None]):
        """Register a callback for when a specific field changes."""
        # Resolve the field name from the field reference
        field_name = self._resolve_field_name(field_reference)
        if field_name not in self._subscriptions:
            self._subscriptions[field_name] = []
        self._subscriptions[field_name].append(callback)

    def _resolve_field_name(self, field_reference: Any) -> str:
        """Resolve the field name from a property reference."""
        for field_obj in fields(self): # type: ignore - Not sure why this doesn't work
            if getattr(self, field_obj.name) is field_reference:
                return field_obj.name
        raise ValueError("Field reference not found")

    def _trigger_callbacks(self, field_name: str, old_value: Any, new_value: Any):
        """Trigger all callbacks associated with the field."""
        for callback in self._subscriptions.get(field_name, []):
            callback(old_value, new_value)

    def __setattr__(self, name: str, value: Any):
        # Handle subscriptions only for changes in fields already present in the instance
        if name in self.__dict__:
            old_value = self.__dict__[name]
            if old_value != value:  # Only trigger if the value is actually changing
                super().__setattr__(name, value)
                self._trigger_callbacks(name, old_value, value)
        else:
            super().__setattr__(name, value)


@dataclass
class Config(Subscribable):
    """Configuration class for the zero-sum library.
    
    Contains default settings for the library, which can be modified at runtime.
    Contains a subscribe mixin using `on_change()` which can be used to register
    callbacks for when specific configuration values are changed.
    """
    # LLM settings
    LLM_MODEL: str = "gpt-4o"
    DOCUMENT_CHUK_TOKENS: int = 2500
    FINAL_TOKEN_LIMIT: int = 750
    # LOG SETTINGS
    LOG_LEVEL: str = "WARNING"
    USE_FILE_LOGGING: bool = False
    LOG_PATH: Path = Path("./logs/zero_sum.log")

    def __post_init__(self):
        Subscribable.__init__(self)


config = Config()
