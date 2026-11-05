# Validation status

## Completed in the authoring environment

- Raw source IDs, duplicate fact keys, scenario completeness and growth boundaries checked.
- Twelve unit tests pass, including compounding at the 2030 breakpoint, missing-history handling, currency-change rejection and visual field bindings.
- Sixteen schema-bearing Power BI report files validate against published Microsoft JSON schemas.
- Four Python charts rendered and visually reviewed.
- SQL queries executed against the generated SQLite database.
- Notebook code cells executed in order for a smoke check; the committed notebook remains without cached output.

## Native Power BI release gate still open

Power BI Desktop was not available at the checked installation path. JSON schema and field-reference checks do not validate Desktop compatibility, M/DAX execution, theme application or native visual appearance.

Before treating this as a finished Power BI portfolio:

- Open powerbi/Semiconductor-Outlook.pbip in a compatible Power BI Desktop build.
- Refresh the embedded model and resolve any import or compatibility errors.
- Check every page and chart against processed tables.
- Confirm the latest-company chart retains fiscal context and no mixed-currency revenue total is shown.
- Confirm index measures return blank for ambiguous totals and themes are not summed.
- Save genuine Power BI screenshots and record Desktop version, date and checks here.

No live data refresh, predictive backtest or ten-year forecast accuracy claim has been validated.
