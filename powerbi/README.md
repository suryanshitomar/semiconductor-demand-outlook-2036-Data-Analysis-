# Power BI project

Open Semiconductor-Outlook.pbip in a current Power BI Desktop installation with Power BI Projects and enhanced report format support. Enable the relevant project/format options if your build requires them. Desktop version compatibility can vary.

The project contains four pages and nine native visual definitions, a TMSL model.bim semantic model and DAX measures. Every import table embeds the curated snapshot as an M #table expression. There are no private file paths, credentials, external services or gateway dependencies. Refresh after opening to load the data; report definitions do not include a cached data model.

Pages:
1. Selected reported market history and source details.
2. Latest included company growth with fiscal context, plus documented technology links.
3. Conservative/Base/Accelerated 2036 indices and the underlying rates.
4. Published outlook values and the source register.

The tables intentionally remain separate analytical domains. There is no misleading company-to-market relationship or allocation of company revenue by qualitative theme links. Selecting data only cross-filters related visuals using the same table; cross-table slicers are not implemented.

## Change the scenario assumptions
Edit config/scenarios.json in the project root. Run python src/analysis.py followed by python src/powerbi.py. Close Desktop before regenerating; reopen and refresh afterward. This rebuilds the embedded snapshot. Power BI measures do not overwrite the Python assumptions.

Scenario index measures return blank for ambiguous combinations instead of summing overlapping themes or years. The latest-company chart uses a latest-only table so annual observations are not accidentally summed. The market chart excludes the superseded 2024 vintage; the CSV keeps it for audit.

## Validation status
Report JSON is checked against published Microsoft schemas with scripts/validate_powerbi.py. Unit tests check visual field references. This validates structure and bindings, not execution of M/DAX or rendering in Power BI Desktop. Desktop is not available in the verified authoring environment, so opening, refresh and visual QA remain a release gate. Do not describe the report as Desktop-tested or publish a screenshot of the Python charts as a Power BI screenshot.

To finish native validation: open the PBIP, refresh, verify all pages, check values against data/processed, select chart categories, confirm totals remain blank where intended, and save a verified PBIX if desired. Native validation findings should be recorded in docs/validation.md.

Microsoft format references:
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
- https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset

Optional theme: import theme.json through View > Themes. It is supplied separately and is not assumed to have been applied in Desktop.
