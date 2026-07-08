import csv
import io

DRR_THRESHOLD = 15.0


def _to_float(value):
    if value is None:
        return 0.0
    s = str(value).strip().replace(" ", "").replace("\xa0", "").replace(",", ".")
    if s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_csv(content_bytes):
    text = content_bytes.decode("utf-8-sig", errors="replace")
    sample = text[:2000]
    delimiter = ";" if sample.count(";") > sample.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows = []
    for r in reader:
        norm = {(k or "").strip().lower(): v for k, v in r.items()}
        rows.append({
            "campaign": norm.get("campaign") or norm.get("кампания") or "—",
            "spend": _to_float(norm.get("spend") or norm.get("расход")),
            "revenue": _to_float(norm.get("revenue") or norm.get("выручка")),
            "buyout": _to_float(norm.get("buyout") or norm.get("выкуп")),
            "orders": _to_float(norm.get("orders") or norm.get("заказы")),
        })
    return rows


def analyze(rows, threshold=DRR_THRESHOLD):
    results = []
    total_spend = 0.0
    total_revenue = 0.0
    for row in rows:
        spend = row["spend"]
        revenue = row["revenue"]
        base = row["buyout"] if row["buyout"] > 0 else revenue
        total_spend += spend
        total_revenue += revenue
        drr = (spend / base * 100) if base > 0 else None
        results.append({**row, "drr": drr, "base": base})

    for r in results:
        drr = r["drr"]
        if r["spend"] > 0 and drr is None:
            r["flag"] = True
            r["reco"] = "Нет продаж при расходе — отключить"
        elif drr is None:
            r["flag"] = False
            r["reco"] = "Нет данных"
        elif drr > 2 * threshold:
            r["flag"] = True
            r["reco"] = "Убыточно — отключить"
        elif drr > threshold:
            r["flag"] = True
            r["reco"] = "Выше порога — снизить ставку / сузить аудиторию"
        else:
            r["flag"] = False
            r["reco"] = "В норме — можно масштабировать"

    results.sort(key=lambda x: (1 if x["flag"] else 0, x["drr"] or 0), reverse=True)
    avg_drr = (total_spend / total_revenue * 100) if total_revenue > 0 else None
    summary = {
        "total_spend": total_spend,
        "total_revenue": total_revenue,
        "avg_drr": avg_drr,
        "threshold": threshold,
        "flagged": sum(1 for r in results if r["flag"]),
    }
    return results, summary


def format_report(results, summary):
    lines = ["📊 Анализ рекламных кампаний", ""]
    lines.append(f"Порог ДРР: {summary['threshold']:.0f}%")
    if summary["avg_drr"] is not None:
        lines.append(f"Средний ДРР по аккаунту: {summary['avg_drr']:.1f}%")
    lines.append(f"Расход: {summary['total_spend']:.0f} ₽ | Выручка: {summary['total_revenue']:.0f} ₽")
    lines.append(f"Кампаний с флагом: {summary['flagged']} из {len(results)}")
    lines.append("")
    for r in results:
        drr_str = f"{r['drr']:.1f}%" if r["drr"] is not None else "—"
        mark = "🔴" if r["flag"] else "🟢"
        lines.append(f"{mark} {r['campaign']}: ДРР {drr_str} | расход {r['spend']:.0f} ₽")
        lines.append(f"    → {r['reco']}")
    return "\n".join(lines)


SAMPLE_ROWS = [
    {"campaign": "Платья лето", "spend": 12000, "revenue": 150000, "buyout": 120000, "orders": 60},
    {"campaign": "Джинсы базовые", "spend": 18000, "revenue": 60000, "buyout": 40000, "orders": 25},
    {"campaign": "Куртки зима", "spend": 9000, "revenue": 0, "buyout": 0, "orders": 0},
    {"campaign": "Футболки принт", "spend": 5000, "revenue": 90000, "buyout": 82000, "orders": 45},
    {"campaign": "Юбки офис", "spend": 14000, "revenue": 55000, "buyout": 30000, "orders": 20},
]
