# Data dictionary

All CSVs use UTF-8, a header row and dot decimal notation. Missing values are empty fields, not zeros. Boolean fields use True/False in CSV. Numeric rates are fractions: 0.10 means 10 percent.

| Table | Grain and fields | Interpretation |
| --- | --- | --- |
| sources | One source_id; title, url, published_date, accessed_date, coverage | Blank publication dates are unresolved; access date is not publication date. |
| company_revenue | One company_id and fiscal_year; period_end, revenue_millions, currency, source_id, status, scope, company, yoy_growth, within_company_index, index_base_fiscal_year | Millions of the stated currency. Growth is within company. Index bases vary across companies; not a common calendar comparison. |
| market | One year and source vintage; value_usd_billions, source_id, selected, status, yoy_growth | Only selected=True rows form the analysis series. The table has two 2024 vintages. |
| published_outlook | One metric, year and source_id; value, unit, status | Sales forecasts and electricity estimates/projections have different units and must not be aggregated. |
| themes | One theme_id; theme, driver, risk | Qualitative research taxonomy, with overlapping categories. |
| company_theme | One company_id and theme_id; company, theme, source_id, relationship, interpretation, documented_link | documented_link=1 indicates a curated source-supported link, not market share or strength. Absence is not evidence of zero involvement. |
| assumptions | One theme_id and scenario; base_year, early_end, end_year, early_growth, late_growth, basis, rationale | Editable illustrative rates; basis is always analyst_assumption. |
| scenarios | One theme_id, scenario and year; theme, index_value, basis, base_year, early_growth, late_growth | Calculated index; 2026=100; no currency units or market-size interpretation. |

The Power BI model additionally contains latest_company and scenario_endpoints, derived subsets used to avoid inappropriate aggregation in native chart measures. The model uses selected market rows; the full audit table remains in CSV/SQLite.
