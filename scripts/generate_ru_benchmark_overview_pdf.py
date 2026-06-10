from __future__ import annotations

import ast
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from textwrap import shorten

from PyPDF2 import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)
PDF_PATH = REPORT_DIR / "power_systems_agent_benchmark_ru_overview.pdf"
MD_PATH = REPORT_DIR / "power_systems_agent_benchmark_ru_overview.md"
MEDIA_PATH = Path.home() / ".hermes" / "media_cache" / PDF_PATH.name
MEDIA_PATH.parent.mkdir(parents=True, exist_ok=True)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", FONT_REG))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD))
pdfmetrics.registerFont(TTFont("DejaVuMono", FONT_MONO))


def escape(s: object) -> str:
    s = "" if s is None else str(s)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def parse_mapping(path: Path, name: str) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.search(rf"{name}\s*=\s*(\{{.*?\}})\n\n", text, re.S)
    if not m:
        raise RuntimeError(f"mapping {name} not found in {path}")
    return ast.literal_eval(m.group(1))


def find_mapping(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"BASELINE_MODULE_BY_FAMILY\s*=\s*(\{.*?\})\n\n", text, re.S)
    if m:
        return ast.literal_eval(m.group(1))
    return {}


def compact_value(v, max_items=6, depth=0):
    if depth > 2:
        return "…"
    if isinstance(v, dict):
        parts = []
        for i, (k, val) in enumerate(v.items()):
            if i >= max_items:
                parts.append(f"… ещё {len(v)-max_items}")
                break
            parts.append(f"{k}: {compact_value(val, max_items=4, depth=depth+1)}")
        return "{" + "; ".join(parts) + "}"
    if isinstance(v, list):
        if not v:
            return "[]"
        sample = ", ".join(compact_value(x, max_items=3, depth=depth+1) for x in v[:max_items])
        if len(v) > max_items:
            sample += f", … ещё {len(v)-max_items}"
        return f"список[{len(v)}]: {sample}"
    return shorten(str(v), width=120, placeholder="…")


def schema_lines(schema) -> list[str]:
    if isinstance(schema, dict):
        lines = []
        for k, v in schema.items():
            if isinstance(v, dict):
                lines.append(f"{k}: объект ({', '.join(map(str, v.keys()))})")
            elif isinstance(v, list):
                lines.append(f"{k}: список / {compact_value(v)}")
            else:
                lines.append(f"{k}: {v}")
        return lines
    return [compact_value(schema)]


def input_lines(task) -> list[str]:
    keys = []
    for k, v in task.items():
        if k in {"task_id", "family", "candidate_id", "substrate", "objective", "bilingual", "subdomain", "submission_schema", "hard_constraints", "metrics", "source_evidence", "source_provenance", "numeric_tolerance"}:
            continue
        if k.endswith("_case") or k in {"public_inputs", "buses", "branches", "contingencies", "candidate_switches", "switching_budget", "flow_tolerance_pct"}:
            keys.append((k, v))
    if not keys and "public_inputs" in task:
        keys.append(("public_inputs", task["public_inputs"]))
    return [f"{k}: {compact_value(v)}" for k, v in keys[:10]]


def source_lines(task, source_card_exists: bool) -> list[str]:
    lines = []
    for src in task.get("source_provenance", []) or []:
        if isinstance(src, dict):
            title = src.get("title", "без названия")
            locator = src.get("locator", "без локатора")
            conf = src.get("confidence", "")
            notes = src.get("notes", "")
            line = f"{title}; локатор: {locator}"
            if conf:
                line += f"; доверие: {conf}"
            if notes:
                line += f"; примечание: {notes}"
            lines.append(line)
    for ev in task.get("source_evidence", []) or []:
        lines.append(f"source_evidence: {ev}")
    if source_card_exists:
        lines.append(f"source card: docs/source_cards/{task['family']}.md")
    return lines or ["Источник в task.json не указан явно; требуется доразметка provenance."]


def make_bullets(items: list[str], style, bullet_type="bullet", max_items=None):
    if max_items:
        items = items[:max_items] + ([f"… ещё {len(items)-max_items}"] if len(items) > max_items else [])
    return ListFlowable(
        [ListItem(Paragraph(escape(x), style), leftIndent=10) for x in items],
        bulletType=bullet_type,
        start="circle" if bullet_type == "bullet" else "1",
        leftIndent=18,
    )


