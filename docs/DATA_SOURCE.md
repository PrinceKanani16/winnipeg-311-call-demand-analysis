# Data source and license

**Dataset:** City of Winnipeg Open Data, *311 Incoming Calls by Day*.

- Dataset page: https://data.winnipeg.ca/dataset/311-Incoming-Calls-By-Day/p3xc-y6xi
- Data API: https://data.winnipeg.ca/resource/p3xc-y6xi.csv
- Archived local CSV: `data/311_incoming_calls_by_day_20260217.csv`
- Source snapshot used by the original project: 2026-02-17
- Original coverage: 2008-10-03 to 2026-02-17; 6,346 records
- Study window: full years 2009-01-01 through 2025-12-31
- Data are aggregate daily call counts, not call records or personally identifying information.

The CSV is provided under the **Open Government Licence – Winnipeg**:
https://data.winnipeg.ca/stories/s/Open-Data-Licence/rwzh-4ijx/

**Attribution:** Contains information licensed under the Open Government Licence – Winnipeg.

This project is an independent analysis and is not endorsed by the City of Winnipeg.

## Cleaning performed

Year, month and day fields are converted into a date index. Numbers with comma
separators (e.g., `1,092`) are parsed as counts. Exactly one day is absent
from the archived source: **2024-03-09**. It is imputed as the mean of
2024-03-08 (1,795) and 2024-03-10 (259), yielding 1,027 calls.

The archived CSV is kept in the repository so rerunning the notebook does not
silently change the results when the City's live feed is updated.
