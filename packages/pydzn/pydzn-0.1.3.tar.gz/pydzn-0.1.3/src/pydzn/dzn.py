from __future__ import annotations
import re
from typing import Iterable

# --- tokens (extend as needed) ---
TOKENS = {
    "space": {
        "0": "0",
        "1": ".25rem",  "2": ".5rem",   "3": ".75rem",  "4": "1rem",
        "5": "1.25rem", "6": "1.5rem",  "7": "1.75rem", "8": "2rem",
        "9": "2.25rem", "10": "2.5rem", "11": "2.75rem","12": "3rem",
        "14": "3.5rem", "16": "4rem",   "20": "5rem",   "24": "6rem",
        "28": "7rem",   "32": "8rem"
    },
    "radius": {
        "none": "0", "sm": "8px", "md": "12px", "lg": "16px",
        "xl": "20px", "2xl": "24px", "3xl": "32px", "full": "9999px"
    },
    "shadow": {
        "none": "none",
        "sm":   "0 1px 3px rgba(0,0,0,.08)",
        "md":   "0 2px 6px rgba(0,0,0,.10)",
        "lg":   "0 6px 18px rgba(0,0,0,.12)",
        "xl":   "0 12px 32px rgba(0,0,0,.14)",
        "2xl":  "0 20px 56px rgba(0,0,0,.16)",
        "3xl":  "0 32px 80px rgba(0,0,0,.18)",
        "inner":"inset 0 2px 6px rgba(0,0,0,.12)"
    },
    "border_width": { "0": "0", "DEFAULT": "1px", "2": "2px", "4": "4px", "8": "8px" },
    "border_color": {
        "subtle": "rgba(15,23,42,.06)",
        "transparent": "transparent",
        "black": "rgba(0,0,0,1)",
        "white": "rgba(255,255,255,1)",
        "slate-200": "rgb(226,232,240)",
        "slate-300": "rgb(203,213,225)",
        "slate-400": "rgb(148,163,184)",
        "blue-500": "rgb(59,130,246)",
        "red-500": "rgb(239,68,68)",
        "green-500": "rgb(34,197,94)"
    }
}

# --- responsive breakpoints ---
BPS = {
    "sm": "(min-width: 640px)",
    "md": "(min-width: 768px)",
    "lg": "(min-width: 1024px)",
}

_used: set[str] = set()

def register_dzn_classes(classes: str | Iterable[str]) -> None:
    if isinstance(classes, str):
        _used.update(c for c in classes.split() if c)
    else:
        _used.update(classes)

# --- selector escaping for arbitrary utilities ---
def css_escape_class(cls: str) -> str:
    # Escape any char not [a-zA-Z0-9_-] so the selector matches the literal class in HTML
    return re.sub(r'([^a-zA-Z0-9_-])', r'\\\1', cls)

# --- emit helpers ---
def rule(selector: str, body: str) -> str:
    return f".{selector}{{{body}}}"

