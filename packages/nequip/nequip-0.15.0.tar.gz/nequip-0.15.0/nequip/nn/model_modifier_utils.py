# This file is a part of the `nequip` package. Please see LICENSE and README at the root for information on using it.
import torch
from typing import Final, Callable, Optional, List


# NOTE: persistent modifiers are modifiers that fundamentally change the behavior of the model (same input will lead to different outputs)
# non-persistent modifiers generally refer to accelerations that should preserve similar model behavior, with the only difference being speed
_MODEL_MODIFIER_PERSISTENT_ATTR_NAME: Final[str] = (
    "_nequip_model_modifier_is_persistent"
)
_MODEL_MODIFIER_PRIVATE_ATTR_NAME: Final[str] = "_nequip_model_modifier_is_private"

# these latter two attributes (unsupported devices and supported compile modes) are meant for acceleration modifiers
_MODEL_MODIFIER_UNSUPPORTED_DEVICES_ATTR_NAME: Final[str] = (
    "_nequip_model_modifier_unsupported_devices"
)
_MODEL_MODIFIER_SUPPORTED_COMPILE_MODES_ATTR_NAME: Final[str] = (
    "_nequip_model_modifier_supported_compile_modes"
)


def model_modifier(
    persistent: bool,
    private: Optional[bool] = None,
    unsupported_devices: List[str] = [],
    supported_compile_modes: Optional[List[str]] = None,
):
    """
    Mark a ``@classmethod`` of an ``nn.Module`` as a "model modifier" that can be applied by the user to modify a packaged or other loaded model on-the-fly. Model modifiers must be a ``@classmethod`` of one of the ``nn.Module`` objects in the model.

    Args:
        persistent (bool): Whether the modifier should be applied when building the model for packaging.
        private (bool, optional): Whether the modifier is private and should not be exposed in public interfaces. Defaults to None.
        unsupported_devices (List[str], optional): List of device types that this modifier does not support. Defaults to [].
        supported_compile_modes (List[str], optional): List of compile modes that this modifier supports. Defaults to None.
    """

    def decorator(func):
        assert isinstance(func, classmethod), (
            "@model_modifier must be applied after @classmethod"
        )
        assert not hasattr(func.__func__, _MODEL_MODIFIER_PERSISTENT_ATTR_NAME)

        setattr(func.__func__, _MODEL_MODIFIER_PERSISTENT_ATTR_NAME, persistent)

        if private is not None:
            setattr(func.__func__, _MODEL_MODIFIER_PRIVATE_ATTR_NAME, private)

        setattr(
            func.__func__,
            _MODEL_MODIFIER_UNSUPPORTED_DEVICES_ATTR_NAME,
            unsupported_devices,
        )

        setattr(
            func.__func__,
            _MODEL_MODIFIER_SUPPORTED_COMPILE_MODES_ATTR_NAME,
            supported_compile_modes,
        )

        return func

    return decorator


def is_model_modifier(func: callable) -> bool:
    # for backwards compatibility, we use the "persistent" flag as a marker for whether the method is a model modifier
    return hasattr(func, _MODEL_MODIFIER_PERSISTENT_ATTR_NAME)


def is_persistent_model_modifier(func: callable) -> bool:
    return getattr(func, _MODEL_MODIFIER_PERSISTENT_ATTR_NAME)


def is_private_model_modifier(func: callable) -> Optional[bool]:
    # for backwards compatibility of packaged models whose modifier would not have this metadata entry,
    # we just default to making it public for convenience of clients
    # should be ok since this mechanism is not safety critical and more just a convenience for documenting modifiers
    return getattr(func, _MODEL_MODIFIER_PRIVATE_ATTR_NAME, False)


def get_model_modifier_unsupported_devices(func: callable) -> List[str]:
    """Get the list of unsupported devices for a model modifier. Returns empty list for backwards compatibility."""
    return getattr(func, _MODEL_MODIFIER_UNSUPPORTED_DEVICES_ATTR_NAME, [])


def get_model_modifier_supported_compile_modes(func: callable) -> Optional[List[str]]:
    """Get the list of supported compile modes for a model modifier. Returns None if not set."""
    return getattr(func, _MODEL_MODIFIER_SUPPORTED_COMPILE_MODES_ATTR_NAME, None)


def replace_submodules(
    model: torch.nn.Module,
    target_cls: type,
    factory: Callable[[torch.nn.Module], torch.nn.Module],
) -> torch.nn.Module:
    """
    Recursively walk the children of ``model``, and whenever we see an instance of ``target_cls``, replace it (in-place) with ``factory(old_module)`` by mutating ``model._modules[name]``.
    """
    for name, child in list(model.named_children()):
        if isinstance(child, target_cls):
            # build a brand-new one based on `factory`
            model._modules[name] = factory(child)
        else:
            # recurse down
            replace_submodules(child, target_cls, factory)
    return model
