from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports"
OUT_DIR.mkdir(exist_ok=True)
OUT_PDF = OUT_DIR / "power_systems_agent_benchmark_tasks_ru.pdf"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuMono", str(FONT_DIR / "DejaVuSansMono.ttf")))

PAGE_W, PAGE_H = A4
MARGIN = 1.65 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="RuTitle", fontName="DejaVu-Bold", fontSize=25, leading=31, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="RuSubtitle", fontName="DejaVu", fontSize=12.5, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#364152"), spaceAfter=8))
styles.add(ParagraphStyle(name="H1ru", fontName="DejaVu-Bold", fontSize=17, leading=22, spaceBefore=12, spaceAfter=7, textColor=colors.HexColor("#17324d")))
styles.add(ParagraphStyle(name="H2ru", fontName="DejaVu-Bold", fontSize=13, leading=17, spaceBefore=9, spaceAfter=5, textColor=colors.HexColor("#214f73")))
styles.add(ParagraphStyle(name="H3ru", fontName="DejaVu-Bold", fontSize=10.6, leading=14, spaceBefore=5, spaceAfter=3, textColor=colors.HexColor("#2f3b52")))
styles.add(ParagraphStyle(name="BodyRu", fontName="DejaVu", fontSize=9.2, leading=12.7, spaceAfter=4))
styles.add(ParagraphStyle(name="SmallRu", fontName="DejaVu", fontSize=7.7, leading=10.3, spaceAfter=2))
styles.add(ParagraphStyle(name="MonoRu", fontName="DejaVuMono", fontSize=7.4, leading=9.5, spaceAfter=2))
styles.add(ParagraphStyle(name="BoxTitle", fontName="DejaVu-Bold", fontSize=8.4, leading=10.5, alignment=TA_CENTER, textColor=colors.white))
styles.add(ParagraphStyle(name="Caption", fontName="DejaVu", fontSize=7.5, leading=9.5, alignment=TA_CENTER, textColor=colors.HexColor("#4d5b6a")))
styles.add(ParagraphStyle(name="TOC", fontName="DejaVu", fontSize=8.6, leading=11.2, leftIndent=8, firstLineIndent=-8))


def esc(text: Any) -> str:
    text = "" if text is None else str(text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def as_list(items: list[str], style="BodyRu") -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(esc(x), styles[style]), leftIndent=7) for x in items if x],
        bulletType="bullet",
        start="circle",
        leftIndent=14,
        bulletFontName="DejaVu",
        bulletFontSize=6,
    )


def read_mapping() -> dict[str, str]:
    text = (ROOT / "scripts/evaluate_submission.py").read_text(encoding="utf-8")
    m = re.search(r"EVALUATOR_MODULE_BY_FAMILY\s*=\s*(\{.*?\})\n\n@", text, re.S)
    return ast.literal_eval(m.group(1)) if m else {}


def read_baseline_mapping() -> dict[str, str]:
    text = (ROOT / "scripts/run_public_baselines.py").read_text(encoding="utf-8")
    m = re.search(r"BASELINE_MODULE_BY_FAMILY\s*=\s*(\{.*?\})\n\n", text, re.S)
    return ast.literal_eval(m.group(1)) if m else {}


EVAL_MAP = read_mapping()
BASELINE_MAP = read_baseline_mapping()

