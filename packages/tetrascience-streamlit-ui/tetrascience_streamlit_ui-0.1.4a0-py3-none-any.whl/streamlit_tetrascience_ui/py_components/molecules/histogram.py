from ..utils import declare_component

_component_func = declare_component("histogram_component")


def histogram(name, key=None):
    component_value = _component_func(
        comp="histogram_component", name=name, key=key, default=0
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
