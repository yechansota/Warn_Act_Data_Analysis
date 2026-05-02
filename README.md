# Texas WARN Act ER Risk Intelligence Report

> **Subtitle**: Labor Market Compliance Benchmarking for Union Prevention & Proactive ER Strategy
> **Period**: January 2019 – April 2026 (88 months)
> **Dataset**: Texas Workforce Commission public WARN Act notices, 2,340 filings
> **Author**: GT MS Analytics Portfolio | ER Risk Intelligence Series

---

## 1. Project Overview

Recent headlines about large-scale layoffs got me curious about what the actual data looks like, so I went back through 2,340 WARN Act notices filed with the Texas Workforce Commission between January 2019 and April 2026.

The first thing that stood out was the gap between law and practice. The federal WARN Act requires 60 days of advance notice, but 63% of filings fell short of that threshold. This doesn’t appear to be a one-time anomaly either — across the full seven-year timeline, more than half of the market consistently sits in lower-compliance ranges.

### Headline Numbers

| Metric | Value |
|---|---:|
| Total WARN filings | 2,340 |
| Valid filings (compliance analysis) | 1,524 |
| Retroactive filings (exception clause invoked) | 807 (34.5%) |
| Average notice lead time (valid cases) | 41.3 days |
| Filed under 60-day legal threshold | **63.5%** |
| Total workers displaced | 211,435 |

---

## 2. Data & Methodology

### Data Source

| Item | Detail |
|---|---|
| Provider | Texas Workforce Commission (TWC) |
| File | `Worker_Adjustment_and_Retraining_Notification__WARN__Notices.csv` |
| Coverage | 2019-01-04 to 2026-04-06 |
| Original records | 2,340 |

### Preprocessing

Retroactive filings (NOTICE_DATE > LAYOFF_DATE) are flagged separately as exception-clause cases rather than excluded, as they represent a meaningful behavioral pattern. Two records with year typos (1930s dates) are excluded entirely. 15 derived variables were generated including `lead_days`, `lead_days_short`, `company_normalized`, `same_company_cluster`, and `industry_final`.

### Industry Classification (3-Stage Pipeline)

Stage 1 applies a keyword dictionary with weighted scoring (strong keyword = 6 pts, normal = 2 pts) to worksite name text. Conflicts within a 4-point margin are flagged as ambiguous and resolved to the top scorer. Stage 2 applies a domain brand dictionary (hotel chains, auto dealers, restaurant franchises) to Stage 1 misses. Stage 3 merges categories under 5 cases into "Other" and retains unmatched cases as "Unknown" — not force-classified. Final result: 1,752 classified (74.9%), 588 Unknown (25.1%).

### Company Name Normalization

Raw worksite names appear in multiple variants for the same company. Normalization strips corporate suffixes (LLC, Inc., Corp), city and branch tags, and special characters, then uppercases all text. Companies appearing 2 or more times after normalization form the repeat-offender cohort (192 companies).

---

## 3. Visualization Guide — 14 Charts

---

### Page 1 — Cover & KPI Summary

**Data file**: `data_exports/01_kpi_summary.csv`

Five headline KPIs are presented on a single cover page: 2,340 total WARN filings, 1,524 valid filings used in compliance analysis, 211,435 total workers displaced, 63.5% of filings below the 60-day legal threshold, and an average notice lead time of 41.3 days. The table of contents and a Data & Methodology summary occupy the lower half of the page.

---

### Page 2 — Industry × Year 60-Day Compliance Rate Heatmap
<img width="905" height="702" alt="image" src="https://github.com/user-attachments/assets/b81ef2be-c73c-4560-8c72-20a31aa42409" />

**Data file**: `data_exports/02_industry_year_heatmap.csv`

A 10-industry × 7-year matrix shows the 60-day compliance rate at each intersection for 2019–2025. Each cell displays the compliance percentage and the underlying event count (n=). Cells with fewer than 3 events are shown as "n/a" to prevent inference from negligible samples. The 2020 column is bordered in red to mark the COVID shock year.

Manufacturing and Tech/IT maintain the highest compliance rates across all years. Retail & Food and Logistics show consistently low rates throughout the period. The 2020 column is uniformly dark across all industries, confirming that COVID affected compliance regardless of sector. Tech/IT compliance deteriorates from 2022–2023 onward, corresponding to large-scale technology sector layoffs registering in the Texas dataset.

