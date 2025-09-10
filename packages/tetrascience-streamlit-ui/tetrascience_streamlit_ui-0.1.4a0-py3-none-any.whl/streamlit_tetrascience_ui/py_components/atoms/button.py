from ..utils import declare_component

_component_func = declare_component("button")


def button(label, variant, size, key=None):
    component_value = _component_func(
        comp="button", label=label, variant=variant, size=size, key=key, default=0
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
