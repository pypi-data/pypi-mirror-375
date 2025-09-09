from pydzn.base_component import BaseComponent
from pydzn.dzn import register_dzn_classes


class NavItem(BaseComponent):
    """
    Minimal sidebar/nav item.
    - No default styling; pass dzn yourself.
    - Put label/content in `children` (e.g., render a Text component).
    - Optional: `active=True` to start active; `group_toggle=True` to clear
      siblings and apply `active_classes` on click (client-only).
    """

    def __init__(
        self,
        *,
        children: str | None = None,
        tag: str = "div",
        dzn: str | None = None,
        active: bool = False,
        active_classes: list[str] | tuple[str, ...] | None = None,
        group_toggle: bool = False,
        **attrs,
    ):
        # No default design; just pass through what caller wants.
        self._active_classes = list(active_classes or [])

        # If we'll toggle classes at runtime, pre-register them so /_dzn.css emits rules.
        if self._active_classes:
            register_dzn_classes(self._active_classes)

        # Start active = append active classes up front
        effective_dzn = (dzn or "")
        if active and self._active_classes:
            effective_dzn = (effective_dzn + " " + " ".join(self._active_classes)).strip()

        # Sensible a11y defaults (still “unstyled”)
        attrs.setdefault("role", "button")
        attrs.setdefault("tabindex", "0")

        # Optional sibling-clearing active toggle, only if requested and not overridden
        if group_toggle and "hx-on:click" not in attrs and self._active_classes:
            # Build JS that removes active classes from siblings, adds to this.
            rm = ",".join(f"'{c}'" for c in self._active_classes)
            add = rm
            attrs["hx-on:click"] = (
                "var p=this.parentElement;"
                f"for(const el of p.children){{el.classList.remove({rm});}}"
                f"this.classList.add({add});"
            )

        super().__init__(children=children or "", tag=tag, dzn=effective_dzn, **attrs)

    def context(self) -> dict:
        # No label here; use children (e.g., a Text component) for content.
        return {}