---

### Page 3 — Quarterly 60-Day Compliance Rate vs. Economic Cycles
<img width="979" height="759" alt="image" src="https://github.com/user-attachments/assets/b705a538-5456-48bc-b6d5-b5c0b120108e" />

**Data file**: `data_exports/03_quarterly_trend.csv`

A line chart plots quarterly compliance rate from 2019Q1 through 2025Q4, with a 4-quarter centered moving average overlaid for trend smoothing. The 60-day legal floor is marked as a horizontal dashed line at 60%. COVID shock (2020Q1–Q2) and the Federal Reserve rate hike cycle (2022Q1–2023Q4) are marked with shaded bands. The minimum is 2020Q1 at 13.3% and the maximum is 2019Q3 at 69.7%.

No quarter since 2019 has sustained compliance above 70%. The moving average shows that post-COVID recovery was partial: the underlying trend stabilized below 40% rather than returning to pre-2020 levels. Volatility increases again from 2025 onward.

---

### Page 4 — Valid WARN Filings per Quarter
<img width="965" height="743" alt="image" src="https://github.com/user-attachments/assets/fa340116-0ac6-4e01-8054-fdcf86d86cf7" />

**Data file**: `data_exports/03_quarterly_trend.csv`

A bar chart shows the count of valid WARN events per quarter. Bars exceeding twice the quarterly mean are highlighted and labeled. The quarterly mean (47 events) is shown as a red dashed line.

2020Q1 and 2020Q2 are the only quarters in the dataset to exceed twice the mean, confirming the COVID-driven spike was structurally distinct from normal variation. Outside of COVID, quarterly volume fluctuates around the mean with no sustained directional trend until 2025, when volume begins rising incrementally.

---

### Page 5 — WDA Regional Compliance Profile
<img width="923" height="717" alt="image" src="https://github.com/user-attachments/assets/23d3e1cd-f6e8-4dbf-b359-245bad0bd704" />

**Data file**: `data_exports/04a_wda_compliance.csv`

A horizontal bar chart ranks all 21 Texas Workforce Development Areas by 60-day compliance rate. The top 5 and bottom 5 WDAs are highlighted. Each bar is labeled with the compliance rate and valid event count.

No WDA in Texas exceeds 50% compliance. North Central Texas (DFW) leads at 47.4%, while Coastal Bend is lowest at 15.8%. Gulf Coast (Houston) has the largest sample in the dataset at 341 valid events with a compliance rate of 39.9%, confirming that low compliance in that region is structural rather than incidental.

---

### Page 6 — Compliance vs. Layoff Scale
<img width="947" height="747" alt="image" src="https://github.com/user-attachments/assets/834cd527-a5b4-46bd-aa65-c26dd1a22203" />

**Data file**: `data_exports/04b_wda_scatter.csv`

A scatter plot maps WDAs on two axes: 60-day compliance rate (x) and average layoff size in workers (y). Bubble size is proportional to the total event count for that WDA. Top 5 and bottom 5 compliance WDAs are highlighted; all others are shown in gray.

There is no strong correlation between compliance rate and average layoff size across WDAs. Low compliance regions do not systematically produce larger layoffs. Coastal Bend combines below-average layoff size with the lowest compliance rate, while Gulf Coast combines near-average layoff size with below-average compliance and the largest event volume.

---

### Page 7 — Top 15 by Workers Displaced
<img width="909" height="712" alt="image" src="https://github.com/user-attachments/assets/452d9296-30f9-4808-b9c5-327e948247cd" />

**Data file**: `data_exports/05a_cohort_top15.csv`

A horizontal bar chart ranks the 15 companies (among those with 4 or more WARN filings) by cumulative workers displaced. Zachry Industrial and American Airlines are highlighted; the second-ranked entity is highlighted as a reference point.

Zachry Industrial displaced 4,410 workers across 4 large industrial construction project completions. American Airlines displaced 2,811 workers across 5 filings with 0% compliance — all filings failed the 60-day threshold. Southwest Key Programs, a federal-grant-dependent nonprofit, displaced 1,300 workers with a 93.3% compliance rate, illustrating that government contract conditions create strong compliance incentives. The cohort as a whole does not follow a uniform behavioral pattern.

