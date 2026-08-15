import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pakistan Cities Population 2026",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# THEME (Pakistan flag green + white)
# ----------------------------------------------------------------------------
PRIMARY_GREEN = "#01411C"   # dark Pakistan flag green
ACCENT_GREEN = "#046A38"    # medium green
LIGHT_GREEN = "#8FBF9F"     # soft green for backgrounds
WHITE = "#FFFFFF"
GOLD = "#D4AF37"            # subtle accent for highlights

GREEN_SEQUENTIAL = ["#EAF5EC", "#BFE0C8", "#8FBF9F", "#5E9E72", "#2E7D47", "#01411C"]
GREEN_DISCRETE = ["#01411C", "#046A38", "#2E8B57", "#5E9E72", "#8FBF9F", "#B7D8C0", "#D4AF37"]

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #F4FAF5;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {PRIMARY_GREEN};
    }}
    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {WHITE};
    }}
    h1, h2, h3 {{
        color: {PRIMARY_GREEN};
    }}
    .metric-card {{
        background-color: {WHITE};
        border: 1px solid {LIGHT_GREEN};
        border-left: 6px solid {ACCENT_GREEN};
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .metric-label {{
        font-size: 0.85rem;
        color: #4a4a4a;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .metric-value {{
        font-size: 1.6rem;
        color: {PRIMARY_GREEN};
        font-weight: 800;
    }}
    .metric-sub {{
        font-size: 0.85rem;
        color: #6a6a6a;
    }}
    .source-box {{
        background-color: {WHITE};
        border: 1px solid {LIGHT_GREEN};
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.9rem;
        color: #333;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_TEMPLATE = dict(
    plot_bgcolor=WHITE,
    paper_bgcolor=WHITE,
    font=dict(color="#1f2b1f", size=13),
    title_font=dict(color=PRIMARY_GREEN, size=18),
    margin=dict(l=10, r=10, t=60, b=10),
)


def style_fig(fig, height=460):
    fig.update_layout(**PLOTLY_TEMPLATE, height=height)
    fig.update_xaxes(showgrid=True, gridcolor="#E3EFE5")
    fig.update_yaxes(showgrid=True, gridcolor="#E3EFE5")
    return fig


# ----------------------------------------------------------------------------
# DATA LOADING + CLEANING (mirrors the notebook's cleaning steps)
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("population_pk.csv")

    # Robust cleaning: works whether pandas already parsed these as numeric
    # or left them as strings (pandas' string dtype varies by version).
    if not pd.api.types.is_numeric_dtype(df["2026 Population"]):
        df["2026 Population"] = (
            df["2026 Population"].astype(str).str.replace(",", "", regex=False).astype(int)
        )
    if not pd.api.types.is_numeric_dtype(df["Annual Change"]):
        df["Annual Change"] = (
            df["Annual Change"].astype(str).str.replace("%", "", regex=False).astype(float)
        )

    if "index" in df.columns:
        df.drop(columns="index", inplace=True)

    df["Population Share (%)"] = (
        df["2026 Population"] / df["2026 Population"].sum() * 100
    )

    def classify_city(population):
        if population >= 5_000_000:
            return "Mega City"
        elif population >= 1_000_000:
            return "Large City"
        elif population >= 500_000:
            return "Medium City"
        else:
            return "Small City"

    df["City Category"] = df["2026 Population"].apply(classify_city)
    return df


df = load_data()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="background: linear-gradient(90deg, {PRIMARY_GREEN}, {ACCENT_GREEN});
                padding: 26px 30px; border-radius: 14px; margin-bottom: 22px;">
        <h1 style="color:{WHITE}; margin:0;">🇵🇰 Pakistan Cities Population Dashboard — 2026</h1>
        <p style="color:{LIGHT_GREEN}; margin:6px 0 0 0; font-size:1.05rem;">
            Population estimates &amp; annual growth rates across 127 Pakistani cities
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🔎 Filters")

all_cities = sorted(df["City"].unique().tolist())
selected_cities = st.sidebar.multiselect(
    "Select cities (leave empty for all)",
    options=all_cities,
    default=[],
    help="Pick one or more cities to focus the whole dashboard on them.",
)

categories = ["Mega City", "Large City", "Medium City", "Small City"]
selected_categories = st.sidebar.multiselect(
    "City category",
    options=categories,
    default=categories,
)

pop_min, pop_max = int(df["2026 Population"].min()), int(df["2026 Population"].max())
pop_range = st.sidebar.slider(
    "Population range",
    min_value=pop_min,
    max_value=pop_max,
    value=(pop_min, pop_max),
    format="%d",
)

growth_min, growth_max = float(df["Annual Change"].min()), float(df["Annual Change"].max())
growth_range = st.sidebar.slider(
    "Annual growth rate range (%)",
    min_value=growth_min,
    max_value=growth_max,
    value=(growth_min, growth_max),
    step=0.1,
)

top_n = st.sidebar.slider("Top N cities to show in rankings", 5, 30, 10)

st.sidebar.markdown("---")
st.sidebar.caption("Built with 🌿 for Pakistan's city data")

# Apply filters
filtered_df = df[
    (df["City Category"].isin(selected_categories))
    & (df["2026 Population"].between(pop_range[0], pop_range[1]))
    & (df["Annual Change"].between(growth_range[0], growth_range[1]))
]
if selected_cities:
    filtered_df = filtered_df[filtered_df["City"].isin(selected_cities)]

if filtered_df.empty:
    st.warning("No cities match the current filters. Try widening your filter selection.")
    st.stop()

# ----------------------------------------------------------------------------
# KEY METRICS
# ----------------------------------------------------------------------------
total_population = int(filtered_df["2026 Population"].sum())
largest_city = filtered_df.loc[filtered_df["2026 Population"].idxmax()]
smallest_city = filtered_df.loc[filtered_df["2026 Population"].idxmin()]
fastest_city = filtered_df.loc[filtered_df["Annual Change"].idxmax()]
slowest_city = filtered_df.loc[filtered_df["Annual Change"].idxmin()]
avg_growth = filtered_df["Annual Change"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (c1, "Cities shown", f"{len(filtered_df):,}", "out of 127 total"),
    (c2, "Total population", f"{total_population:,}", "sum of selected cities"),
    (c3, "🏙️ Largest city", largest_city["City"], f"{largest_city['2026 Population']:,} people"),
    (c4, "📈 Fastest growing", fastest_city["City"], f"{fastest_city['Annual Change']:.2f}% / yr"),
    (c5, "Average growth", f"{avg_growth:.2f}%", "annual, selected cities"),
]
for col, label, value, sub in metrics:
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# ----------------------------------------------------------------------------
# TABS — one per analysis, following the notebook's sequence
# ----------------------------------------------------------------------------
tab_overview, tab_rankings, tab_distribution, tab_growth, tab_relationships, tab_data = st.tabs(
    [
        "📊 Overview",
        "🏆 Rankings",
        "📉 Distribution",
        "🚀 Growth",
        "🔗 Relationships",
        "🗂️ Data & Source",
    ]
)

# ---- Overview tab -----------------------------------------------------------
with tab_overview:
    left, right = st.columns([3, 2])

    with left:
        top_pop = filtered_df.nlargest(top_n, "2026 Population")
        fig = px.bar(
            top_pop.sort_values("2026 Population"),
            x="2026 Population",
            y="City",
            orientation="h",
            color="2026 Population",
            color_continuous_scale=GREEN_SEQUENTIAL,
            title=f"Top {top_n} Most Populated Cities",
            text="2026 Population",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Population", yaxis_title="")
        st.plotly_chart(style_fig(fig, 520), use_container_width=True)

    with right:
        cat_counts = filtered_df["City Category"].value_counts().reindex(categories).dropna()
        fig2 = px.pie(
            names=cat_counts.index,
            values=cat_counts.values,
            title="Cities by Population Category",
            color_discrete_sequence=GREEN_DISCRETE,
            hole=0.45,
        )
        fig2.update_traces(textinfo="label+percent")
        st.plotly_chart(style_fig(fig2, 520), use_container_width=True)

    st.markdown("#### Category counts")
    cat_counts_df = pd.DataFrame({"City Category": cat_counts.index, "Count": cat_counts.values})
    fig_cat = px.bar(
        cat_counts_df,
        x="City Category",
        y="Count",
        color="City Category",
        color_discrete_sequence=GREEN_DISCRETE,
        text="Count",
    )
    fig_cat.update_traces(textposition="outside")
    fig_cat.update_layout(showlegend=False, xaxis_title="Category", yaxis_title="Number of Cities")
    st.plotly_chart(style_fig(fig_cat, 380), use_container_width=True)

# ---- Rankings tab -----------------------------------------------------------
with tab_rankings:
    st.markdown("#### Population ranking table")
    st.dataframe(
        filtered_df.sort_values("2026 Population", ascending=False)
        [["Rank", "City", "2026 Population", "Annual Change", "Population Share (%)", "City Category"]]
        .style.format(
            {
                "2026 Population": "{:,}",
                "Annual Change": "{:.2f}%",
                "Population Share (%)": "{:.2f}%",
            }
        ),
        use_container_width=True,
        height=420,
    )

    st.markdown("#### Population share of top cities")
    top_share = filtered_df.nlargest(top_n, "2026 Population")
    fig3 = px.bar(
        top_share.sort_values("Population Share (%)"),
        x="Population Share (%)",
        y="City",
        orientation="h",
        color="Population Share (%)",
        color_continuous_scale=GREEN_SEQUENTIAL,
        title=f"Share of National Population — Top {top_n} Cities",
        text="Population Share (%)",
    )
    fig3.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig3.update_layout(coloraxis_showscale=False, yaxis_title="")
    st.plotly_chart(style_fig(fig3, 520), use_container_width=True)

# ---- Distribution tab --------------------------------------------------------
with tab_distribution:
    left, right = st.columns(2)
    with left:
        fig4 = px.histogram(
            filtered_df,
            x="2026 Population",
            nbins=20,
            title="Distribution of City Populations",
            color_discrete_sequence=[ACCENT_GREEN],
        )
        fig4.update_layout(xaxis_title="Population", yaxis_title="Number of Cities", bargap=0.05)
        st.plotly_chart(style_fig(fig4), use_container_width=True)

    with right:
        fig5 = px.box(
            filtered_df,
            x="2026 Population",
            title="Population Spread & Outliers",
            color_discrete_sequence=[PRIMARY_GREEN],
            points="outliers",
        )
        fig5.update_layout(xaxis_title="Population")
        st.plotly_chart(style_fig(fig5), use_container_width=True)

    st.info(
        f"📌 Population is highly right-skewed: the median city has "
        f"{int(filtered_df['2026 Population'].median()):,} people, while the largest "
        f"({largest_city['City']}) has {largest_city['2026 Population']:,} — showing a small "
        f"number of very large metro areas alongside many smaller cities."
    )

# ---- Growth tab ---------------------------------------------------------------
with tab_growth:
    left, right = st.columns(2)
    with left:
        fastest = filtered_df.nlargest(top_n, "Annual Change").sort_values("Annual Change")
        fig6 = px.bar(
            fastest,
            x="Annual Change",
            y="City",
            orientation="h",
            title=f"Top {top_n} Fastest-Growing Cities",
            color="Annual Change",
            color_continuous_scale=GREEN_SEQUENTIAL,
            text="Annual Change",
        )
        fig6.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig6.update_layout(coloraxis_showscale=False, xaxis_title="Annual Change (%)", yaxis_title="")
        st.plotly_chart(style_fig(fig6, 480), use_container_width=True)

    with right:
        slowest = filtered_df.nsmallest(top_n, "Annual Change").sort_values("Annual Change", ascending=False)
        fig7 = px.bar(
            slowest,
            x="Annual Change",
            y="City",
            orientation="h",
            title=f"{top_n} Slowest-Growing Cities",
            color="Annual Change",
            color_continuous_scale=["#01411C", "#B7D8C0"],
            text="Annual Change",
        )
        fig7.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig7.update_layout(coloraxis_showscale=False, xaxis_title="Annual Change (%)", yaxis_title="")
        st.plotly_chart(style_fig(fig7, 480), use_container_width=True)

# ---- Relationships tab ---------------------------------------------------------
with tab_relationships:
    left, right = st.columns([3, 2])
    with left:
        fig8 = px.scatter(
            filtered_df,
            x="2026 Population",
            y="Annual Change",
            hover_name="City",
            size="2026 Population",
            color="City Category",
            color_discrete_sequence=GREEN_DISCRETE,
            title="Population vs. Annual Growth Rate",
        )
        fig8.update_layout(xaxis_title="2026 Population", yaxis_title="Annual Change (%)")
        st.plotly_chart(style_fig(fig8, 480), use_container_width=True)

    with right:
        corr = filtered_df[["Rank", "2026 Population", "Annual Change"]].corr()
        fig9 = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale=GREEN_SEQUENTIAL,
            title="Correlation Between Numerical Variables",
            aspect="auto",
        )
        st.plotly_chart(style_fig(fig9, 480), use_container_width=True)

    pearson_r = filtered_df["2026 Population"].corr(filtered_df["Annual Change"])
    st.info(
        f"📌 Correlation between population size and annual growth rate: **{pearson_r:.3f}** "
        "— a value near 0 means city size alone doesn't strongly predict how fast a city is growing."
    )

# ---- Data & Source tab ---------------------------------------------------------
with tab_data:
    st.markdown("#### Filtered dataset")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True, height=420)

    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="pakistan_cities_population_filtered.csv",
        mime="text/csv",
    )

    st.markdown("#### 📚 Data source")
    st.markdown(
        f"""
        <div class="source-box">
        The dataset used in this project contains 2026 population estimates
        and annual population growth rates for cities in Pakistan.<br><br>
        <b>Source:</b> World Population Review (WPR)<br>
        <b>Dataset:</b> Pakistan Cities Population 2026<br>
        <b>URL:</b> <a href="https://worldpopulationreview.com/cities/pakistan" target="_blank">
        https://worldpopulationreview.com/cities/pakistan</a><br><br>
        The population figures are estimates/projections based on historical
        Pakistan census data and World Population Review projections.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div style="text-align:center; color:#6a6a6a; margin-top:30px; padding-top:14px;
                border-top:1px solid {LIGHT_GREEN};">
        🇵🇰 Pakistan Cities Population Dashboard · Data: World Population Review
    </div>
    """,
    unsafe_allow_html=True,
)