def emit_base(name: str) -> str | None:
    match name:
        # layout
        case "flex":            return rule(name, "display:flex")
        case "flex-col":        return rule(name, "flex-direction:column")
        case "items-center":    return rule(name, "align-items:center")
        case "justify-center":  return rule(name, "justify-content:center")
        case "text-center":     return rule(name, "text-align:center")

        # border (longhand for predictable overrides)
        case "border":
            return rule(name,
                f"border-style:solid;"
                f"border-width:{TOKENS['border_width']['DEFAULT']};"
                f"border-color:{TOKENS['border_color']['subtle']}"
            )

        # quick border colors
        case "border-subtle":       return rule(name, f"border-color:{TOKENS['border_color']['subtle']}")
        case "border-transparent":  return rule(name, f"border-color:{TOKENS['border_color']['transparent']}")
        case "border-black":        return rule(name, f"border-color:{TOKENS['border_color']['black']}")
        case "border-white":        return rule(name, f"border-color:{TOKENS['border_color']['white']}")

        # radius
        case "rounded":         return rule(name, "border-radius:12px")
        case "rounded-none":    return rule(name, "border-radius:0")

        # shadows
        case "shadow-none":     return rule(name, f"box-shadow:{TOKENS['shadow']['none']}")
        case "shadow-sm":       return rule(name, f"box-shadow:{TOKENS['shadow']['sm']}")
        case "shadow":          return rule(name, f"box-shadow:{TOKENS['shadow']['md']}")
        case "shadow-md":       return rule(name, f"box-shadow:{TOKENS['shadow']['md']}")
        case "shadow-lg":       return rule(name, f"box-shadow:{TOKENS['shadow']['lg']}")
        case "shadow-xl":       return rule(name, f"box-shadow:{TOKENS['shadow']['xl']}")
        case "shadow-2xl":      return rule(name, f"box-shadow:{TOKENS['shadow']['2xl']}")
        case "shadow-3xl":      return rule(name, f"box-shadow:{TOKENS['shadow']['3xl']}")
        case "shadow-inner":    return rule(name, f"box-shadow:{TOKENS['shadow']['inner']}")

        # visibility
        case "hidden":       return rule(name, "display:none")
        case "block":        return rule(name, "display:block")          # handy for toggling back
        case "inline-block": return rule(name, "display:inline-block")
        case "invisible":    return rule(name, "visibility:hidden")      # keeps layout
        case "visible":      return rule(name, "visibility:visible")

        # positioning
        case "fixed":    return rule(name, "position:fixed")
        case "absolute": return rule(name, "position:absolute")
        case "relative": return rule(name, "position:relative")
        case "top-0":    return rule(name, "top:0")
        case "right-0":  return rule(name, "right:0")
        case "bottom-0": return rule(name, "bottom:0")
        case "left-0":   return rule(name, "left:0")
        case "inset-0":  return rule(name, "top:0;right:0;bottom:0;left:0")

        case "flex-1":   return rule(name, "flex:1 1 0%")
        case "grow":     return rule(name, "flex-grow:1")
        case "shrink-0": return rule(name, "flex-shrink:0")

        case "grid": return rule(name, "display:grid")

        case "border-solid": return rule(name, "border-style:solid")
        case "border-dashed": return rule(name, "border-style:dashed")
        case "border-dotted": return rule(name, "border-style:dotted")

        case "aspect-square": return rule(name, "aspect-ratio:1/1")

    return None