---

### Page 8 — Compliance vs. Lead Days by Company
<img width="939" height="733" alt="image" src="https://github.com/user-attachments/assets/0853cebc-4655-4e96-865b-aa5b8ab4e5c4" />

**Data file**: `data_exports/05b_cohort_scatter.csv`

A scatter plot maps each company in the repeat-offender cohort (4+ events) on two axes: 60-day compliance rate (x) and average notice lead days (y). Bubble size reflects total workers displaced. The top 5 and bottom 5 compliance companies are highlighted; all others are gray. No text labels are shown — color alone identifies the extreme groups.

Companies clustered at 0% compliance have never once filed within the 60-day threshold across 4 or more events, indicating a structural behavioral pattern rather than oversight. Several large-displacement companies appear in the bottom-5 compliance group, combining high workforce impact with consistent non-compliance.

---

### Page 9 — Distribution of Repeat Filing Frequency
<img width="961" height="751" alt="image" src="https://github.com/user-attachments/assets/1c95c3a8-1c57-4cbd-9969-a63222c71fa7" />

**Data file**: `data_exports/05c_cohort_event_distribution.csv`

A bar chart shows how many companies appear at each filing frequency — exactly twice, three times, four times, and so on. The most frequent bucket is highlighted.

The majority of repeat filers appear exactly twice, suggesting a one-time structural change rather than persistent restructuring behavior. The distribution has a long right tail, extending to companies with 24 or more filings. 192 companies appear 2 or more times; approximately 17% of those appear 4 or more times and constitute the formal analysis cohort used in Pages 7 and 8.

---

### Page 10 — Repeat Filings by Industry
<img width="921" height="714" alt="image" src="https://github.com/user-attachments/assets/e5a020c0-6154-4b10-a5d0-63acb94155a1" />

**Data file**: `data_exports/05d_cohort_industry.csv`

A horizontal bar chart shows total WARN events and company count for each industry within the repeat-offender cohort (2+ filings). Total events are shown as filled bars; company count is shown as an outline overlay on the same bars. Public/Nonprofit, Retail & Food, and Logistics are highlighted; all other industries are shown in gray.

Retail & Food leads in total repeat-offender events, driven primarily by franchise-level closures. Logistics shows a high company count relative to its event total, meaning many different logistics companies each filed a small number of times rather than a few companies filing many times. Manufacturing appears near the bottom of this chart, consistent with its stronger compliance pattern visible in Pages 2 and 5.

---

### Page 11 — Annual Retroactive Filing Volume
<img width="873" height="678" alt="image" src="https://github.com/user-attachments/assets/4bbd2dc3-09ec-48e8-9dbb-f762a61541bd" />

**Data file**: `data_exports/06a_retro_yearly.csv`

A bar chart shows the count of retroactive filings (filed after layoff date) by year from 2019 through 2026. The 2020 bar is highlighted. A trend line fitted to 2021–2026 data is overlaid as a dashed line.

640 of 807 total retroactive filings (79.3%) occurred in 2020 alone, reflecting widespread invocation of the "unforeseeable business circumstances" WARN exception during COVID. Outside of COVID, the normal range is 12–34 filings per year. The 2025 count of 56 filings is the second-highest year in the dataset excluding COVID. The post-2021 trend line slopes upward, indicating that exception-clause use has not returned to pre-COVID baseline levels.

---

### Page 12 — How Late Are Retroactive Filings?
<img width="972" height="750" alt="image" src="https://github.com/user-attachments/assets/a992cb39-ba8c-4cdb-be4a-356a62ce52a3" />

**Data file**: `data_exports/06b_retro_delay_distribution.csv`

A histogram shows the distribution of delay between layoff date and notice date across all 807 retroactive filings (capped at 365 days). Each bin is labeled with its count. The median and mean delay are marked as vertical reference lines.

The distribution is right-skewed. The tallest bin concentrates near 0–10 days, meaning the majority of retroactive filers submitted notice within days of the layoff date. A long right tail indicates that a meaningful subset of filers delayed 90 days or more. The mean exceeds the median due to these extreme delay cases.

---

### Page 13 — Industry Use of Exception Clause
<img width="912" height="714" alt="image" src="https://github.com/user-attachments/assets/ca244bb6-1fde-4070-a21f-d67924843871" />

