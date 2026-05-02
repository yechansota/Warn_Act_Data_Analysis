"""
================================================================================
build_report.py  -  Texas WARN Act ER Risk Intelligence Report
================================================================================
Usage:
    python build_report.py
    python build_report.py --input warn_clean.csv --output ./reports
Output:
    Texas_WARN_ER_Intelligence_Report.pdf
    report_pages/page1.pdf  ~ page15.pdf  (individual charts)
================================================================================
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from pypdf import PdfWriter

GT_GOLD    = "#B3A369"
GT_NAVY    = "#003057"
GT_RED     = "#C8102E"
GT_GRAY_DK = "#54585A"
GT_GRAY_LT = "#C7C7C7"
GT_LGRAY   = "#E8E6DD"
GT_WHITE   = "#FFFFFF"

DTYPES = {
    "flag_year_typo": "Int64", "flag_retroactive": "Int64",
    "flag_valid": "Int64", "lead_days": "Int64",
    "lead_days_short": "Int64", "layoff_count": "Int64",
    "same_company_cluster": "Int64", "county_warn_count": "Int64",
    "wda_warn_count": "Int64", "notice_year": "Int64",
    "industry_score": "Int64",
}

INDUSTRIES = [
    "Manufacturing", "Energy", "Technology_IT",
    "Logistics_Transportation", "Healthcare", "Finance",
    "Construction_Real_Estate", "Public_Nonprofit",
    "Retail_Food", "Staffing_Services",
]

IND_LABELS = {
    "Manufacturing": "Manufacturing", "Energy": "Energy",
    "Technology_IT": "Tech / IT",
    "Logistics_Transportation": "Logistics",
    "Healthcare": "Healthcare", "Finance": "Finance",
    "Construction_Real_Estate": "Construction",
    "Public_Nonprofit": "Public / Nonprofit",
    "Retail_Food": "Retail & Food",
    "Staffing_Services": "Staffing & Svcs",
}

IND_SHORT = {
    "Retail_Food": "Retail & Food", "Technology_IT": "Tech/IT",
    "Logistics_Transportation": "Logistics",
    "Healthcare": "Healthcare", "Energy": "Energy",
    "Manufacturing": "Manufacturing",
    "Staffing_Services": "Staffing",
    "Public_Nonprofit": "Public/NP",
    "Construction_Real_Estate": "Const.", "Finance": "Finance",
    "Other": "Other", "Unknown": "Unknown",
}

FOOTER = "Source: TWC WARN Notices  |  GT MS Analytics Portfolio"


def setup_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.facecolor": GT_WHITE, "figure.facecolor": GT_WHITE,
        "axes.edgecolor": GT_GRAY_LT, "axes.labelcolor": GT_GRAY_DK,
        "xtick.color": GT_GRAY_DK, "ytick.color": GT_GRAY_DK,
        "text.color": GT_NAVY, "grid.color": GT_GRAY_LT,
        "grid.linewidth": 0.4,
        "axes.spines.top": False, "axes.spines.right": False,
    })


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col, dtype in DTYPES.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(dtype)
    return df


def add_footer(fig, page_label):
    fig.text(0.5, 0.01, f"{FOOTER}  |  {page_label}",
             ha="center", fontsize=8, color=GT_GRAY_DK)


# ════════════════════════════════════════════════════════════
# PAGE 1 - Cover
# ════════════════════════════════════════════════════════════
def build_page1(df: pd.DataFrame, out: Path):
    valid = df[df["flag_valid"] == 1]
    kpi = {
        "total": len(df),
        "valid": len(valid),
        "total_layoffs": int(df["layoff_count"].sum()),
        "pct_short": round((valid["lead_days_short"] == 1).mean() * 100, 1),
        "avg_lead": round(valid["lead_days"].mean(), 1),
    }
    fig = plt.figure(figsize=(11, 8.5), facecolor=GT_WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0.78), 1, 0.22, color=GT_NAVY))
    ax.add_patch(plt.Rectangle((0, 0.76), 1, 0.02, color=GT_GOLD))
    ax.text(0.06, 0.895, "TEXAS WARN ACT", fontsize=28,
            fontweight="bold", color=GT_WHITE, va="center")
    ax.text(0.06, 0.825, "ER RISK INTELLIGENCE REPORT", fontsize=16,
            color=GT_GOLD, va="center", fontweight="bold")
    ax.text(0.06, 0.70,
            "Labor Market Compliance Benchmarking for\n"
            "Union Prevention & Proactive ER Strategy",
            fontsize=13, color=GT_NAVY, va="top", linespacing=1.6)
    facts = [
        (f"{kpi['total']:,}", "Total WARN filings\n2019-2026"),
        (f"{kpi['valid']:,}", "Valid filings\nused in analysis"),
        (f"{kpi['total_layoffs']:,}", "Workers displaced\nstatewide"),
        (f"{kpi['pct_short']}%", "Filed under 60-day\nlegal threshold"),
        (f"{kpi['avg_lead']} d", "Avg notice lead\n(valid only)"),
    ]
    fw = 0.176
    for i, (v, lab) in enumerate(facts):
        x = 0.06 + i * (fw + 0.005)
        ax.add_patch(plt.Rectangle((x, 0.42), fw, 0.18, color=GT_LGRAY))
        ax.add_patch(plt.Rectangle((x, 0.58), fw, 0.02, color=GT_GOLD))
        ax.text(x + fw / 2, 0.54, v, fontsize=15, fontweight="bold",
                color=GT_NAVY, ha="center", va="center")
        ax.text(x + fw / 2, 0.455, lab, fontsize=8, color=GT_GRAY_DK,
                ha="center", va="center", linespacing=1.4)
    sections = [
        "01  Industry x Year Compliance Heatmap",
        "02  Quarterly Compliance Rate vs. Economic Cycles",
        "03  Valid WARN Filings per Quarter",
        "04  WDA Regional Compliance Profile",
        "05  Compliance vs. Layoff Scale",
        "06  Top 15 by Workers Displaced",
        "07  Compliance vs. Lead Days by Company",
        "08  Distribution of Repeat Filing Frequency",
        "09  Repeat Filings by Industry",
        "10  Annual Retroactive Filing Volume",
        "11  How Late Are Retroactive Filings",
        "12  Industry Use of Exception Clause",
        "13  Layoff Size: Valid vs. Retroactive",
        "14  ER Strategy Implications",
    ]
    ax.text(0.06, 0.38, "Contents", fontsize=10, fontweight="bold", color=GT_NAVY)
    ax.add_patch(plt.Rectangle((0.06, 0.365), 0.10, 0.002, color=GT_GOLD))
    for i, s in enumerate(sections[:7]):
        ax.text(0.06, 0.33 - i * 0.034, s, fontsize=8.5, color=GT_GRAY_DK)
    for i, s in enumerate(sections[7:]):
        ax.text(0.54, 0.33 - i * 0.034, s, fontsize=8.5, color=GT_GRAY_DK)
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.04, color=GT_LGRAY))
    ax.text(0.06, 0.02,
            "GT MS Analytics Portfolio Project  |  ER Risk Intelligence Series",
            fontsize=7.5, color=GT_GRAY_DK, va="center")
    ax.text(0.94, 0.02, "2026", fontsize=7.5, color=GT_GRAY_DK, va="center", ha="right")
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 1: Cover")


# ════════════════════════════════════════════════════════════
# PAGE 2 - Heatmap
# ════════════════════════════════════════════════════════════
def build_page2(df: pd.DataFrame, out: Path):
    valid = df[df["flag_valid"] == 1]
    years = list(range(2019, 2026))
    heat = pd.DataFrame(index=INDUSTRIES, columns=years, dtype=float)
    cnt  = pd.DataFrame(index=INDUSTRIES, columns=years, dtype=float)
    for ind in INDUSTRIES:
        for yr in years:
            sub = valid[(valid["industry_final"] == ind) & (valid["notice_year"] == yr)]
            n = len(sub)
            heat.loc[ind, yr] = round((sub["lead_days_short"] == 0).mean() * 100, 1) if n >= 3 else np.nan
            cnt.loc[ind, yr] = n
    heat.index = [IND_LABELS.get(i, i) for i in heat.index]
    cnt.index  = [IND_LABELS.get(i, i) for i in cnt.index]
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    vals = heat.values.astype(float)
    cmap = LinearSegmentedColormap.from_list("gt_heatmap", [
        (0.0, GT_NAVY), (0.35, "#6A7F9A"),
        (0.5, "#D6D2C4"), (0.65, "#C9BA8A"), (1.0, GT_GOLD)
    ], N=256)
    im = ax.imshow(vals, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, fontsize=10)
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=10)
    ax.set_xlabel("Notice Year", fontsize=10, color=GT_GRAY_DK, labelpad=8)
    for i in range(len(heat.index)):
        for j in range(len(years)):
            v = vals[i, j]
            n = cnt.values[i, j]
            if not np.isnan(v):
                tc = GT_WHITE if (v < 30 or v > 75) else GT_NAVY
                ax.text(j, i - 0.1, f"{v:.0f}%", ha="center", va="center",
                        fontsize=9, color=tc, fontweight="bold")
                ax.text(j, i + 0.25, f"n={int(n)}", ha="center", va="center",
                        fontsize=6.5, color=tc, alpha=0.85)
            else:
                ax.text(j, i, "N/A", ha="center", va="center",
                        fontsize=8, color=GT_GRAY_LT)
    ax.add_patch(plt.Rectangle((0.5, -0.5), 1, len(heat.index),
                 fill=False, edgecolor=GT_RED, linewidth=2.5, zorder=5))
    for i in range(len(heat.index) + 1):
        ax.axhline(i - 0.5, color=GT_WHITE, linewidth=1.5)
    for j in range(len(years) + 1):
        ax.axvline(j - 0.5, color=GT_WHITE, linewidth=1.5)
    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.ax.tick_params(labelsize=8.5, colors=GT_GRAY_DK)
    cbar.set_label("60-day Compliance Rate (%)", fontsize=9, color=GT_GRAY_DK, labelpad=8)
    ax.set_title("01  Industry x Year - 60-Day Compliance Rate Heatmap",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=14)
    add_footer(fig, "p.2")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 2: Heatmap")

# ════════════════════════════════════════════════════════════
# PAGE 3 - Quarterly Compliance Rate (top chart only)
# ════════════════════════════════════════════════════════════
def build_page3(df: pd.DataFrame, out: Path):
    valid = df[(df["flag_valid"] == 1) &
               (df["notice_year"] >= 2019) &
               (df["notice_year"] <= 2025)]
    qtr = valid.groupby("notice_quarter").agg(
        count=("lead_days", "count"),
        compliance_rate=("lead_days_short", lambda x: (x == 0).mean() * 100)
    ).reset_index()
    qtr = qtr[qtr["notice_quarter"] <= "2025Q4"].reset_index(drop=True)
    labels = qtr["notice_quarter"].tolist()
    comp   = qtr["compliance_rate"].values
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    covid_s = labels.index("2020Q1"); covid_e = labels.index("2020Q2")
    ax.axvspan(covid_s - 0.5, covid_e + 0.5, color=GT_LGRAY, alpha=0.6, zorder=0)
    rate_s = labels.index("2022Q1"); rate_e = labels.index("2023Q4")
    ax.axvspan(rate_s - 0.5, rate_e + 0.5, color=GT_LGRAY, alpha=0.3, zorder=0)
    ax.axhline(60, color=GT_RED, linewidth=1.2, linestyle="--", alpha=0.7, zorder=3)
    ax.text(len(labels) - 0.5, 62, "60-day legal floor",
            fontsize=8, color=GT_RED, ha="right")
    ax.plot(x, comp, color=GT_NAVY, linewidth=2.2, zorder=4,
            marker="o", markersize=4.5, markerfacecolor=GT_WHITE,
            markeredgecolor=GT_NAVY, markeredgewidth=1.5,
            label="Quarterly compliance rate")
    ma = pd.Series(comp).rolling(4, center=True).mean()
    ax.plot(x, ma, color=GT_GOLD, linewidth=2.2, alpha=0.9, zorder=3,
            label="4-quarter moving avg")
    mn = int(np.nanargmin(comp)); mx = int(np.nanargmax(comp))
    ax.scatter([mn], [comp[mn]], color=GT_RED, s=80, zorder=6)
    ax.text(mn, comp[mn] - 8, f"{comp[mn]:.1f}%\n({labels[mn]})",
            ha="center", fontsize=7.5, color=GT_RED, fontweight="bold")
    ax.scatter([mx], [comp[mx]], color=GT_NAVY, s=80, zorder=6)
    ax.text(mx, comp[mx] + 4, f"{comp[mx]:.1f}%\n({labels[mx]})",
            ha="center", fontsize=7.5, color=GT_NAVY, fontweight="bold")
    ax.text((covid_s + covid_e) / 2, 5, "COVID\nShock",
            fontsize=8, ha="center", color=GT_GRAY_DK, fontweight="bold")
    ax.text((rate_s + rate_e) / 2, 5, "Fed Rate\nHike Cycle",
            fontsize=8, ha="center", color=GT_GRAY_DK, fontweight="bold", alpha=0.8)
    ax.set_xlim(-0.5, len(labels) - 0.5)
    ax.set_ylim(0, 95)
    ax.set_ylabel("60-day compliance rate (%)", fontsize=10)
    ax.set_xticks(x[::2])
    ax.set_xticklabels(labels[::2], rotation=45, ha="right", fontsize=8.5)
    ax.grid(axis="y", alpha=0.4)
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    ax.set_title("02  Quarterly 60-Day Compliance Rate vs. Economic Cycles",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    add_footer(fig, "p.3")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 3: Quarterly Compliance Rate")


# ════════════════════════════════════════════════════════════
# PAGE 4 - Valid WARN Filings per Quarter (bottom chart only)
# ════════════════════════════════════════════════════════════
def build_page4(df: pd.DataFrame, out: Path):
    valid = df[(df["flag_valid"] == 1) &
               (df["notice_year"] >= 2019) &
               (df["notice_year"] <= 2025)]
    qtr = valid.groupby("notice_quarter").agg(
        count=("lead_days", "count"),
    ).reset_index()
    qtr = qtr[qtr["notice_quarter"] <= "2025Q4"].reset_index(drop=True)
    labels = qtr["notice_quarter"].tolist()
    counts = qtr["count"].values
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    mean_count = counts.mean()
    bar_colors = [GT_GOLD if c > mean_count * 2 else GT_GRAY_LT for c in counts]
    ax.bar(x, counts, color=bar_colors, edgecolor="none", width=0.7, zorder=2)
    for i, c in enumerate(counts):
        if c > mean_count * 2:
            ax.text(i, c + 8, f"{int(c)}", ha="center", fontsize=9,
                    color=GT_GOLD, fontweight="bold")
    ax.plot(x, counts, color=GT_GRAY_DK, linewidth=1.2, alpha=0.4, zorder=3,
            marker="o", markersize=3,
            markerfacecolor=GT_GRAY_DK, markeredgecolor="none")
    ax.axhline(mean_count, color=GT_RED, linewidth=1.5,
               linestyle="--", alpha=0.85, zorder=4)
    ax.text(len(labels) - 0.3, mean_count + 6,
            f"Avg: {mean_count:.0f}", fontsize=9, color=GT_RED,
            fontweight="bold", ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=GT_WHITE,
                      edgecolor=GT_RED, linewidth=0.8))
    ax.set_xlim(-0.5, len(labels) - 0.5)
    ax.set_ylabel("WARN filings (valid events)", fontsize=10)
    ax.set_xticks(x[::2])
    ax.set_xticklabels(labels[::2], rotation=45, ha="right", fontsize=8.5)
    ax.grid(axis="y", alpha=0.4)
    ax.set_title("03  Valid WARN Filings per Quarter",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    add_footer(fig, "p.4")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 4: Valid WARN Filings per Quarter")


# ════════════════════════════════════════════════════════════
# PAGE 5 - WDA Bar Chart
# ════════════════════════════════════════════════════════════
def build_page5(df: pd.DataFrame, out: Path):
    valid = df[df["flag_valid"] == 1]
    wda = valid.groupby("WDA_NAME").agg(
        count=("lead_days", "count"),
        compliance_rate=("lead_days_short",
                         lambda x: round((x == 0).mean() * 100, 1)),
        avg_layoff=("layoff_count", "mean"),
    ).reset_index().dropna()
    wda = wda[wda["count"] >= 10].sort_values(
        "compliance_rate", ascending=True).reset_index(drop=True)
    n = len(wda)
    top5_idx = list(range(n - 5, n))
    bot5_idx = list(range(0, 5))
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    bc = [GT_NAVY if i in top5_idx else GT_GOLD if i in bot5_idx
          else GT_GRAY_LT for i in range(n)]
    ax.barh(range(n), wda["compliance_rate"],
            color=bc, edgecolor="none", height=0.65)
    ax.set_yticks(range(n))
    ax.set_yticklabels(wda["WDA_NAME"], fontsize=9)
    for i, lbl in enumerate(ax.get_yticklabels()):
        if i in top5_idx:
            lbl.set_color(GT_NAVY); lbl.set_fontweight("bold")
        elif i in bot5_idx:
            lbl.set_color(GT_GOLD); lbl.set_fontweight("bold")
        else:
            lbl.set_color(GT_GRAY_DK)
    ax.axvline(60, color=GT_RED, linewidth=1.2, linestyle="--", alpha=0.7)
    ax.text(60.5, n - 1, "60d floor", fontsize=8, color=GT_RED)
    ax.set_xlim(0, 85)
    ax.set_xlabel("60-day compliance rate (%)", fontsize=10)
    for i, (v, nc) in enumerate(zip(wda["compliance_rate"], wda["count"])):
        c = GT_NAVY if i in top5_idx else GT_GOLD if i in bot5_idx else GT_GRAY_DK
        w = "bold" if (i in top5_idx or i in bot5_idx) else "normal"
        ax.text(v + 0.8, i, f"{v:.1f}%  (n={int(nc)})",
                va="center", fontsize=8, color=c, fontweight=w)
    ax.set_title("04  WDA Regional Compliance Profile",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    add_footer(fig, "p.5")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 5: WDA Bar Chart")


# ════════════════════════════════════════════════════════════
# PAGE 6 - Compliance vs Layoff Scale Scatter
# ════════════════════════════════════════════════════════════
def build_page6(df: pd.DataFrame, out: Path):
    valid = df[df["flag_valid"] == 1]
    wda = valid.groupby("WDA_NAME").agg(
        count=("lead_days", "count"),
        compliance_rate=("lead_days_short",
                         lambda x: round((x == 0).mean() * 100, 1)),
        avg_layoff=("layoff_count", "mean"),
    ).reset_index().dropna()
    wda = wda[wda["count"] >= 10].sort_values(
        "compliance_rate", ascending=True).reset_index(drop=True)
    top5_wda = wda.nlargest(5, "compliance_rate")["WDA_NAME"].tolist()
    bot5_wda = wda.nsmallest(5, "compliance_rate")["WDA_NAME"].tolist()
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    ax.scatter(wda["compliance_rate"], wda["avg_layoff"],
               c=GT_GRAY_LT, s=wda["count"] * 3,
               alpha=0.5, edgecolors="none", zorder=2)
    for w in top5_wda:
        r = wda[wda["WDA_NAME"] == w].iloc[0]
        ax.scatter(r["compliance_rate"], r["avg_layoff"],
                   c=GT_NAVY, s=r["count"] * 4, alpha=1.0,
                   edgecolors="none", zorder=5)
    for w in bot5_wda:
        r = wda[wda["WDA_NAME"] == w].iloc[0]
        ax.scatter(r["compliance_rate"], r["avg_layoff"],
                   c=GT_GOLD, s=r["count"] * 4, alpha=1.0,
                   edgecolors="none", zorder=5)
    ax.axvline(60, color=GT_RED, linewidth=1.2, linestyle="--", alpha=0.6)
    ax.text(60.5, ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] > 0 else 200,
            "60d floor", fontsize=8.5, color=GT_RED, va="top")
    ax.set_xlabel("60-day compliance rate (%)", fontsize=10)
    ax.set_ylabel("Avg layoff size (workers)", fontsize=10)
    ax.set_title("05  Compliance vs. Layoff Scale",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.grid(alpha=0.3)
    patches = [
        mpatches.Patch(color=GT_NAVY, label="Top 5 compliance"),
        mpatches.Patch(color=GT_GOLD, label="Bottom 5 compliance"),
        mpatches.Patch(color=GT_GRAY_LT, label="Other WDAs"),
    ]
    ax.legend(handles=patches, fontsize=9, frameon=False, loc="upper right")
    add_footer(fig, "p.6")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 6: Compliance vs Layoff Scale")


# ════════════════════════════════════════════════════════════
# PAGE 7 - Top 15 by Workers Displaced
# ════════════════════════════════════════════════════════════
def build_page7(df: pd.DataFrame, out: Path):
    co_raw = df[df["same_company_cluster"] == 1].copy()
    co = co_raw.groupby("company_normalized").agg(
        events=("lead_days", "size"),
        total_layoffs=("layoff_count", "sum"),
        avg_lead=("lead_days", "mean"),
        compliance_rate=("lead_days_short",
                         lambda x: (x == 0).mean() * 100 if x.notna().any() else np.nan),
        industry=("industry_final", "first"),
    ).reset_index()
    co["total_layoffs"] = pd.to_numeric(co["total_layoffs"], errors="coerce").fillna(0)
    co["compliance_rate"] = pd.to_numeric(co["compliance_rate"], errors="coerce")
    co["avg_lead"] = pd.to_numeric(co["avg_lead"], errors="coerce")
    top = co[co["events"] >= 4].copy().sort_values(
        "total_layoffs", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    top_co = top.iloc[0]["company_normalized"] if len(top) > 0 else None
    sec_co = top.iloc[1]["company_normalized"] if len(top) > 1 else None
    aa_co = None
    for nm in top["company_normalized"]:
        if "AMERICAN AIRLINES" in str(nm).upper():
            aa_co = nm
            break
    HIGHLIGHT_GOLD = {top_co, aa_co}
    HIGHLIGHT_GOLD.discard(None)
    labs = [n[:28] + ".." if len(str(n)) > 28 else str(n)
            for n in top["company_normalized"]]
    cc = [GT_GOLD if n in HIGHLIGHT_GOLD
          else GT_NAVY if n == sec_co
          else GT_GRAY_LT
          for n in top["company_normalized"]]
    ax.barh(range(len(top)), top["total_layoffs"],
            color=cc, height=0.65, edgecolor="none")
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labs, fontsize=9.5)
    for i, lbl in enumerate(ax.get_yticklabels()):
        n = top.iloc[i]["company_normalized"]
        if n in HIGHLIGHT_GOLD: lbl.set_color(GT_GOLD); lbl.set_fontweight("bold")
        elif n == sec_co:       lbl.set_color(GT_NAVY); lbl.set_fontweight("bold")
        else:                   lbl.set_color(GT_GRAY_DK)
    for i, v in enumerate(top["total_layoffs"]):
        n = top.iloc[i]["company_normalized"]
        c = GT_GOLD if n in HIGHLIGHT_GOLD else GT_NAVY if n == sec_co else GT_GRAY_DK
        w = "bold" if (n in HIGHLIGHT_GOLD or n == sec_co) else "normal"
        ax.text(v + 20, i, f"{int(v):,}", va="center", fontsize=8.5, color=c, fontweight=w)
    ax.set_xlabel("Total workers displaced", fontsize=10)
    ax.set_title("06  Top 15 by Workers Displaced",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.grid(axis="x", alpha=0.3)
    add_footer(fig, "p.7")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 7: Top 15 Workers Displaced")


# ════════════════════════════════════════════════════════════
# PAGE 8 - Compliance vs Lead Days Scatter
# ════════════════════════════════════════════════════════════
def build_page8(df: pd.DataFrame, out: Path):
    co_raw = df[df["same_company_cluster"] == 1].copy()
    co = co_raw.groupby("company_normalized").agg(
        events=("lead_days", "size"),
        total_layoffs=("layoff_count", "sum"),
        avg_lead=("lead_days", "mean"),
        compliance_rate=("lead_days_short",
                         lambda x: (x == 0).mean() * 100 if x.notna().any() else np.nan),
    ).reset_index()
    co["total_layoffs"] = pd.to_numeric(co["total_layoffs"], errors="coerce").fillna(0)
    co["compliance_rate"] = pd.to_numeric(co["compliance_rate"], errors="coerce")
    co["avg_lead"] = pd.to_numeric(co["avg_lead"], errors="coerce")
    co_all = co[co["events"] >= 4].copy().dropna(subset=["compliance_rate", "avg_lead"])
    top5_c = co_all.nlargest(5, "compliance_rate")["company_normalized"].tolist()
    bot5_c = co_all.nsmallest(5, "compliance_rate")["company_normalized"].tolist()
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    sizes = co_all["total_layoffs"].clip(10) / 30
    mask_g = ~co_all["company_normalized"].isin(top5_c + bot5_c)
    ax.scatter(co_all.loc[mask_g, "compliance_rate"],
               co_all.loc[mask_g, "avg_lead"],
               c=GT_GRAY_LT, s=sizes[mask_g] * 5, alpha=0.5,
               edgecolors="none", zorder=2)
    for w in top5_c:
        r = co_all[co_all["company_normalized"] == w].iloc[0]
        ax.scatter(r["compliance_rate"], r["avg_lead"],
                   c=GT_GOLD, s=max(r["total_layoffs"] / 30, 5) * 5,
                   alpha=1.0, edgecolors="none", zorder=5)
    for w in bot5_c:
        r = co_all[co_all["company_normalized"] == w].iloc[0]
        ax.scatter(r["compliance_rate"], r["avg_lead"],
                   c=GT_NAVY, s=max(r["total_layoffs"] / 30, 5) * 5,
                   alpha=1.0, edgecolors="none", zorder=5)
    ax.axvline(50, color=GT_RED, linewidth=1.2, linestyle="--", alpha=0.5)
    ax.axhline(60, color=GT_RED, linewidth=1.2, linestyle="--", alpha=0.5)
    ax.text(51, 5, "50% compliance", fontsize=8, color=GT_RED, alpha=0.7)
    ax.text(2, 62, "60-day floor", fontsize=8, color=GT_RED, alpha=0.7)
    ax.set_xlabel("Compliance rate (%)", fontsize=10)
    ax.set_ylabel("Avg notice lead days", fontsize=10)
    ax.set_title("07  Compliance vs. Lead Days by Company",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.grid(alpha=0.3)
    ax.set_xlim(-5, 110)
    add_footer(fig, "p.8")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 8: Compliance vs Lead Days")


# ════════════════════════════════════════════════════════════
# PAGE 9 - Distribution of Repeat Filing Frequency
# ════════════════════════════════════════════════════════════
def build_page9(df: pd.DataFrame, out: Path):
    co_raw = df[df["same_company_cluster"] == 1].copy()
    co = co_raw.groupby("company_normalized").agg(
        events=("lead_days", "size"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    ec = co["events"].value_counts().sort_index()
    max_v = ec.max()
    bc3 = [GT_GOLD if v == max_v else GT_GRAY_LT for v in ec.values]
    ax.bar(ec.index, ec.values, color=bc3, edgecolor="none", width=0.7)
    for xv, yv in zip(ec.index, ec.values):
        c = GT_GOLD if yv == max_v else GT_GRAY_DK
        w = "bold" if yv == max_v else "normal"
        ax.text(xv, yv + 0.5, str(yv), ha="center", fontsize=10, color=c, fontweight=w)
    ax.set_xlabel("Number of WARN Events per Company", fontsize=10)
    ax.set_ylabel("Company Count", fontsize=10)
    ax.set_title("08  Distribution of Repeat Filing Frequency",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.grid(axis="y", alpha=0.4)
    add_footer(fig, "p.9")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 9: Repeat Filing Distribution")


# ════════════════════════════════════════════════════════════
# PAGE 10 - Repeat Filings by Industry
# ════════════════════════════════════════════════════════════
def build_page10(df: pd.DataFrame, out: Path):
    co_raw = df[df["same_company_cluster"] == 1].copy()
    co = co_raw.groupby("company_normalized").agg(
        events=("lead_days", "size"),
        industry=("industry_final", "first"),
    ).reset_index()
    ind_d = co[co["events"] >= 2].groupby("industry").agg(
        companies=("company_normalized", "count"),
        total_events=("events", "sum")
    ).sort_values("total_events", ascending=True)
    ind_d = ind_d[ind_d.index != "Unknown"]
    HIGHLIGHT_INDS = {"Public_Nonprofit", "Retail_Food", "Logistics_Transportation"}
    bc4 = [GT_NAVY if i in HIGHLIGHT_INDS else GT_GRAY_LT for i in ind_d.index]
    yl = [IND_SHORT.get(i, i) for i in ind_d.index]
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    ax.barh(range(len(ind_d)), ind_d["total_events"],
            color=bc4, height=0.65, edgecolor="none")
    ax.barh(range(len(ind_d)), ind_d["companies"],
            color="none", height=0.65, edgecolor=GT_GOLD, linewidth=1.5)
    ax.set_yticks(range(len(ind_d)))
    ax.set_yticklabels(yl, fontsize=10)
    for i, lbl in enumerate(ax.get_yticklabels()):
        ind_n = ind_d.index[i]
        if ind_n in HIGHLIGHT_INDS: lbl.set_color(GT_NAVY); lbl.set_fontweight("bold")
        else:                       lbl.set_color(GT_GRAY_DK)
    for i, (ev, cn) in enumerate(zip(ind_d["total_events"], ind_d["companies"])):
        ind_n = ind_d.index[i]
        c = GT_NAVY if ind_n in HIGHLIGHT_INDS else GT_GRAY_DK
        w = "bold" if ind_n in HIGHLIGHT_INDS else "normal"
        ax.text(ev + 0.3, i, f"{int(ev)} events  ({int(cn)} cos.)",
                va="center", fontsize=8.5, color=c, fontweight=w)
    ax.set_xlabel("Count", fontsize=10)
    ax.set_title("09  Repeat Filings by Industry",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.legend(["Total events", "Company count"], fontsize=9, frameon=False)
    ax.grid(axis="x", alpha=0.3)
    ax.set_xlim(0, ind_d["total_events"].max() * 1.45)
    add_footer(fig, "p.10")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 10: Repeat Filings by Industry")


# ════════════════════════════════════════════════════════════
# PAGE 11 - Annual Retroactive Filing Volume
# ════════════════════════════════════════════════════════════
def build_page11(df: pd.DataFrame, out: Path):
    retro = df[df["flag_retroactive"] == 1].copy()
    retro_yr = retro.groupby("notice_year").size()
    years = list(retro_yr.index)
    counts_r = list(retro_yr.values)
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    bc = [GT_GOLD if y == 2020 else GT_GRAY_LT for y in years]
    ax.bar(range(len(years)), counts_r, color=bc, edgecolor="none")
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, fontsize=10)
    for i, c in enumerate(counts_r):
        clr = GT_GOLD if years[i] == 2020 else GT_GRAY_DK
        w = "bold" if years[i] == 2020 else "normal"
        ax.text(i, c + 10, str(c), ha="center", fontsize=10, color=clr, fontweight=w)
    ax.set_ylabel("Retroactive filings", fontsize=10)
    ax.set_title("10  Annual Retroactive Filing Volume",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.text(years.index(2020), counts_r[years.index(2020)] / 2,
            "COVID\nshock", ha="center", fontsize=9,
            color=GT_NAVY, fontweight="bold")
    ax.set_ylim(0, 780)
    ax.grid(axis="y", alpha=0.4)
    post_covid_years = [y for y in years if y >= 2021]
    post_covid_x = [years.index(y) for y in post_covid_years]
    post_covid_y = [counts_r[years.index(y)] for y in post_covid_years]
    if len(post_covid_x) >= 2:
        z = np.polyfit(post_covid_x, post_covid_y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(post_covid_x), max(post_covid_x), 100)
        ax.plot(x_line, p(x_line), color=GT_NAVY, linewidth=2,
                linestyle="--", alpha=0.7, label="Trend (2021+)")
        ax.legend(fontsize=9, frameon=False, loc="upper left")
    add_footer(fig, "p.11")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 11: Annual Retroactive Filing Volume")


# ════════════════════════════════════════════════════════════
# PAGE 12 - How Late Are Retroactive Filings
# ════════════════════════════════════════════════════════════
def build_page12(df: pd.DataFrame, out: Path):
    retro = df[df["flag_retroactive"] == 1].copy()
    retro["NOTICE_DATE_dt"] = pd.to_datetime(retro["NOTICE_DATE"])
    retro["LayOff_Date_dt"] = pd.to_datetime(retro["LayOff_Date"])
    retro["delay_days"] = (retro["NOTICE_DATE_dt"] - retro["LayOff_Date_dt"]).dt.days
    delay = retro["delay_days"].dropna()
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    delay_clip = delay.clip(0, 365)
    n_counts, bin_edges, bar_patches = ax.hist(
        delay_clip, bins=30, color=GT_NAVY, alpha=0.8,
        edgecolor=GT_WHITE, linewidth=0.5)
    max_count = n_counts.max()
    for count, patch in zip(n_counts, bar_patches):
        if count == max_count:
            patch.set_facecolor(GT_GOLD)
        if count > 0:
            ax.text(patch.get_x() + patch.get_width() / 2,
                    count + 1, str(int(count)),
                    ha="center", va="bottom", fontsize=7,
                    color=GT_GOLD if count == max_count else GT_GRAY_DK)
    ax.axvline(delay_clip.median(), color=GT_RED, linewidth=2,
               linestyle="--", label=f"Median: {delay_clip.median():.0f} days")
    ax.axvline(delay_clip.mean(), color=GT_GOLD, linewidth=2,
               linestyle="--", label=f"Mean: {delay_clip.mean():.0f} days")
    ax.set_xlabel("Days between layoff and notice (capped at 365)", fontsize=10)
    ax.set_ylabel("Count of filings", fontsize=10)
    ax.set_title("11  How Late Are Retroactive Filings?",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.legend(fontsize=9.5, frameon=False)
    ax.grid(axis="y", alpha=0.4)
    add_footer(fig, "p.12")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 12: How Late Are Retroactive Filings")


# ════════════════════════════════════════════════════════════
# PAGE 13 - Industry Use of Exception Clause
# ════════════════════════════════════════════════════════════
def build_page13(df: pd.DataFrame, out: Path):
    KEEP = ["Retail_Food", "Logistics_Transportation", "Healthcare",
            "Manufacturing", "Energy", "Public_Nonprofit",
            "Technology_IT", "Staffing_Services",
            "Construction_Real_Estate", "Finance"]
    retro = df[df["flag_retroactive"] == 1].copy()
    retro_ind = (retro[retro["industry_final"].isin(KEEP)]
                 .groupby("industry_final").size()
                 .sort_values(ascending=True))
    RETRO_GOLD = {"Retail_Food"}
    RETRO_NAVY = {"Logistics_Transportation", "Public_Nonprofit", "Manufacturing"}
    bc3 = [GT_GOLD if i in RETRO_GOLD
           else GT_NAVY if i in RETRO_NAVY
           else GT_GRAY_LT
           for i in retro_ind.index]
    ls3 = {"Retail_Food": "Retail & Food", "Technology_IT": "Tech/IT",
           "Logistics_Transportation": "Logistics",
           "Healthcare": "Healthcare", "Energy": "Energy",
           "Manufacturing": "Manufacturing",
           "Staffing_Services": "Staffing & Svcs",
           "Public_Nonprofit": "Public/NP",
           "Construction_Real_Estate": "Construction",
           "Finance": "Finance"}
    yl3 = [ls3.get(i, i) for i in retro_ind.index]
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    ax.barh(range(len(retro_ind)), retro_ind.values, color=bc3, edgecolor="none")
    ax.set_yticks(range(len(retro_ind)))
    ax.set_yticklabels(yl3, fontsize=10)
    for i, lbl in enumerate(ax.get_yticklabels()):
        ind_n = retro_ind.index[i]
        if ind_n in RETRO_GOLD:   lbl.set_color(GT_GOLD); lbl.set_fontweight("bold")
        elif ind_n in RETRO_NAVY: lbl.set_color(GT_NAVY); lbl.set_fontweight("bold")
        else:                     lbl.set_color(GT_GRAY_DK)
    for i, v in enumerate(retro_ind.values):
        ind_n = retro_ind.index[i]
        c = GT_GOLD if ind_n in RETRO_GOLD else GT_NAVY if ind_n in RETRO_NAVY else GT_GRAY_DK
        w = "bold" if (ind_n in RETRO_GOLD or ind_n in RETRO_NAVY) else "normal"
        ax.text(v + 2, i, str(v), va="center", fontsize=9, color=c, fontweight=w)
    ax.set_xlabel("Retroactive filings", fontsize=10)
    ax.set_title("12  Industry Use of Exception Clause",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.grid(axis="x", alpha=0.4)
    add_footer(fig, "p.13")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 13: Industry Use of Exception Clause")


# ════════════════════════════════════════════════════════════
# PAGE 14 - Layoff Size Valid vs Retroactive
# ════════════════════════════════════════════════════════════
def build_page14(df: pd.DataFrame, out: Path):
    retro = df[df["flag_retroactive"] == 1].copy()
    normal_sz = df[df["flag_valid"] == 1]["layoff_count"].dropna()
    retro_sz = retro["layoff_count"].dropna()
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor(GT_WHITE)
    bp = ax.boxplot([normal_sz.values, retro_sz.values],
                    positions=[1, 2], widths=0.6, patch_artist=True,
                    showfliers=False,
                    medianprops=dict(color=GT_WHITE, linewidth=2.5))
    for patch, color in zip(bp["boxes"], [GT_NAVY, GT_GOLD]):
        patch.set_facecolor(color); patch.set_edgecolor("none")
    for pos, data in [(1, normal_sz), (2, retro_sz)]:
        p25 = float(data.quantile(0.25))
        med = float(data.median())
        p75 = float(data.quantile(0.75))
        ax.text(pos, med, f"  {int(med)}", va="center", ha="left",
                fontsize=10, color=GT_WHITE, fontweight="bold")
        ax.text(pos + 0.33, p25, f"P25: {int(p25)}", va="center",
                fontsize=9, color=GT_GRAY_DK)
        ax.text(pos + 0.33, p75, f"P75: {int(p75)}", va="center",
                fontsize=9, color=GT_GRAY_DK)
    ax.set_xticks([1, 2])
    ax.set_xticklabels([
        f"Valid Filings\n(n={len(normal_sz):,})",
        f"Retroactive\n(n={len(retro_sz):,})"
    ], fontsize=11)
    ax.set_ylabel("Layoff size (workers)", fontsize=10)
    ax.set_title("13  Layoff Size: Valid vs. Retroactive",
                 fontsize=12, fontweight="bold", color=GT_NAVY, loc="left", pad=12)
    ax.set_ylim(0, 380)
    add_footer(fig, "p.14")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out, bbox_inches="tight", dpi=150)
    plt.close()
    print("  - Page 14: Layoff Size Valid vs Retroactive")

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Generate Texas WARN ER Intelligence Report PDF")
    parser.add_argument("--input", default="warn_clean.csv")
    parser.add_argument("--output", default=".")
    args = parser.parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output)
    pages_dir  = output_dir / "report_pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    if not input_path.exists():
        print(f"ERROR: input file not found - {input_path}")
        return
    setup_style()
    print(f"Loading {input_path}...")
    df = load_data(input_path)
    print(f"Loaded {len(df):,} records\n")
    print("Building pages...")
    build_page1 (df, pages_dir / "page01.pdf")
    build_page2 (df, pages_dir / "page02.pdf")
    build_page3 (df, pages_dir / "page03.pdf")
    build_page4 (df, pages_dir / "page04.pdf")
    build_page5 (df, pages_dir / "page05.pdf")
    build_page6 (df, pages_dir / "page06.pdf")
    build_page7 (df, pages_dir / "page07.pdf")
    build_page8 (df, pages_dir / "page08.pdf")
    build_page9 (df, pages_dir / "page09.pdf")
    build_page10(df, pages_dir / "page10.pdf")
    build_page11(df, pages_dir / "page11.pdf")
    build_page12(df, pages_dir / "page12.pdf")
    build_page13(df, pages_dir / "page13.pdf")
    build_page14(df, pages_dir / "page14.pdf")
    pdf_path = output_dir / "Texas_WARN_ER_Intelligence_Report.pdf"
    writer = PdfWriter()
    for i in range(1, 15):
        writer.append(str(pages_dir / f"page{i:02d}.pdf"))
    with open(pdf_path, "wb") as f:
        writer.write(f)
    size_kb = pdf_path.stat().st_size / 1024
    print(f"\nPDF saved: {pdf_path}")
    print(f"Size: {size_kb:.0f} KB  |  Pages: 15")


if __name__ == "__main__":
    main()