def emit_scale(name: str) -> str | None:
    # spacing
    if m := re.fullmatch(r"gap-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"gap:{val}")
    if m := re.fullmatch(r"p-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding:{val}")
    if m := re.fullmatch(r"px-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-left:{val};padding-right:{val}")
    if m := re.fullmatch(r"py-(\d+)", name):
        if (val := TOKENS["space"].get(m.group(1))) is not None:
            return rule(name, f"padding-top:{val};padding-bottom:{val}")

    # border widths
    if m := re.fullmatch(r"border-(0|2|4|8)", name):
        w = TOKENS["border_width"][m.group(1)]
        return rule(name, f"border-width:{w}")
    if m := re.fullmatch(r"border-(x|y)(?:-(0|2|4|8))?", name):
        axis, wkey = m.group(1), m.group(2) or "DEFAULT"
        w = TOKENS["border_width"][wkey]
        if axis == "x":
            return rule(name, f"border-left-width:{w};border-right-width:{w}")
        else:
            return rule(name, f"border-top-width:{w};border-bottom-width:{w}")
    if m := re.fullmatch(r"border-(t|r|b|l)(?:-(0|2|4|8))?", name):
        side, wkey = m.group(1), m.group(2) or "DEFAULT"
        w = TOKENS["border_width"][wkey]
        prop = {"t":"top","r":"right","b":"bottom","l":"left"}[side]
        return rule(name, f"border-{prop}-width:{w}")

    # border colors by token (e.g., border-slate-300)
    if m := re.fullmatch(r"border-([a-z0-9-]+)", name):
        col = TOKENS["border_color"].get(m.group(1))
        if col is not None:
            return rule(name, f"border-color:{col}")

    # rounded scale
    if m := re.fullmatch(r"rounded-([a-z0-9]+)", name):
        key = m.group(1); val = TOKENS["radius"].get(key)
        if val is not None:
            return rule(name, f"border-radius:{val}")
    if m := re.fullmatch(r"rounded-(t|r|b|l)-([a-z0-9]+)", name):
        side, key = m.group(1), m.group(2)
        val = TOKENS["radius"].get(key)
        if val is None:
            return None
        if side == "t":
            body = f"border-top-left-radius:{val};border-top-right-radius:{val}"
        elif side == "r":
            body = f"border-top-right-radius:{val};border-bottom-right-radius:{val}"
        elif side == "b":
            body = f"border-bottom-right-radius:{val};border-bottom-left-radius:{val}"
        else:
            body = f"border-top-left-radius:{val};border-bottom-left-radius:{val}"
        return rule(name, body)
    if m := re.fullmatch(r"rounded-(tl|tr|br|bl)-([a-z0-9]+)", name):
        corner, key = m.group(1), m.group(2)
        val = TOKENS["radius"].get(key)
        if val is None:
            return None
        prop = {"tl":"top-left","tr":"top-right","br":"bottom-right","bl":"bottom-left"}[corner]
        return rule(name, f"border-{prop}-radius:{val}")

    return None

def emit_arbitrary(name: str) -> str | None:
    esel = css_escape_class(name)

    # width
    if m := re.fullmatch(r"w-\[(.+?)\]", name):
        return rule(esel, f"width:{m.group(1)}")

    # padding
    if m := re.fullmatch(r"p-\[(.+?)\]", name):
        return rule(esel, f"padding:{m.group(1)}")
    if m := re.fullmatch(r"px-\[(.+?)\]", name):
        v = m.group(1); return rule(esel, f"padding-left:{v};padding-right:{v}")
    if m := re.fullmatch(r"py-\[(.+?)\]", name):
        v = m.group(1); return rule(esel, f"padding-top:{v};padding-bottom:{v}")

    # gap
    if m := re.fullmatch(r"gap-\[(.+?)\]", name):
        return rule(esel, f"gap:{m.group(1)}")

    # border width arbitrary
    if m := re.fullmatch(r"border-\[(.+?)\]", name):
        return rule(esel, f"border-width:{m.group(1)}")

    # rounded arbitrary
    if m := re.fullmatch(r"rounded-\[(.+?)\]", name):
        return rule(esel, f"border-radius:{m.group(1)}")

    # shadow arbitrary (underscores become spaces)
    if m := re.fullmatch(r"shadow-\[(.+?)\]", name):
        return rule(esel, f"box-shadow:{m.group(1).replace('_',' ')}")

    # colors
    if m := re.fullmatch(r"bg-\[(.+?)\]", name):
        return rule(esel, f"background:{m.group(1).replace('_',' ')}")
    if m := re.fullmatch(r"text-\[(.+?)\]", name):
        return rule(esel, f"color:{m.group(1).replace('_',' ')}")

    # size
    if m := re.fullmatch(r"h-\[(.+?)\]", name):
        return rule(css_escape_class(name), f"height:{m.group(1)}")

    # grid template columns: grid-cols-[280px_1fr]  (underscores -> spaces)
    if m := re.fullmatch(r"grid-cols-\[(.+?)\]", name):
        v = m.group(1).replace("_", " ")
        return rule(css_escape_class(name), f"grid-template-columns:{v}")

    # grid template rows: grid-rows-[auto_1fr]  (underscores -> spaces)
    if m := re.fullmatch(r"grid-rows-\[(.+?)\]", name):
        v = m.group(1).replace("_", " ")
        return rule(css_escape_class(name), f"grid-template-rows:{v}")

    return None

# --- variants ---
def wrap_variant(sel: str, css: str, variant: str) -> str:
    esel = css_escape_class(sel)
    if variant in BPS:
        return f"@media {BPS[variant]}{{{css}}}"
    if variant == "hover":
        return css.replace(f".{esel}{{", f".{variant}\\:{esel}:hover{{")
    if variant == "focus":
        return css.replace(f".{esel}{{", f".{variant}\\:{esel}:focus{{")
    return css

def emit_one(cls: str) -> str | None:
    parts = cls.split(":")
    base = parts[-1]
    variants = parts[:-1]

    css = emit_base(base) or emit_scale(base) or emit_arbitrary(base)
    if not css:
        return None
    for v in reversed(variants):
        css = wrap_variant(base, css, v)
    return css

def compile_used_css() -> str:
    out: list[str] = []
    for cls in sorted(_used):
        css = emit_one(cls)
        if css:
            out.append(css)
    return "\n".join(out)