**Data file**: `data_exports/06c_retro_industry.csv`

A horizontal bar chart ranks industries by the count of retroactive filings. Retail & Food is the top user; Logistics, Public/Nonprofit, and Manufacturing are highlighted as secondary heavy users.

Retail & Food dominates retroactive filing volume, reflecting COVID-driven store and restaurant closures. Logistics reflects supply chain and transportation company failures in 2020. Manufacturing's presence in the middle of the distribution is notable given its stronger compliance profile on Pages 2 and 5 — it suggests that manufacturing firms, despite better advance-notice practices overall, also invoked the exception clause when facing sudden macro shocks. Healthcare shows relatively low retroactive volume given the scale of COVID's impact on the sector.

---

### Page 14 — Layoff Size: Valid vs. Retroactive
<img width="953" height="746" alt="image" src="https://github.com/user-attachments/assets/48e57c1e-802b-4054-8936-7b07721e339c" />

**Data file**: `data_exports/06d_retro_size_compare.csv`

A side-by-side boxplot compares the distribution of layoff size (workers per event) between valid filings and retroactive filings. Outliers are suppressed. Each box shows the median value inside and P25/P75 labels outside.

| Statistic | Valid Filings | Retroactive |
|---|---:|---:|
| n | 1,524 | 807 |
| Median | 60 | 70 |
| P25 | 50 | 52 |
| P75 | 100 | 120 |

Retroactive filings are associated with modestly larger layoff events on average. The IQR is wider for retroactive filings, indicating more variance in the size of events invoking the exception clause. The pattern is consistent with the exception being used across a range of event sizes rather than exclusively for large-scale emergencies.



---

## 5. Limitations

**Small sample WDAs**: 65.5% of WDAs have fewer than 30 valid events. At n=10, a 30% observed rate carries a 95% confidence interval of approximately ±25 percentage points. WDA-level conclusions with small samples are directional, not definitive.

**Industry classifier accuracy**: The keyword-based classifier has not been validated against ground truth. 494 low-confidence classifications (score ≤4), approximately 21% of the dataset, may contain noise.

**Metro vs. non-metro gap is a composition effect**: Within-industry comparison reduces or reverses the metro/non-metro compliance gap. Metro regions concentrate more short-notice industries (Retail/Food, Logistics). The difference reflects structural industry mix, not regional behavioral differences.

**WARN Act selection bias**: Only sites with 100+ employees laying off 50+ are covered. Small-establishment closures are absent from the data entirely.

**Period asymmetry**: 2020 accounts for 51.7% of all events. Single-number aggregate statistics carry residual COVID influence.

**Correlation, not causation**: All findings are observational.

---

## 6. Reproducibility

### File Structure

```
texas-warn-er-intelligence/
├── README.md
├── data/
│   └── warn_clean.csv                     (23-column cleaned dataset, 2,340 rows)
├── scripts/
│   ├── build_report.py                    (generates 14-page PDF report)
│   └── extract_report_data.py             (extracts per-chart CSV files)
├── reports/
│   └── Texas_WARN_ER_Intelligence_Report.pdf
└── data_exports/
    ├── 01_kpi_summary.csv
    ├── 02_industry_year_heatmap.csv
    ├── 03_quarterly_trend.csv
    ├── 04a_wda_compliance.csv
    ├── 04b_wda_scatter.csv
    ├── 05a_cohort_top15.csv
    ├── 05b_cohort_scatter.csv
    ├── 05c_cohort_event_distribution.csv
    ├── 05d_cohort_industry.csv
    ├── 06a_retro_yearly.csv
    ├── 06b_retro_delay_distribution.csv
    ├── 06b2_retro_delay_stats.csv
    ├── 06c_retro_industry.csv
    └── 06d_retro_size_compare.csv
```

### Commands

```bash
# Extract per-chart data
python scripts/extract_report_data.py --input data/warn_clean.csv --output data_exports/

# Build PDF report
python scripts/build_report.py --input data/warn_clean.csv --output reports/
```

### Dependencies

```
Python 3.10+
pandas
numpy
matplotlib
pypdf
```

---

**Data Source**: Texas Workforce Commission — https://www.twc.texas.gov/
**License**: Free use for analytical purposes. Data source attribution required.