RU_FAMILY_TITLES = {
    "bess_ancillary_response": "Отклик батарейной системы накопления на вспомогательную услугу",
    "breaker_relay_short_circuit": "Токи короткого замыкания для выбора выключателя и уставки реле",
    "commercial_pv_lcoe_uncertainty": "Неопределённость приведённой стоимости энергии коммерческой СЭС",
    "contingency_screening": "Проверка аварийных отключений элементов сети",
    "corrective_transmission_switching": "Корректирующие переключения в передающей сети",
    "critical_clearing_time": "Критическое время отключения повреждения",
    "dispatch_uncertainty": "Диспетчеризация при неопределённости нагрузки и генерации",
    "distance_protection_settings": "Уставки дистанционной защиты линии",
    "dynamic_thermal_rating": "Динамический тепловой предел линии",
    "earth_fault_calculation": "Расчёт однофазного замыкания на землю",
    "electric_boiler_capacity_sizing": "Выбор мощности электрического котла",
    "electric_boiler_step_control": "Ступенчатое управление электрическим котлом",
    "en50160_voltage_compliance": "Проверка качества напряжения по EN 50160",
    "ev_v2g_outage_schedule": "График Vehicle-to-Grid при аварийном отключении",
    "ev_v2g_voltage_support": "Поддержка напряжения за счёт электромобилей",
    "fault_section_localization": "Определение повреждённого участка сети",
    "fci_placement": "Размещение указателей повреждения",
    "fci_saidi_caidi": "Оценка SAIDI/CAIDI для указателей повреждения",
    "fdi_state_estimation": "Обнаружение ложных данных в оценивании состояния",
    "flisr_restoration": "Поиск повреждения, изоляция и восстановление питания",
    "frt_compliance": "Проверка способности генератора проходить провал напряжения",
    "hydro_thermal_storage_uc": "Состав агрегатов с ГЭС, ТЭС и накопителем",
    "ibr_short_circuit_frt": "КЗ и прохождение провала напряжения для инверторного источника",
    "islanded_microgrid_pq_dispatch": "P–Q диспетчеризация изолированной микросети",
    "mas_frequency_handover": "Передача управления частотой между агентами",
    "microgrid_economic_dispatch": "Экономическая диспетчеризация микросети",
    "min_synchronous_share": "Минимальная доля синхронной генерации",
    "operator_breaker_load_actions": "Действия оператора с выключателями и нагрузкой",
    "overcurrent_protection": "Уставки максимальной токовой защиты",
    "pf_voltage_repair": "Коррекция напряжения по расчёту установившегося режима",
    "power_quality_event_classification": "Классификация события качества электроэнергии",
    "protected_meter_placement": "Размещение защищённых измерений",
    "pv_soft_cost_sobol": "Чувствительность мягких затрат СЭС методом Соболя",
    "pv_volt_var": "Volt–var регулирование фотоэлектрической установки",
    "rolling_microgrid_dispatch": "Скользящая диспетчеризация микросети",
    "scuc_n1": "Включение агрегатов с учётом критерия N−1",
    "three_phase_short_circuit": "Расчёт трёхфазного короткого замыкания",
    "transient_stability_prediction": "Прогноз переходной устойчивости",
    "wind_power_forecast": "Прогноз мощности ветровой генерации",
    "wind_prediction_interval": "Интервал прогноза ветровой генерации",
    "ybus_construction": "Построение матрицы узловых проводимостей Ybus",
}

DOMAIN_RU = {
    "protection": "релейная защита и расчёты коротких замыканий",
    "transmission": "передающие сети и режимные ограничения",
    "distribution": "распределительные сети и восстановление питания",
    "microgrid": "микросети и локальная диспетчеризация",
    "renewable": "возобновляемая генерация и инверторные источники",
    "forecast": "прогнозирование и вероятностные оценки",
    "power quality": "качество электроэнергии",
    "state estimation": "измерения, оценивание состояния и киберустойчивость",
}

FIELD_RU = {
    "task_id": "идентификатор задачи",
    "family": "семейство задач",
    "candidate_id": "номер исходной задачи-кандидата",
    "substrate": "тип вычислительной постановки",
    "objective": "цель",
    "subdomain": "раздел электроэнергетики",
    "public_inputs": "открытые входные данные",
    "network": "описание сети",
    "grid": "схема сети",
    "protection_case": "исходные данные для защиты",
    "short_circuit_case": "исходные данные для расчёта КЗ",
    "contingency_case": "исходные данные для проверки аварий",
    "switching_case": "исходные данные для переключений",
    "measurements": "измерения",
    "timeseries": "временные ряды",
    "calculation_spec": "расчётная спецификация",
    "scenario": "сценарий",
    "constraints": "ограничения",
    "assets": "оборудование и ресурсы",
}

