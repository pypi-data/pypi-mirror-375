from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple
import html
from src.dzn import register_dzn_classes


CSSVal = Union[int, str]


def _css_px(v: CSSVal) -> str:
    if isinstance(v, int):
        return f"{v}px"
    return str(v)

def _join_tokens(parts: List[str]) -> str:
    # DZN arbitrary classes use "_" instead of spaces inside [...]
    return "_".join(p.replace(" ", "_") for p in parts)

def _grid_cols_class(named_cols: List[Tuple[str, str]]) -> str:
    return f"grid-cols-[{_join_tokens([w for _, w in named_cols])}]"

def _grid_rows_class(named_rows: List[Tuple[str, str]]) -> str:
    return f"grid-rows-[{_join_tokens([h for _, h in named_rows])}]"

@dataclass
class _Region:
    name: str
    col_name: str
    row_name: Optional[str]           # if None, will resolve to first row
    col_span: int = 1
    row_span: Optional[int] = 1       # if None => span all rows
    dzn: str = ""

    # placement resolved at build-time (indexes)
    _col_index: int = 1
    _row_index: int = 1
    _row_span_resolved: int = 1

    def placement_style(self) -> str:
        gc = f"{self._col_index} / span {self.col_span}"
        gr = f"{self._row_index} / span {self._row_span_resolved}"
        return f"grid-column:{gc};grid-row:{gr};"

