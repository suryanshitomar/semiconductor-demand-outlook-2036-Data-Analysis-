# Methodology and analytical boundaries

## Research question
Which technology themes deserve further demand research through 2036, and how do selected companies connect to them?

## Dataset
The raw JSON snapshot contains 17 source references, seven companies, 16 annual company revenue observations, five historical market-vintage rows, four published outlook observations, seven themes and 13 documented company-theme links. Dates and numbers were manually curated from linked primary sources on 5 November 2026. Source URLs and release coverage are preserved. This is a small research dataset, not a comprehensive or automatically refreshed market database.

Only four market years are selected for charts. The original 2024 figure 627.6 and revised 630.5 are retained; the latter is selected. Other years come from separate releases, so even the selected series spans vintages. No interpolation fills missing history. Historical revenue is reported nominal revenue, not units shipped or constant-currency growth.

Siemens EDA is qualitatively mapped. Siemens group revenue is excluded because it would not measure semiconductor EDA revenue. TSMC uses company-reported USD revenue, not an independently chosen FX rate. SK hynix is stored in KRW millions; 97.1467 trillion KRW becomes 97,146,700 million KRW. Infineon stays in EUR millions. Absolute values are not aggregated across currencies or value-chain stages.

## Scenario math
For each theme and scenario:

Index(year) = 100 × (1 + early rate) ^ min(year − 2026, 4) × (1 + late rate) ^ max(year − 2030, 0)

There are four annual growth steps from 2026 to 2030 and six from 2030 to 2036. Rates are explicit analyst assumptions in config/scenarios.json. They are intentionally illustrative ranges rather than fitted parameters or published market forecasts. The labels Conservative, Base and Accelerated have no probability interpretation. Validate completeness and rate boundaries before computation.

A larger index means faster assumed growth from an artificial equal base. It does not mean larger addressable market, stronger margins, better company returns or more resilient demand. Themes overlap and indices must not be summed. Company-theme links have no exposure weights; do not allocate consolidated company revenue using them.

## Public forecasts
Published WSTS 2026/2027 sales forecasts use the June 2026 release and remain separate from historical data. Values are rounded. IEA electricity figures are a published estimate and projection, with TWh units; they cannot be converted directly into semiconductor revenue. No source-backed 2036 market-size forecast is currently included.

## What to add before claiming a winner
Collect compatible segment size, shipment, price and adoption data. Define non-overlapping product categories and a common geography, period and currency. Add independent forecast vintages and test a model against earlier periods. Explain how efficiency, supply, competition and pricing alter adoption. Avoid manufacturing a confidence interval from three hand-chosen scenarios.

## Reproducibility and rights
The pipeline operates offline on the pinned JSON. Updating a URL does not refresh facts: review the source, edit the snapshot, record the release and rerun tests. Original source documents are linked rather than bundled. Underlying publications retain their own rights. IEA cites CC BY 4.0; this does not establish the license of other sources. No reuse license has yet been selected for project code.
