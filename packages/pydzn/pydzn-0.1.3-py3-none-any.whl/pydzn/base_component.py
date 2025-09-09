from abc import ABC, abstractmethod
import secrets
import re
import html as _html
import json
import inspect
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .dzn import register_dzn_classes


class BaseComponent(ABC):
    """
    Abstract base for file-based HTML components using Jinja2.

    Each component subclass must:
      1. Reside alongside a `template.html` file (or override `template_name`).
      2. Implement the `context()` method to supply template variables.

    The constructor now accepts optional HTML attributes that get rendered
    into the top-level tag under the variable `attrs`.
    """
    template_name: str = "template.html"
    _asset_candidates = ("styles.css", "component.js")

    def __init__(
        self,
        children: str | None = None,
        tag: str = "div",
        id: str | None = None,
        styles: dict | None = None,
        dzn: str | None = None,
        **html_attrs,
    ):
        # Content & basic props
        self.children = children or ""
        self.tag = tag
        self.html_attrs = html_attrs or {}
        self.styles = dict(styles or {})
        self.error_status = None

        # merge dzn utility classes into class attr + register them
        if dzn:
            self.html_attrs["class"] = self._merge_classes(self.html_attrs.get("class", ""), dzn)
            register_dzn_classes(dzn)

        # Locate component dir/name
        module_path = inspect.getfile(self.__class__)
        base_dir = Path(module_path).resolve().parent
        self.component_dir: Path = base_dir
        self.component_name: str = base_dir.name

        # Decide on id: explicit arg > html_attrs["id"] > generated
        provided_id = id or self.html_attrs.get("id")
        final_id = provided_id or self._gen_id(prefix=self.component_name)
        self.html_attrs["id"] = str(final_id)
        self.id = self.html_attrs["id"]

        # Discover adjacent assets
        discovered = [fname for fname in self._asset_candidates
                    if (self.component_dir / fname).exists()]
        self.assets: list[str] = discovered

        # Jinja env
        self.env = Environment(
            loader=FileSystemLoader(str(base_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _update_error_status(self, error_body: dict, error_status_code: int):
        self.error_status = (
            json.dumps(error_body),
            error_status_code,
            {
                "Content-Type": "application/json",
                "HX-Trigger": json.dumps(
                    {"showMessage": error_body["message"]
                   })
            })
        return self.error_status

    def set_style(self, key: str, value) -> None:
        """Set/override a single CSS property. Pass None/False to remove it."""
        k = key.replace("_", "-")             # allow background_color → background-color
        if value in (None, False):
            self.styles.pop(k, None)
        else:
            self.styles[k] = str(value)

    def _style_string(self) -> str:
        """Merge any existing 'style' attr with styles dict; return final string or ''."""
        parts = []
        inline = self.html_attrs.get("style")
        if inline:
            parts.append(str(inline).rstrip().rstrip(";"))
        if self.styles:
            dict_str = "; ".join(f"{k}: {v}" for k, v in self.styles.items())
            if dict_str:
                parts.append(dict_str)
        return "; ".join(parts) if parts else ""

    def _merge_classes(self, base: str, extra: str) -> str:
        seen, out = set(), []
        for c in (base.split() + extra.split()):
            if c and c not in seen:
                seen.add(c); out.append(c)
        return " ".join(out)

    def _gen_id(self, prefix: str | None = None) -> str:
        """Generate a short, readable, unique-ish id."""
        # sanitize prefix to valid id-ish token
        base = re.sub(r"[^a-zA-Z0-9_-]+", "-", (prefix or "x"))
        token = secrets.token_hex(4)  # 8 hex chars
        return f"{base}-{token}"

    @abstractmethod
    def context(self) -> dict:
        """
        Return dict of template variables for rendering.
        """
        pass

    def render(self) -> str:
        """
        Render `template_name` with the provided context,
        injecting any HTML attributes into the variable `attrs`.
        Templates should use `{{ attrs|safe }}` on their top-level tag.
        """
        # Build attribute string
        attr_parts = []
        for k, v in self.html_attrs.items():
            if k == "style":
                continue
            attr_parts.append(f'{k}="{_html.escape(str(v), quote=True)}"')

        # Merge style attr + styles dict; only add if non-empty
        style_str = self._style_string()
        if style_str:
            attr_parts.append(f'style="{_html.escape(style_str, quote=True)}"')

        attrs = " ".join(attr_parts)

        # Context
        ctx = self.context().copy()
        ctx["attrs"] = attrs
        ctx["children"] = self.children
        ctx["tag"] = self.tag

        tpl = self.env.get_template(self.template_name)
        return tpl.render(**ctx)
