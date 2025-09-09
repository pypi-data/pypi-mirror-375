from src.base_component import BaseComponent

class Button(BaseComponent):
    """
    Renders a button element.
    Expects `template.html`
    """

    DEFAULT_DZN = (
        "px-5 py-2 rounded-sm border-2 border-blue-500 "
        "shadow-sm hover:shadow-md bg-[transparent] text-[#2563eb] "
    )

    def __init__(self, text: str = "", children: str | None = None,
                 tag: str = "button", dzn: str | None = None, **attrs):
        # 2) Accept dzn both as a named arg and as a stray attribute (attrs["dzn"])
        user_dzn = dzn or attrs.pop("dzn", None)

        # 3) Merge: default + user-provided (so user can extend the default easily)
        effective_dzn = (self.DEFAULT_DZN + " " + user_dzn).strip() if user_dzn else self.DEFAULT_DZN

        # 4) Pass the merged dzn to BaseComponent (it will register + merge into class)
        super().__init__(children=children, tag=tag, dzn=effective_dzn, **attrs)
        self.text = text

    def context(self) -> dict:
        return {"text": self.text}