EXEC_FLOWS = {
    "breaker_relay_short_circuit": ["Импедансы источника, трансформатора и фидера", "Расчёт токов КЗ", "Выбор выключателя", "Проверка уставки реле"],
    "distance_protection_settings": ["Линия и резервируемые участки", "Окна зон защиты", "Проверка нагрузки", "Координация выдержек времени"],
    "ybus_construction": ["Узлы, ветви, шунты", "Расчёт комплексных проводимостей", "Сборка Ybus", "Сравнение матрицы"],
    "corrective_transmission_switching": ["Послеаварийный режим", "Кандидатные переключения", "Расчёт потоков DC", "Проверка перегрузок"],
    "contingency_screening": ["Сеть и список отключений", "Расчёт каждого N−1", "Поиск островов и перегрузок", "Сравнение списка критичных"],
    "fdi_state_estimation": ["Измерения и модель", "Оценка состояния", "Поиск атакованных измерений", "Проверка исправленного состояния"],
    "flisr_restoration": ["Повреждение и выключатели", "План изоляции", "Восстановление питания", "Проверка радиальности"],
    "frt_compliance": ["Профиль напряжения и тока", "Окно провала", "Поддержка реактивного тока", "Решение о соответствии"],
    "overcurrent_protection": ["Нагрузка и минимальный ток КЗ", "Уставка тока", "Выдержка времени", "Селективность и чувствительность"],
    "pf_voltage_repair": ["Исходное напряжение", "Компенсация реактивной мощности", "Пересчёт напряжения", "Штраф за стоимость действия"],
    "pv_volt_var": ["Кривая volt–var", "Команды Q", "Исправленные напряжения", "Монотонность и пределы"],
}


def evaluator_kind(family: str) -> str:
    mod = EVAL_MAP.get(family, "")
    if mod.endswith("evaluate_generic_expected_answer"):
        return "эталонный ответ"
    return "отдельная исполняемая проверка"


def family_title(task: dict[str, Any]) -> str:
    fam = task.get("family", "")
    ru = (((task.get("bilingual") or {}).get("title") or {}).get("ru") or "").strip()
    return ru or RU_FAMILY_TITLES.get(fam, fam)


def objective_text(task: dict[str, Any]) -> str:
    ru = (((task.get("bilingual") or {}).get("objective") or {}).get("ru") or "").strip()
    return ru or str(task.get("objective", ""))


def pretty_key(k: str) -> str:
    return FIELD_RU.get(k, k.replace("_", " "))


def summarize_inputs(task: dict[str, Any]) -> list[str]:
    out = []
    pi = task.get("public_inputs") or {}
    if isinstance(pi, dict):
        fields = pi.get("input_fields") or []
        if fields:
            for f in fields[:9]:
                out.append(f"{f}: открытое поле, которое агент может использовать при решении")
        elif pi.get("calculation_spec"):
            out.append("calculation_spec: формулы, параметры и численные величины для расчёта")
    for k, v in task.items():
        if k in {"bilingual", "source_provenance", "source_evidence", "metrics", "hard_constraints", "submission_schema", "expected_submission", "baseline_submission"}:
            continue
        if k in {"network", "grid", "protection_case", "short_circuit_case", "contingency_case", "switching_case", "measurements", "timeseries", "scenario", "assets", "constraints"}:
            if isinstance(v, dict):
                inner = ", ".join(list(v.keys())[:7])
                out.append(f"{pretty_key(k)}: {inner}")
            elif isinstance(v, list):
                out.append(f"{pretty_key(k)}: список из {len(v)} элементов")
    # De-duplicate while preserving order
    seen, clean = set(), []
    for x in out:
        if x not in seen:
            clean.append(x); seen.add(x)
    return clean[:12] or ["Входные данные перечислены в task.json; для этой ранней версии задачи они сведены в раздел public_inputs."]


def summarize_output(task: dict[str, Any]) -> list[str]:
    schema = task.get("submission_schema") or {}
    if isinstance(schema, dict) and schema:
        return [f"{k}: {v}" for k, v in schema.items()]
    exp = task.get("expected_submission") or task.get("baseline_submission") or {}
    if isinstance(exp, dict) and exp:
        return [f"{k}: поле ответа" for k in exp.keys()]
    return ["JSON-файл submission.json с полями, указанными в условии задачи."]


