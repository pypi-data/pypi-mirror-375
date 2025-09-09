from pydzn.base_component import BaseComponent


class Sidebar(BaseComponent):
    """
    Minimal sidebar container.
    Spans parent height; default subtle panel bg.
    The layout decides which side shows the divider.
    """

    def __init__(self, *, children: str | None = None, tag: str = "div", dzn: str | None = None, **attrs):
        super().__init__(children=children or "", tag=tag, dzn=dzn, **attrs)

    def context(self) -> dict:
        return {}
