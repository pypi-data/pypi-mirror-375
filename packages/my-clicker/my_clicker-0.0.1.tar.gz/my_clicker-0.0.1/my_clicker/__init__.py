import os
import streamlit.components.v1 as components

_RELEASE = True  # Set True for production

if not _RELEASE:
    _component_func = components.declare_component(
        "my_clicker",
        url="http://localhost:3001",  # Dev server URL
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("my_clicker", path=build_dir)


def my_clicker(name: str, key=None) -> int:
    """Streamlit wrapper for MyComponent.

    Parameters
    ----------
    name: str
        Name to display in the component.
    key: str | None
        Optional Streamlit key.

    Returns
    -------
    int
        Number of times the button has been clicked.
    """
    return _component_func(name=name, key=key, default=0)
