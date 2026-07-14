"""CSV export for analytics modules."""

from __future__ import annotations

import csv
import io
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.analytics.schemas import AnalyticsFilter, ExportResponse
from app.modules.analytics.service import get_module_summary


def export_module_csv(
    db: Session,
    org_id: UUID,
    module: str,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ExportResponse:
    summary = get_module_summary(db, org_id, module, filters, today=today)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["section", "id", "label", "value", "unit", "status", "note"])

    for kpi in summary.kpis:
        writer.writerow(
            [
                "kpi",
                kpi.id,
                kpi.label,
                "" if kpi.value is None else str(kpi.value),
                kpi.unit or "",
                kpi.status,
                kpi.note or "",
            ]
        )

    for table in summary.tables_preview:
        headers = [c.key for c in table.columns]
        writer.writerow(["table", table.id, table.title, "|".join(headers), "", "", ""])
        for row in table.rows:
            values = [str(row.cells.get(h, "")) for h in headers]
            writer.writerow(["table_row", table.id, "", "|".join(values), "", "", ""])

    for point in summary.series_preview:
        writer.writerow(
            [
                "series",
                point.series or "primary",
                point.x,
                str(point.y),
                "",
                "",
                "",
            ]
        )

    content = buf.getvalue()
    # Subtract header
    row_count = max(content.count("\n") - 1, 0)
    filename = f"analytics_{module}_{summary.filters.date_from}_{summary.filters.date_to}.csv"
    return ExportResponse(
        module=module,
        format="csv",
        filename=filename,
        content_type="text/csv; charset=utf-8",
        content=content,
        row_count=row_count,
    )