def summarize_eval(task: dict[str, Any]) -> list[str]:
    fam = task.get("family", "")
    mod = EVAL_MAP.get(fam, "не зарегистрирован")
    items = [f"модуль проверки: {mod}", f"тип проверки: {evaluator_kind(fam)}"]
    metrics = task.get("metrics") or []
    if metrics:
        for m in metrics[:3]:
            if isinstance(m, dict):
                items.append(f"метрика {m.get('name')}: {m.get('description') or m.get('direction')}")
    constraints = task.get("hard_constraints") or []
    if constraints:
        items.extend([f"ограничение: {c}" for c in constraints[:4]])
    return items


def source_items(task: dict[str, Any]) -> list[str]:
    srcs = task.get("source_provenance") or []
    out = []
    for s in srcs[:5]:
        if isinstance(s, dict):
            title = s.get("title", "источник")
            loc = s.get("locator", "")
            notes = s.get("notes", "")
            conf = s.get("confidence", "")
            out.append(f"{title}; расположение: {loc}; уверенность: {conf}. {notes}")
    if not out:
        ev = task.get("source_evidence") or []
        out = [str(x) for x in ev[:5]]
    return out or ["Источник в task.json не указан явно; задача относится к внутреннему набору прототипа."]


class FlowDiagram(Flowable):
    def __init__(self, labels: list[str], width: float = CONTENT_W, height: float = 38 * mm):
        super().__init__()
        self.labels = labels
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return self.width, self.height

    def draw(self):
        c = self.canv
        n = len(self.labels)
        gap = 5 * mm
        box_w = (self.width - gap * (n - 1)) / n
        box_h = 18 * mm
        y = self.height / 2 - box_h / 2
        for i, label in enumerate(self.labels):
            x = i * (box_w + gap)
            c.setFillColor(colors.HexColor("#e9f2fb"))
            c.setStrokeColor(colors.HexColor("#3775a9"))
            c.roundRect(x, y, box_w, box_h, 5, stroke=1, fill=1)
            c.setFillColor(colors.HexColor("#1d3557"))
            c.setFont("DejaVu-Bold", 7.1)
            lines = split_label(label, int(box_w / 4.2))[:3]
            start_y = y + box_h / 2 + (len(lines)-1)*3.8
            for j, line in enumerate(lines):
                c.drawCentredString(x + box_w / 2, start_y - j * 7.4, line)
            if i < n - 1:
                x1 = x + box_w
                x2 = x1 + gap
                yy = y + box_h / 2
                c.setStrokeColor(colors.HexColor("#607d99"))
                c.line(x1 + 1.5, yy, x2 - 3.5, yy)
                c.setFillColor(colors.HexColor("#607d99"))
                c.line(x2 - 3.5, yy, x2 - 6.5, yy + 2.5)
                c.line(x2 - 3.5, yy, x2 - 6.5, yy - 2.5)


def split_label(label: str, max_chars: int) -> list[str]:
    words = label.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [label]