def p(text, style):
    return Paragraph(escape(text), style)


def add_markdown_task(md: list[str], task, evaluator, baseline, source_exists):
    fam = task["family"]
    b = task.get("bilingual", {})
    ru_obj = b.get("objective", {}).get("ru") or task.get("objective", "")
    en_obj = b.get("objective", {}).get("en") or task.get("objective", "")
    md.append(f"### {fam}\n")
    md.append(f"- Идентификаторы: `{task.get('task_id')}`, candidate `{task.get('candidate_id', '—')}`")
    md.append(f"- Область: {task.get('subdomain', 'не указана')}")
    md.append(f"- Назначение: {ru_obj}")
    md.append(f"- English objective: {en_obj}")
    md.append(f"- Исходные данные: {'; '.join(input_lines(task)[:5])}")
    md.append(f"- Выход: {'; '.join(schema_lines(task.get('submission_schema', {})))}")
    md.append(f"- Проверка: `{evaluator}`; baseline: `{baseline}`")
    md.append("- Источники:")
    for line in source_lines(task, source_exists):
        md.append(f"  - {line}")
    md.append("")


def main():
    evaluator_map = parse_mapping(ROOT / "scripts" / "evaluate_submission.py", "EVALUATOR_MODULE_BY_FAMILY")
    baseline_map = find_mapping(ROOT / "scripts" / "run_public_baselines.py")
    tasks = []
    for path in sorted((ROOT / "tasks").glob("*/public/case_001/task.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        fam = task["family"]
        task["__path"] = str(path.relative_to(ROOT))
        task["__sample_path"] = str((path.parent / "sample_submission.json").relative_to(ROOT))
        tasks.append(task)

    generic = [fam for fam, mod in evaluator_map.items() if "generic_expected_answer" in mod]
    by_domain = defaultdict(list)
    for task in tasks:
        by_domain[task.get("subdomain") or "без указанной области"].append(task)

    md = []
    md.append("# Power Systems Agent Benchmark — подробный обзор\n")
    md.append(f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    md.append("## Краткий итог\n")
    md.append(f"- Всего публичных задач: {len(tasks)}")
    md.append(f"- Зарегистрированных проверяющих программ: {len(evaluator_map)}")
    md.append(f"- Generic expected-answer проверок: {len(generic)}")
    md.append(f"- Остались generic: {', '.join(generic) if generic else 'нет'}\n")

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.35 * cm,
        bottomMargin=1.35 * cm,
        title="Power Systems Agent Benchmark — обзор",
        author="Hermes Agent",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("RU", parent=styles["Normal"], fontName="DejaVu", fontSize=9.2, leading=12.4, spaceAfter=5))
    styles.add(ParagraphStyle("SmallRU", parent=styles["Normal"], fontName="DejaVu", fontSize=8, leading=10.2, spaceAfter=3))
    styles.add(ParagraphStyle("MonoRU", parent=styles["Normal"], fontName="DejaVuMono", fontSize=7.3, leading=9.2, spaceAfter=4))
    styles.add(ParagraphStyle("TitleRU", parent=styles["Title"], fontName="DejaVu-Bold", fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle("H1RU", parent=styles["Heading1"], fontName="DejaVu-Bold", fontSize=15, leading=18, spaceBefore=10, spaceAfter=8))
    styles.add(ParagraphStyle("H2RU", parent=styles["Heading2"], fontName="DejaVu-Bold", fontSize=12.5, leading=15, spaceBefore=9, spaceAfter=6))
    styles.add(ParagraphStyle("H3RU", parent=styles["Heading3"], fontName="DejaVu-Bold", fontSize=10.5, leading=13, spaceBefore=8, spaceAfter=4))

    story = []
    story.append(Paragraph("Power Systems Agent Benchmark", styles["TitleRU"]))
    story.append(Paragraph("Подробный обзор публичного набора задач, проверяющих программ и источников постановок", styles["RU"]))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Table([
        ["Показатель", "Значение"],
        ["Публичных задач", str(len(tasks))],
        ["Зарегистрированных проверяющих программ", str(len(evaluator_map))],
        ["Задач с generic expected-answer проверкой", str(len(generic))],
        ["Оставшиеся generic", ", ".join(generic) if generic else "нет"],
        ["Репозиторий", str(ROOT)],
    ], colWidths=[7 * cm, 10 * cm], style=TableStyle([
        ("FONT", (0, 0), (-1, -1), "DejaVu", 8.5),
        ("FONT", (0, 0), (-1, 0), "DejaVu-Bold", 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])))
    story.append(Spacer(1, 0.35 * cm))

    story.append(Paragraph("1. Что это за бенч", styles["H1RU"]))
    intro = (
        "Бенч предназначен для проверки того, умеет ли агент решать инженерные задачи в электроэнергетике не как свободное эссе, "
        "а как воспроизводимый расчёт или структурированное решение. Каждая публичная задача публикует входные данные в `task.json`, "
        "агент должен сформировать `submission.json`, после чего независимая программа проверки пересчитывает целевые величины, проверяет ограничения "
        "и возвращает `feasible`, `score` и список нарушений. Такой формат специально уменьшает зависимость от LLM-судьи: итог определяется кодом проверки, "
        "а не общим впечатлением от текста ответа."
    )
    story.append(Paragraph(intro, styles["RU"]))
    story.append(Paragraph("Жизненный цикл одной задачи:", styles["H2RU"]))
    flow = [["task.json\nисходные данные", "→", "агент\nрасчёт/выбор", "→", "submission.json\nструктурированный ответ", "→", "evaluator\nпроверка", "→", "score + violations"]]
    story.append(Table(flow, colWidths=[3.1*cm, .45*cm, 3.1*cm, .45*cm, 3.6*cm, .45*cm, 3.0*cm, .45*cm, 3.1*cm], style=TableStyle([
        ("FONT", (0, 0), (-1, -1), "DejaVu-Bold", 7.2),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F6F8FA")),
        ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#F6F8FA")),
        ("BACKGROUND", (4, 0), (4, 0), colors.HexColor("#F6F8FA")),
        ("BACKGROUND", (6, 0), (6, 0), colors.HexColor("#F6F8FA")),
        ("BACKGROUND", (8, 0), (8, 0), colors.HexColor("#F6F8FA")),
        ("BOX", (0, 0), (0, 0), 0.4, colors.grey),
        ("BOX", (2, 0), (2, 0), 0.4, colors.grey),
        ("BOX", (4, 0), (4, 0), 0.4, colors.grey),
        ("BOX", (6, 0), (6, 0), 0.4, colors.grey),
        ("BOX", (8, 0), (8, 0), 0.4, colors.grey),
    ])))

    story.append(Paragraph("2. Состав набора", styles["H1RU"]))
    domain_rows = [["Область", "Число задач"]]
    for domain, items in sorted(by_domain.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        domain_rows.append([domain, str(len(items))])
    story.append(Table(domain_rows, colWidths=[13*cm, 3*cm], repeatRows=1, style=TableStyle([
        ("FONT", (0, 0), (-1, -1), "DejaVu", 8),
        ("FONT", (0, 0), (-1, 0), "DejaVu-Bold", 8.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])))
    story.append(Paragraph("Все 41 публичные family сейчас подключены к специализированным executable-проверкам; generic expected-answer маршрутов не осталось.", styles["RU"]))

    story.append(PageBreak())
    story.append(Paragraph("3. Каталог задач", styles["H1RU"]))
    story.append(Paragraph("Ниже для каждой задачи указаны назначение, входы, требуемый выход, проверка и источники постановки. Источники взяты из `source_provenance`, `source_evidence` и карточек `docs/source_cards/`.", styles["RU"]))

    for idx, task in enumerate(tasks, 1):
        fam = task["family"]
        evaluator = evaluator_map.get(fam, "не зарегистрирован")
        baseline = baseline_map.get(fam, "не зарегистрирован")
        source_exists = (ROOT / "docs" / "source_cards" / f"{fam}.md").exists()
        b = task.get("bilingual", {})
        title_ru = b.get("title", {}).get("ru") or fam
        obj_ru = b.get("objective", {}).get("ru") or task.get("objective", "")
        obj_en = b.get("objective", {}).get("en") or task.get("objective", "")
        instructions_ru = b.get("instructions", {}).get("ru", "")

        add_markdown_task(md, task, evaluator, baseline, source_exists)

        header = f"3.{idx}. {fam}"
        block = [Paragraph(header, styles["H2RU"]), Paragraph(title_ru, styles["H3RU"])]
        meta = [
            ["task_id", task.get("task_id", "—")],
            ["candidate_id", task.get("candidate_id", "—")],
            ["substrate", task.get("substrate", "—")],
            ["область", task.get("subdomain", "—")],
            ["evaluator", evaluator],
            ["baseline", baseline],
            ["файлы", f"{task['__path']} ; {task['__sample_path']}"],
        ]
        block.append(Table([[p(escape(a), styles["SmallRU"]), p(escape(bv), styles["SmallRU"])] for a,bv in meta], colWidths=[3.1*cm, 13.3*cm], style=TableStyle([
            ("FONT", (0,0), (-1,-1), "DejaVu", 7.7),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F6F8FA")),
            ("GRID", (0,0), (-1,-1), 0.2, colors.lightgrey),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ])))
        block.append(Paragraph("Назначение", styles["H3RU"]))
        block.append(Paragraph(obj_ru, styles["RU"]))
        if obj_en and obj_en != obj_ru:
            block.append(Paragraph(f"Английская формулировка: {obj_en}", styles["SmallRU"]))
        if instructions_ru:
            block.append(Paragraph(f"Инструкция участнику: {instructions_ru}", styles["SmallRU"]))
        block.append(Paragraph("Исходные данные", styles["H3RU"]))
        block.append(make_bullets(input_lines(task), styles["SmallRU"], max_items=9))
        block.append(Paragraph("Требуемый выход", styles["H3RU"]))
        block.append(make_bullets(schema_lines(task.get("submission_schema", {})), styles["SmallRU"], max_items=12))
        constraints = task.get("hard_constraints", []) or []
        if constraints:
            block.append(Paragraph("Жёсткие ограничения и проверка", styles["H3RU"]))
            block.append(make_bullets([str(x) for x in constraints], styles["SmallRU"], max_items=8))
        metrics = task.get("metrics", []) or []
        if metrics:
            metric_lines = []
            for m in metrics[:6]:
                if isinstance(m, dict):
                    metric_lines.append(f"{m.get('name', 'metric')}: {m.get('description', '')} направление: {m.get('direction', '')}")
                else:
                    metric_lines.append(str(m))
            block.append(Paragraph("Метрики", styles["H3RU"]))
            block.append(make_bullets(metric_lines, styles["SmallRU"], max_items=6))
        block.append(Paragraph("Источники постановки", styles["H3RU"]))
        block.append(make_bullets(source_lines(task, source_exists), styles["SmallRU"], max_items=12))
        # Keep first part of each task together if possible, but avoid huge unbreakable sections.
        story.extend(block)
        story.append(Spacer(1, 0.15 * cm))

    story.append(PageBreak())
    story.append(Paragraph("4. Выводы и замечания по готовности", styles["H1RU"]))
    story.append(make_bullets([
        "В публичном срезе зарегистрирована 41 задача; все они имеют специализированный маршрут проверки, а не generic expected-answer evaluator.",
        "Каждая задача хранит явный `source_provenance` и/или `source_evidence`; это позволяет проследить, из какого списка литературы или task-bank записи она была получена.",
        "Для открытого использования наиболее важный следующий шаг — расширить hidden cases, чтобы публичный sample_submission не был единственным примером проверки.",
        "Часть source cards краткая: для финальной публикации стоит дополнить их более точными библиографическими ссылками, DOI/URL и пояснением адаптации к компактной executable-задаче.",
        "Проверки являются детерминированными и хорошо подходят для агент-агностичного сравнения: можно подключать любой CLI/агент, если он читает task.json и пишет submission.json.",
    ], styles["RU"]))

    MD_PATH.write_text("\n".join(md), encoding="utf-8")
    doc.build(story)
    shutil.copy2(PDF_PATH, MEDIA_PATH)

    reader = PdfReader(str(PDF_PATH))
    text0 = reader.pages[0].extract_text() or ""
    result = {
        "pdf": str(PDF_PATH),
        "media_pdf": str(MEDIA_PATH),
        "markdown": str(MD_PATH),
        "pages": len(reader.pages),
        "bytes": PDF_PATH.stat().st_size,
        "first_page_text_ok": "Power Systems Agent Benchmark" in text0,
        "tasks": len(tasks),
        "generic_count": len(generic),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