class GridLayoutBuilder:
    """
    Intuitive rows/columns named builder.

    You define tracks by NAME (order preserved), then drop regions by name:

        DashboardLayout = (
            layout_builder()
              .columns(sidebar=280, main="1fr")
              .rows(hero="auto", content="1fr")
              .region("sidebar", col="sidebar", row=None, row_span=None)   # spans all rows
              .region("hero",    col="main",    row="hero")
              .region("content", col="main",    row="content")
              .build(name="DashboardLayout")
        )

    Then use on any page:

        html = DashboardLayout(debug=True).render(
            sidebar=sidebar_html,
            hero=hero_html,
            content=content_html
        )
    """

    def __init__(self):
        self._named_cols: List[Tuple[str, str]] = [("main", "1fr")]
        self._named_rows: List[Tuple[str, str]] = [("content", "1fr")]
        self._regions: List[_Region] = []
        self._outer_dzn: str = ""          # keep empty by default (no forced classes)
        self._height_css: str = "100vh"    # default grid height

    # ---------------- tracks (named & ordered) ----------------
    def columns(self, **spec: CSSVal) -> "GridLayoutBuilder":
        """
        Define columns with names, in the order you pass them:
            .columns(sidebar=280, main="1fr")
        """
        if not spec:
            raise ValueError("columns(): provide at least one named column")
        self._named_cols = [(k, _css_px(v)) for k, v in spec.items()]
        return self

    def rows(self, **spec: CSSVal) -> "GridLayoutBuilder":
        """
        Define rows with names, in the order you pass them:
            .rows(hero="auto", content="1fr")
        """
        if not spec:
            raise ValueError("rows(): provide at least one named row")
        self._named_rows = [(k, _css_px(v)) for k, v in spec.items()]
        return self

    def add_column(self, name: str, width: CSSVal) -> "GridLayoutBuilder":
        self._named_cols.append((name, _css_px(width)))
        return self

    def add_row(self, name: str, height: CSSVal) -> "GridLayoutBuilder":
        self._named_rows.append((name, _css_px(height)))
        return self

    def fill_height(self, css_value: str = "100vh") -> "GridLayoutBuilder":
        self._height_css = css_value
        return self

    # ---------------- convenience shapes ----------------
    def with_sidebar(self, *, width: CSSVal = 280, position: str = "left") -> "GridLayoutBuilder":
        """
        Quick two-column pattern with sidebar + main.
        Rows untouched; add rows() or add_row() after if you want multiple rows.
        """
        pos = "right" if str(position).lower() == "right" else "left"
        if pos == "left":
            self._named_cols = [("sidebar", _css_px(width)), ("main", "1fr")]
        else:
            self._named_cols = [("main", "1fr"), ("sidebar", _css_px(width))]
        return self

    # ---------------- regions ----------------
    def region(
        self,
        name: str,
        *,
        col: str,
        row: Optional[str],
        col_span: int = 1,
        row_span: Optional[int] = 1,  # None = span all rows
        dzn: str = "",
    ) -> "GridLayoutBuilder":
        """
        Add a region by track names. Example:
          .region("sidebar", col="sidebar", row=None, row_span=None)  # full height
          .region("hero",    col="main", row="hero")
          .region("content", col="main", row="content")
        """
        self._regions.append(
            _Region(
                name=name,
                col_name=col,
                row_name=row,
                col_span=col_span,
                row_span=row_span,
                dzn=dzn,
            )
        )
        return self

    # ---------------- build ----------------
    def build(self, *, name: str = "BuiltGridLayout"):
        # Prepare grid class names (optional styling)
        grid_cols = _grid_cols_class(self._named_cols)
        grid_rows = _grid_rows_class(self._named_rows)
        register_dzn_classes([grid_cols, grid_rows])  # let /_dzn.css emit helpers if needed
        register_dzn_classes(["grid"])                # if you have .grid { display:grid } in dzn

        # name→index maps
        col_index: Dict[str, int] = {n: i + 1 for i, (n, _) in enumerate(self._named_cols)}
        row_index: Dict[str, int] = {n: i + 1 for i, (n, _) in enumerate(self._named_rows)}
        total_rows = len(self._named_rows)

        # resolve placements (indices, spans)
        resolved: Dict[str, _Region] = {}
        order: List[str] = []
        for r in self._regions:
            if r.col_name not in col_index:
                raise ValueError(f"Unknown column '{r.col_name}' for region '{r.name}'")
            r._col_index = col_index[r.col_name]

            if r.row_name is None:
                r._row_index = 1
                r._row_span_resolved = total_rows if r.row_span is None else r.row_span
            else:
                if r.row_name not in row_index:
                    raise ValueError(f"Unknown row '{r.row_name}' for region '{r.name}'")
                r._row_index = row_index[r.row_name]
                r._row_span_resolved = total_rows - (r._row_index - 1) if r.row_span is None else r.row_span

            resolved[r.name] = r
            order.append(r.name)

        height_css = self._height_css

        class _Layout:
            __slots__ = ("_grid_cols", "_grid_rows", "_regions", "_order",
                         "_outer_dzn", "_region_dzn", "_debug")

            def __init__(
                self,
                *,
                outer_dzn: str = "",
                region_dzn: Optional[Dict[str, str]] = None,
                debug: bool = False,
            ):
                self._grid_cols = grid_cols
                self._grid_rows = grid_rows
                self._regions = resolved
                self._order = order
                self._outer_dzn = outer_dzn or ""
                self._region_dzn = region_dzn or {}
                self._debug = bool(debug)

                if self._outer_dzn:
                    register_dzn_classes(self._outer_dzn)
                if self._region_dzn:
                    register_dzn_classes(" ".join(self._region_dzn.values()))

            def render(self, **slots: str) -> str:
                # outer wrapper (no template)
                outer_attr = f' class="{html.escape(self._outer_dzn)}"' if self._outer_dzn else ""
                # ensure grid without relying on dzn
                grid_style = f"display:grid;min-height:{html.escape(height_css)};"
                grid_class = f"{self._grid_cols} {self._grid_rows}".strip()

                out: List[str] = []
                out.append(f"<div{outer_attr}>")
                out.append(f'  <div class="{html.escape(grid_class)}" style="{grid_style}">')

                for name in self._order:
                    R = self._regions[name]
                    slot_html = slots.get(name, "") or ""
                    region_cls = " ".join(c for c in [R.dzn, self._region_dzn.get(name, "")] if c).strip()
                    region_cls_attr = f' class="{html.escape(region_cls)}"' if region_cls else ""
                    region_style_attr = f' style="{html.escape(R.placement_style())}"'

                    if self._debug:
                        dbg = "outline:1px dashed rgba(220,38,38,.55);outline-offset:-1px;"
                        region_style_attr = region_style_attr[:-1] + dbg + '"'  # append

                    out.append(f'    <div data-region="{html.escape(name)}"{region_cls_attr}{region_style_attr}>')

                    if self._debug:
                        out.append(
                            '      <div style="font:11px/1.2 system-ui, -apple-system, Segoe UI, Roboto;'
                            'color:rgba(220,38,38,.8);padding:2px 4px;display:inline-block;">'
                            f'{html.escape(name)}</div>'
                        )

                    if slot_html:
                        out.append(f"      {slot_html}")
                    out.append("    </div>")

                out.append("  </div>")
                out.append("</div>")
                return "\n".join(out)

        _Layout.__name__ = name
        return _Layout


def layout_builder() -> GridLayoutBuilder:
    return GridLayoutBuilder()
