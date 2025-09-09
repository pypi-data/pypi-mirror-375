from pydzn.base_component import BaseComponent


class Card(BaseComponent):
    """
    Renders a card element.
    Expects `template.html`
    """

    def __init__(self, children: str | None = None, tag: str = "div", **html_attrs):
        super().__init__(children=children, tag=tag, **html_attrs)


    def context(self) -> dict:
        return {}
