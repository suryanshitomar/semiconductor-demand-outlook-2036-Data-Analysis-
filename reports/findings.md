# Results and findings

Research snapshot reviewed 5 November 2026. Results below distinguish reported facts, published outlooks and illustrative analyst assumptions. This is a small market-intelligence study, not a validated ten-year demand forecast.

## Main conclusion

The sampled companies show strong recent revenue growth in AI computing, memory and foundry businesses, alongside slower or negative growth in some automotive and industrial suppliers. This supports prioritizing the AI infrastructure ecosystem for further demand research. It does not establish which chip segment or company will perform best by 2036.

## Result 1 Global semiconductor sales recovered after 2023

| Calendar year | Selected reported sales USD billions | Calculated year over year | Source |
| --- | ---: | ---: | --- |
| 2022 | 574.1 | Prior year not included | S01 |
| 2023 | 526.8 | -8.2% | S01 |
| 2024 | 630.5 | +19.7% | S03 |
| 2025 | 795.6 | +26.2% | S04 |

**Interpretation:** recovery in aggregate sales provides context for the opportunity, but does not mean every product category grows at the same pace. Revenue includes price and product-mix effects; this table does not measure chips shipped.
**Vintage detail:** the initial 2024 release reported 627.6 billion USD (S02); a later report gives 630.5 billion (S03). Both are retained in the audit data and only the later one is selected. Calculated growth uses selected rows from different release vintages and can differ from a release headline. Do not sum the two 2024 values.

## Result 2 Growth differs across the sampled companies

| Company | Included fiscal year | Period end | Revenue YoY | Source |
| --- | ---: | --- | ---: | --- |
| NVIDIA | 2026 | 2026-01-25 | +65.5% | S07 |
| SK hynix | 2025 | 2025-12-31 | +46.8% | S14 |
| TSMC | 2025 | 2025-12-31 | +35.9% | S13 |
| Texas Instruments | 2025 | 2025-12-31 | +13.0% | S09 |
| Infineon | 2025 | 2025-09-30 | -2.0% | S10 |
| NXP | 2025 | 2025-12-31 | -2.7% | S08 |

**Interpretation:** NVIDIA, SK hynix and TSMC have the strongest latest-included growth in this sample. Their different roles suggest that the recent opportunity warrants investigation across compute, memory and manufacturing. This is a comparison of consolidated company results, not measured growth of seven technology markets.
Texas Instruments shows recovery in its latest included year while Infineon and NXP decline. Their exposure to industrial, automotive and power applications remains relevant, but the observed results do not support describing the whole semiconductor industry as one uniform boom.
**Comparability:** fiscal-year labels refer to different periods. NVIDIA FY2026 ends in January 2026; Infineon FY2025 ends in September 2025. Growth is within each company in its reported currency and may reflect pricing, product mix, acquisitions and foreign exchange. No mixed-currency company revenue total or company market share is calculated.

## Result 3 The opportunity spans several parts of the value chain

| Technology theme | Documented company links in this study | Meaning for further research |
| --- | --- | --- |
| AI compute | NVIDIA | Investigate training, inference and competition from custom chips. |
| AI memory | SK hynix | Investigate bandwidth needs, capacity expansion and memory pricing cycles. |
| AI networking | NVIDIA | Investigate connectivity needs as AI systems scale. |
| Power electronics | Infineon and Texas Instruments | Investigate power conversion and efficiency requirements. |
| Automotive and edge AI | Infineon, NXP and Texas Instruments | Investigate adoption timing and automotive qualification cycles. |
| Industrial embedded | Infineon, NXP and Texas Instruments | Investigate automation demand and industrial capital spending. |
| Design tools and packaging | Siemens EDA and TSMC | Investigate design complexity and heterogeneous integration as distinct activities. |

These links are qualitative product/business relevance, not revenue allocation, market share or a complete competitive map. A company missing from a theme is not proven to have no involvement. Siemens EDA is mapped qualitatively; Siemens group revenue is excluded from chip-company comparisons. Design software and packaging share a broad research theme here, but would need separate market definitions for a market-size forecast.

## Published outlook External forecasts provide context

| External observation | Value | Classification | Source |
| --- | --- | --- | --- |
| Global semiconductor sales in 2026 | Approximately 1.51 trillion USD | WSTS Spring 2026 forecast | S05 |
| Global semiconductor sales in 2027 | Approximately 1.9 trillion USD | WSTS Spring 2026 forecast | S05 |
| Data-center electricity in 2025 | 485 TWh | IEA estimate | S12 |
| Data-center electricity in 2030 | 950 TWh | IEA projection | S12 |

**Interpretation:** the electricity outlook motivates research into data-center power requirements. It cannot be converted directly into power-chip revenue. WSTS values are rounded, vintage-specific forecasts, not confirmed sales or forecasts for 2036. They are not extended mechanically to 2036 in this project.

## Scenario result What the assumptions produce by 2036

Every theme starts at an artificial index of 100 in 2026. Early rates apply for four annual steps through 2030 and late rates for six steps through 2036. The table below is calculated from config/scenarios.json; it is not an externally validated demand prediction.

| Theme | Conservative index | Base index | Accelerated index | Base early rate | Base late rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| AI compute | 145.1 | 249.7 | 382.7 | 12.0% | 8.0% |
| AI memory | 131.7 | 219.7 | 338.7 | 10.0% | 7.0% |
| AI networking | 131.7 | 211.8 | 299.2 | 9.0% | 7.0% |
| Power electronics | 121.9 | 185.9 | 254.6 | 7.0% | 6.0% |
| Design tools and packaging | 126.8 | 185.9 | 254.6 | 7.0% | 6.0% |
| Automotive and edge AI | 121.9 | 179.1 | 259.4 | 6.0% | 6.0% |
| Industrial embedded | 110.5 | 153.8 | 204.2 | 5.0% | 4.0% |

**How to read it:** an index of 249.7 means approximately 2.50 times the artificial starting level under the chosen assumptions. AI compute has the highest base index because it was assigned the highest base rates. Power electronics and design tools/packaging have identical base rates and therefore overlap in the chart.
**What it cannot show:** equal index bases do not imply equal market sizes. Indices cannot rank absolute dollar opportunities, company returns or probabilities. Themes overlap and must not be summed. No company revenue, market share or share-price forecast is produced.

## Decision What to conclude from this project

Prioritize further research into AI compute, memory, connectivity, manufacturing/design and power conversion as linked infrastructure needs. Use automotive/edge and industrial embedded as contrasting demand cycles. Treat this as a research shortlist rather than a final 2036 winner ranking.

## Evidence needed before a ten-year winner claim

- Compatible segment market sizes, shipment volumes and pricing series, with non-overlapping definitions.
- Independent adoption forecasts, competitive-share evidence and multiple forecast vintages.
- Explicit evidence for growth assumptions and out-of-period backtesting.
- Common currency/period treatment where absolute comparisons are intended.

## Delivery and validation status

The Python analysis, SQL checks, notebook and chart review are completed. The Power BI report definitions pass structural schema checks and field-reference tests. Opening, refreshing and visually checking the project in Power BI Desktop remain pending; these are release gates before describing the native report as verified.
The study has 16 company-year observations and four selected market years. This sparse snapshot is useful for transparent exploratory analysis, but insufficient for a validated ten-year forecasting model.

## Source traceability

Source IDs resolve to original URLs, access dates and coverage in [sources.csv](../data/processed/sources.csv). Facts are manually curated, not a live feed or exhaustive company universe. Underlying source publications retain their own rights.
