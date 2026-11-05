-- SQLite: run against outputs/analysis.sqlite after python src/analysis.py.
-- Do not aggregate company revenue across currencies or value-chain stages.

-- Selected market vintage; the rejected historical version stays in the audit table.
SELECT year, value_usd_billions,
       ROUND(100*yoy_growth,2) AS yoy_percent, source_id
FROM market WHERE selected=1 ORDER BY year;

-- Latest included fiscal period per company. This is not a calendar-aligned comparison.
WITH latest AS (
  SELECT *, ROW_NUMBER() OVER(PARTITION BY company_id ORDER BY fiscal_year DESC) AS rn
  FROM company_revenue
)
SELECT company, fiscal_year, period_end, currency,
       ROUND(100*yoy_growth,2) AS growth_percent, source_id
FROM latest WHERE rn=1 ORDER BY growth_percent DESC;

-- No summation of theme indices: the themes overlap and have equal artificial bases.
SELECT theme, scenario, ROUND(index_value,1) AS index_2036
FROM scenarios WHERE year=2036 ORDER BY scenario,index_value DESC;

-- Verify each fact row has source provenance.
SELECT r.company_id, r.fiscal_year
FROM company_revenue r LEFT JOIN sources s USING(source_id)
WHERE s.source_id IS NULL;
