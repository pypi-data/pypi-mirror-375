from pydzn.base_component import BaseComponent


class Text(BaseComponent):
    """
    Renders a text element.
    Expects `template.html`
    """

    def __init__(self, text: str = "", children: str | None = None, tag: str = "div", **html_attrs):
        super().__init__(children=children, tag=tag, **html_attrs)
        self.text = text

    def context(self) -> dict:
        return {"text": self.text}