def make_table(rows, col_widths=None, style="SmallRu"):
    data = [[Paragraph(esc(cell), styles[style]) for cell in row] for row in rows]
    tbl = Table(data, colWidths=col_widths, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "DejaVu"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5df")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4fa")),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return tbl


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d8e0e8"))
    canvas.line(MARGIN, PAGE_H - 1.05*cm, PAGE_W - MARGIN, PAGE_H - 1.05*cm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(colors.HexColor("#5b6672"))
    canvas.drawString(MARGIN, PAGE_H - 0.78*cm, "Power Systems Agent Benchmark — описание задач")
    canvas.drawRightString(PAGE_W - MARGIN, 0.85*cm, str(doc.page))
    canvas.restoreState()


def build_story():
    tasks = []
    for p in sorted(ROOT.glob("tasks/*/public/case_001/task.json")):
        task = json.loads(p.read_text(encoding="utf-8"))
        tasks.append((task.get("family"), p, task))
    tasks.sort(key=lambda x: RU_FAMILY_TITLES.get(x[0], x[0]))
    story = []
    story.append(Spacer(1, 2.5*cm))
    story.append(Paragraph("Power Systems Agent Benchmark", styles["RuTitle"]))
    story.append(Paragraph("Пояснительная записка по задачам бенчмарка", styles["RuSubtitle"]))
    story.append(Paragraph("Что дано агенту, что нужно получить на выходе, как устроена проверка и на каких источниках основана постановка", styles["RuSubtitle"]))
    story.append(Spacer(1, 0.8*cm))
    story.append(make_table([
        ["Параметр", "Значение"],
        ["Репозиторий", str(ROOT)],
        ["Открытых задач", str(len(tasks))],
        ["Задач с отдельной исполняемой проверкой", str(sum(1 for fam,_,__ in tasks if evaluator_kind(fam) == "отдельная исполняемая проверка"))],
        ["Задач с проверкой по эталонному ответу", str(sum(1 for fam,_,__ in tasks if evaluator_kind(fam) == "эталонный ответ"))],
        ["Дата подготовки", date.today().isoformat()],
    ], [4.5*cm, CONTENT_W-4.5*cm]))
    story.append(PageBreak())

    story.append(Paragraph("1. Что представляет собой бенчмарк", styles["H1ru"]))
    story.append(Paragraph(
        "Бенчмарк предназначен для проверки того, умеет ли агент решать прикладные задачи электроэнергетики по исходным данным, а не только писать общий текст. Каждая задача задаётся файлом task.json: в нём есть условие, открытые входные данные, ограничения и схема ответа. Агент должен создать JSON-файл ответа. Затем отдельная программа проверки оценивает, удовлетворяет ли ответ ограничениям и насколько хорош результат.", styles["BodyRu"]))
    story.append(Paragraph("Важно: часть задач уже имеет полноценную расчётную проверку, где ответ пересчитывается независимо. Другая часть пока остаётся прототипом: проверка сравнивает ответ с заранее заданным эталоном. В отчёте это явно отмечено для каждой задачи.", styles["BodyRu"]))
    story.append(Paragraph("Общая схема работы", styles["H2ru"]))
    story.append(FlowDiagram(["task.json с условием", "Агент решает задачу", "submission.json", "Программа проверки", "оценка и нарушения"], height=30*mm))
    story.append(Paragraph("Типы проверок", styles["H2ru"]))
    story.append(make_table([
        ["Тип", "Что означает", "Как трактовать результат"],
        ["Отдельная исполняемая проверка", "Проверяющая программа заново считает режим, ток, матрицу, ограничения или качество плана.", "Такой вариант ближе к настоящей инженерной задаче."],
        ["Проверка по эталонному ответу", "Ответ сравнивается с заранее записанным ожидаемым результатом.", "Это полезно как каркас и быстрая проверка работоспособности, но слабее как независимая проверка способности решать задачу."],
    ], [4.2*cm, 7.0*cm, CONTENT_W-11.2*cm]))

    story.append(Paragraph("2. Состав задач", styles["H1ru"]))
    by_kind = defaultdict(list)
    for fam, p, task in tasks:
        by_kind[evaluator_kind(fam)].append(family_title(task))
    story.append(Paragraph("Задачи с отдельной исполняемой проверкой", styles["H2ru"]))
    story.append(as_list(by_kind["отдельная исполняемая проверка"], "SmallRu"))
    story.append(Paragraph("Задачи, которые пока проверяются по эталонному ответу", styles["H2ru"]))
    story.append(as_list(by_kind["эталонный ответ"], "SmallRu"))
    story.append(PageBreak())

    story.append(Paragraph("3. Как читать описание одной задачи", styles["H1ru"]))
    story.append(Paragraph("Для каждой задачи ниже приведены одинаковые блоки: назначение, исходные данные, что должен сделать агент, формат ответа, проверка, файлы и источники. Пути к файлам указаны относительно корня репозитория.", styles["BodyRu"]))
    story.append(FlowDiagram(["Исходные данные", "Инженерный расчёт или выбор", "Ответ в JSON", "Проверка ограничений"], height=28*mm))
    story.append(PageBreak())

    story.append(Paragraph("4. Подробное описание задач", styles["H1ru"]))
    for idx, (fam, path, task) in enumerate(tasks, 1):
        title = family_title(task)
        header = f"4.{idx}. {title}"
        elems = [Paragraph(header, styles["H2ru"])]
        elems.append(Paragraph(f"<b>Семейство:</b> <font name='DejaVuMono'>{esc(fam)}</font>; <b>идентификатор:</b> <font name='DejaVuMono'>{esc(task.get('task_id'))}</font>; <b>тип проверки:</b> {evaluator_kind(fam)}.", styles["BodyRu"]))
        if task.get("candidate_id"):
            elems.append(Paragraph(f"<b>Кандидат из банка задач:</b> {esc(task.get('candidate_id'))}.", styles["BodyRu"]))
        obj = objective_text(task)
        if obj:
            elems.append(Paragraph("Назначение", styles["H3ru"]))
            elems.append(Paragraph(esc(obj), styles["BodyRu"]))
        elems.append(Paragraph("Исходные данные", styles["H3ru"]))
        elems.append(as_list(summarize_inputs(task), "SmallRu"))
        elems.append(Paragraph("Что нужно сделать", styles["H3ru"]))
        if evaluator_kind(fam) == "отдельная исполняемая проверка":
            action = "Агент должен выполнить расчёт или выбор по исходным данным и вернуть численные значения/план, которые пройдут независимую проверку. Нельзя полагаться на скрытый эталон: проверка пересчитывает ключевые величины и ограничения."
        else:
            action = "Агент должен получить ответ в заданном формате. В текущем прототипе задача проверяется сравнением с эталонным ответом; это сохраняет единый интерфейс бенчмарка, но дальнейшая цель — заменить такую проверку независимым расчётом или имитацией процесса."
        elems.append(Paragraph(action, styles["BodyRu"]))
        if fam in EXEC_FLOWS:
            elems.append(FlowDiagram(EXEC_FLOWS[fam], height=25*mm))
        elems.append(Paragraph("Выходной файл", styles["H3ru"]))
        elems.append(as_list(summarize_output(task)[:10], "SmallRu"))
        elems.append(Paragraph("Проверка результата", styles["H3ru"]))
        elems.append(as_list(summarize_eval(task)[:8], "SmallRu"))
        rows = [["Файл", "Назначение"]]
        rel_task = path.relative_to(ROOT)
        rows.append([str(rel_task), "условие задачи и открытые входные данные"])
        sample = path.with_name("sample_submission.json")
        if sample.exists():
            rows.append([str(sample.relative_to(ROOT)), "пример корректного ответа для открытого случая"])
        mod = EVAL_MAP.get(fam)
        if mod:
            rows.append([mod.replace(".", "/") + ".py", "модуль проверки"])
        base = BASELINE_MAP.get(fam)
        if base:
            rows.append([base.replace(".", "/") + ".py", "базовое решение для открытого случая"])
        sc = ROOT / "docs/source_cards" / f"{fam}.md"
        if sc.exists():
            rows.append([str(sc.relative_to(ROOT)), "карточка источников и допущений"])
        elems.append(Paragraph("Файлы", styles["H3ru"]))
        elems.append(make_table(rows, [7.6*cm, CONTENT_W-7.6*cm], "SmallRu"))
        elems.append(Paragraph("Источники постановки", styles["H3ru"]))
        elems.append(as_list(source_items(task), "SmallRu"))
        elems.append(Spacer(1, 5*mm))
        # Keep first paragraphs together, but allow long sections to split.
        story.extend(elems)
    story.append(PageBreak())
    story.append(Paragraph("5. Выводы и что стоит улучшить дальше", styles["H1ru"]))
    story.append(Paragraph("Бенчмарк уже покрывает широкий набор задач: релейная защита, режимы сети, восстановление питания, инверторная генерация, микросети, качество электроэнергии, прогнозирование и надёжность. Наиболее сильная часть текущей версии — задачи с отдельной исполняемой проверкой: там агенту нужно выполнить расчёт или построить допустимый план, а проверка независимо воспроизводит ограничения.", styles["BodyRu"]))
    story.append(Paragraph("Главное направление развития — постепенно заменить задачи с проверкой по эталонному ответу на независимые проверяющие модели: расчёт короткого замыкания, простые оптимизационные постановки, проверку временных рядов, сетевые графы и вероятностные метрики. Это снизит риск угадывания формата и сделает бенчмарк ближе к реальным инженерным заданиям.", styles["BodyRu"]))
    return story


def main():
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=1.35*cm,
        bottomMargin=1.35*cm,
        title="Power Systems Agent Benchmark — описание задач",
        author="Hermes Agent",
    )
    doc.build(build_story(), onFirstPage=on_page, onLaterPages=on_page)
    print(OUT_PDF)

if __name__ == "__main__":
    main()
