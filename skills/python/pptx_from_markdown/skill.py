#!/usr/bin/env python3
"""
pptx_from_markdown skill

PPTXテンプレートとMarkdownファイルをもとに PowerPoint プレゼンテーションを生成する。

## Markdownの書き方

```markdown
# プレゼンタイトル
発表者名や日付などのサブタイトル

## セクション見出し

### スライドタイトル
- 箇条書き1
- 箇条書き2

### 別のスライドタイトル
本文テキストはそのままスライドに入ります。
```

### スライドの種類とレイアウト対応

| Markdown               | スライドレイアウト                        |
|------------------------|-------------------------------------------|
| `# タイトル`           | タイトルスライド (layout index 0)         |
| `## セクション`        | セクションヘッダー (layout index 2 or 1) |
| `### スライドタイトル` | タイトルと内容 (layout index 1)          |
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pptx import Presentation
from pptx.util import Pt


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Slide:
    kind: str  # "title" | "section" | "content"
    title: str = ""
    subtitle: str = ""
    bullets: list[str] = field(default_factory=list)
    body_lines: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

def parse_markdown(text: str) -> list[Slide]:
    """Markdownテキストをスライドのリストに変換する。"""
    slides: list[Slide] = []
    current: Optional[Slide] = None
    pending_subtitle: list[str] = []

    def flush_pending_subtitle() -> str:
        s = "\n".join(pending_subtitle).strip()
        pending_subtitle.clear()
        return s

    def commit_slide(slide: Optional[Slide]) -> None:
        if slide is not None:
            slides.append(slide)

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        # --- H1: タイトルスライド ---
        m = re.match(r'^# (.+)$', line)
        if m:
            commit_slide(current)
            current = Slide(kind="title", title=m.group(1).strip())
            pending_subtitle.clear()
            continue

        # --- H2: セクションヘッダー ---
        m = re.match(r'^## (.+)$', line)
        if m:
            if current and current.kind == "title" and pending_subtitle:
                current.subtitle = flush_pending_subtitle()
            elif current:
                flush_pending_subtitle()
            commit_slide(current)
            current = Slide(kind="section", title=m.group(1).strip())
            pending_subtitle.clear()
            continue

        # --- H3: コンテンツスライド ---
        m = re.match(r'^### (.+)$', line)
        if m:
            if current and current.kind == "title" and pending_subtitle:
                current.subtitle = flush_pending_subtitle()
            elif current:
                flush_pending_subtitle()
            commit_slide(current)
            current = Slide(kind="content", title=m.group(1).strip())
            pending_subtitle.clear()
            continue

        # 現在スライドがなければ無視
        if current is None:
            continue

        # --- 箇条書き ---
        m = re.match(r'^[\-\*\+] (.+)$', line)
        if m:
            flush_pending_subtitle()
            current.bullets.append(m.group(1).strip())
            continue

        # --- 番号付きリスト ---
        m = re.match(r'^\d+\. (.+)$', line)
        if m:
            flush_pending_subtitle()
            current.bullets.append(m.group(1).strip())
            continue

        # --- 空行 ---
        if line.strip() == "":
            if current.kind == "title" and not current.subtitle:
                pending_subtitle.append("")
            continue

        # --- 通常テキスト ---
        if current.kind == "title" and not current.subtitle:
            pending_subtitle.append(line)
        else:
            flush_pending_subtitle()
            current.body_lines.append(line)

    # 最後のスライドを確定
    if current and current.kind == "title" and pending_subtitle:
        current.subtitle = flush_pending_subtitle()
    commit_slide(current)

    return slides


# ---------------------------------------------------------------------------
# Layout resolver
# ---------------------------------------------------------------------------

def find_layout(prs: Presentation, *name_candidates: str) -> object:
    """
    スライドレイアウトを名前で検索して返す。
    見つからない場合はインデックスでフォールバック。
    """
    layouts_by_name = {layout.name: layout for layout in prs.slide_layouts}
    for name in name_candidates:
        if name in layouts_by_name:
            return layouts_by_name[name]
    # フォールバック: 候補の順に最初に一致する部分一致を使う
    for candidate in name_candidates:
        for lname, layout in layouts_by_name.items():
            if candidate.lower() in lname.lower():
                return layout
    return None


def get_layout_title(prs: Presentation) -> object:
    layout = find_layout(prs, "Title Slide", "タイトル スライド", "タイトル")
    return layout if layout else prs.slide_layouts[0]


def get_layout_section(prs: Presentation) -> object:
    layout = find_layout(prs, "Section Header", "セクション見出し", "セクション")
    return layout if layout else prs.slide_layouts[min(2, len(prs.slide_layouts) - 1)]


def get_layout_content(prs: Presentation) -> object:
    layout = find_layout(prs, "Title and Content", "タイトルとコンテンツ", "タイトル、コンテンツ")
    return layout if layout else prs.slide_layouts[min(1, len(prs.slide_layouts) - 1)]


# ---------------------------------------------------------------------------
# Placeholder helpers
# ---------------------------------------------------------------------------

def set_placeholder_text(slide_obj, idx: int, text: str) -> bool:
    """指定インデックスのプレースホルダーにテキストをセットする。"""
    for ph in slide_obj.placeholders:
        if ph.placeholder_format.idx == idx:
            tf = ph.text_frame
            tf.text = text
            return True
    return False


def add_bullets_to_placeholder(slide_obj, idx: int, bullets: list[str]) -> bool:
    """指定インデックスのプレースホルダーに箇条書きを追加する。"""
    for ph in slide_obj.placeholders:
        if ph.placeholder_format.idx == idx:
            tf = ph.text_frame
            tf.clear()
            for i, bullet in enumerate(bullets):
                if i == 0:
                    tf.text = bullet
                else:
                    p = tf.add_paragraph()
                    p.text = bullet
            return True
    return False


def add_body_text_to_placeholder(slide_obj, idx: int, lines: list[str]) -> bool:
    """指定インデックスのプレースホルダーに本文テキストを追加する。"""
    return add_bullets_to_placeholder(slide_obj, idx, lines)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def add_title_slide(prs: Presentation, slide_data: Slide) -> None:
    layout = get_layout_title(prs)
    slide = prs.slides.add_slide(layout)
    set_placeholder_text(slide, 0, slide_data.title)
    if slide_data.subtitle:
        set_placeholder_text(slide, 1, slide_data.subtitle)


def add_section_slide(prs: Presentation, slide_data: Slide) -> None:
    layout = get_layout_section(prs)
    slide = prs.slides.add_slide(layout)
    set_placeholder_text(slide, 0, slide_data.title)
    if slide_data.subtitle or slide_data.body_lines:
        text = slide_data.subtitle or "\n".join(slide_data.body_lines)
        set_placeholder_text(slide, 1, text)


def add_content_slide(prs: Presentation, slide_data: Slide) -> None:
    layout = get_layout_content(prs)
    slide = prs.slides.add_slide(layout)
    set_placeholder_text(slide, 0, slide_data.title)
    if slide_data.bullets:
        add_bullets_to_placeholder(slide, 1, slide_data.bullets)
    elif slide_data.body_lines:
        add_body_text_to_placeholder(slide, 1, slide_data.body_lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_presentation(template_path: Path, slides: list[Slide], output_path: Path) -> None:
    prs = Presentation(str(template_path))

    # テンプレートの既存スライドを削除して白紙にする
    xml_slides = prs.slides._sldIdLst  # noqa: SLF001
    for sld_id in list(xml_slides):
        xml_slides.remove(sld_id)

    for slide_data in slides:
        if slide_data.kind == "title":
            add_title_slide(prs, slide_data)
        elif slide_data.kind == "section":
            add_section_slide(prs, slide_data)
        else:
            add_content_slide(prs, slide_data)

    prs.save(str(output_path))
    print(f"生成完了: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PPTXテンプレートとMarkdownからPowerPointを生成するスキル"
    )
    parser.add_argument("--template", required=True, help="PPTXテンプレートファイルのパス")
    parser.add_argument("--markdown", required=True, help="Markdownファイルのパス")
    parser.add_argument("--output", default="output.pptx", help="出力ファイルのパス (default: output.pptx)")
    args = parser.parse_args()

    template_path = Path(args.template)
    markdown_path = Path(args.markdown)
    output_path = Path(args.output)

    if not template_path.exists():
        print(f"エラー: テンプレートファイルが見つかりません: {template_path}", file=sys.stderr)
        sys.exit(1)
    if not markdown_path.exists():
        print(f"エラー: Markdownファイルが見つかりません: {markdown_path}", file=sys.stderr)
        sys.exit(1)

    markdown_text = markdown_path.read_text(encoding="utf-8")
    slides = parse_markdown(markdown_text)

    if not slides:
        print("エラー: Markdownファイルにスライドが見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    build_presentation(template_path, slides, output_path)


if __name__ == "__main__":
    main()
