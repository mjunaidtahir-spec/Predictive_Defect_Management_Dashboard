import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# DATA LOADING & PRE-PROCESSING
# =====================================================

data_path = Path("..") / "Data" / "Defects Database Sample.xlsx"

try:
    df = pd.read_excel(data_path)
    df.columns = df.columns.str.strip()
except Exception:
    # Graceful fallback if the file path is slightly different during local runs
    df = pd.DataFrame(columns=[
        "Priority", "CustomerImpact", "DefectAge", "CommentsCount", 
        "ModuleName", "FixingVendor", "DefectCategory", "Environment", 
        "EscalationFlag (Yes/No)", "DefectStatus", "RootCause"
    ])

# Feature Engineering
priority_score = {"Critical": 100, "High": 75, "Med": 50, "Low": 25}
df["PriorityScore"] = df["Priority"].map(priority_score).fillna(25)

customer_score = {"Yes": 100, "No": 0}
df["CustomerImpactScore"] = df["CustomerImpact"].map(customer_score).fillna(0)

df["AgeScore"] = df["DefectAge"].clip(upper=60) / 60 * 100

escalation_score = {"Yes": 100, "No": 0}
df["EscalationScore"] = df["EscalationFlag (Yes/No)"].map(escalation_score).fillna(0)

df["NumericRiskScore"] = (
    df["PriorityScore"] * 0.35 +
    df["CustomerImpactScore"] * 0.30 +
    df["AgeScore"] * 0.20 +
    df["EscalationScore"] * 0.15
)

def risk_category(score):
    if score >= 80: return "Critical"
    elif score >= 60: return "High"
    elif score >= 40: return "Medium"
    else: return "Low"

df["RiskLevel"] = df["NumericRiskScore"].apply(risk_category)

# =====================================================
# APPLICATION INITIALIZATION
# =====================================================

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True  # Required for dynamic tab layouts
)
app.title = "AI Defect Command Center"

# -------------------------------------------------
# UI Helpers
# -------------------------------------------------
def create_kpi_card(title, value, description):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-uppercase text-muted small"),
            html.H2(value, className="mt-2 font-weight-bold"),
            html.P(description, className="mb-0 text-info small")
        ]),
        style={"borderRadius": "10px", "margin": "5px 0"}
    )

def get_chart_template(theme_choice):
    """Swaps internal plot templates and makes backgrounds transparent for the glass theme."""
    template = "plotly_white" if theme_choice == "white" else "plotly_dark"
    layout_adjustments = {}
    if theme_choice == "glass":
        layout_adjustments = {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)"
        }
    return template, layout_adjustments

# =====================================================
# SIDEBAR FILTERS WITH THEME TOGGLE
# =====================================================

sidebar = dbc.Col(
    [
        html.H4("Dashboard Filters", className="mb-4"),
        html.Hr(style={"color": "inherit"}),
        
        # Theme Custom Selector
        html.H6("Dashboard Theme", className="text-muted small"),
        dcc.Dropdown(
            id="theme-selector",
            options=[
                {"label": "🌑 Dark Black", "value": "black"},
                {"label": "☀️ Clean White", "value": "white"},
                {"label": "🔮 Premium Glass", "value": "glass"}
            ],
            value="black",
            clearable=False,
            className="mb-4" # Removed text-dark so it styles itself smoothly
        ),
        
        html.Hr(style={"color": "inherit"}),
        
        html.H6("Environment", className="text-muted small"),
        dcc.Checklist(
            id="environment-filter", 
            options=[{"label": x, "value": x} for x in sorted(df["Environment"].dropna().unique())], 
            value=[], className="mb-3"
        ),
        
        html.H6("Vendor", className="text-muted small"),
        dcc.Checklist(
            id="vendor-filter", 
            options=[{"label": x, "value": x} for x in sorted(df["FixingVendor"].dropna().unique())], 
            value=[], className="mb-3"
        ),
        
        html.H6("Module", className="text-muted small"),
        dcc.Checklist(
            id="module-filter", 
            options=[{"label": x, "value": x} for x in sorted(df["ModuleName"].dropna().unique())], 
            value=[], className="mb-3"
        ),
        
        html.H6("Risk Level", className="text-muted small"),
        dcc.Checklist(
            id="risk-filter", 
            options=[{"label": x, "value": x} for x in ["Critical", "High", "Medium", "Low"]], 
            value=[], className="mb-3"
        )
    ],
    width=3,
    className="sidebar-class",
    style={"padding": "25px", "minHeight": "100vh"}
)

# =====================================================
# MAIN LAYOUT CONTAINER WITH MASTER WRAPPER
# =====================================================

app.layout = html.Div(
    id="theme-wrapper",
    **{"data-theme": "black"}, # Native initialization tag
    children=[
        dbc.Container(
            [
                dbc.Row([
                    sidebar,
                    dbc.Col(
                        [
                            html.H1("AI-Powered Predictive Defect Management Dashboard", className="mt-4 text-center"),
                            html.P("Machine Learning Driven Quality Risk Assessment & Delivery Intelligence", className="text-center text-muted"),
                            html.Hr(style={"color": "inherit"}),
                            
                            dcc.Tabs(id="dashboard-tabs", value="executive", children=[
                                dcc.Tab(label="Executive Overview", value="executive", className="tab", selected_className="tab--selected"),
                                dcc.Tab(label="Risk Intelligence", value="risk", className="tab", selected_className="tab--selected"),
                                dcc.Tab(label="Delivery Analytics", value="delivery", className="tab", selected_className="tab--selected"),
                                dcc.Tab(label="AI Insights", value="ai", className="tab", selected_className="tab--selected")
                            ]),
                            html.Br(),
                            html.Div(id="tab-content")
                        ],
                        width=9,
                        style={"padding": "25px"}
                    )
                ])
            ],
            fluid=True,
            className="app-container",
            style={"minHeight": "100vh"}
        )
    ]
)

# =====================================================
# CALLBACK 1: GLOBAL THEME SWITCHER
# =====================================================
@app.callback(
    Output("theme-wrapper", "data-theme"),
    Input("theme-selector", "value")
)
def change_dashboard_theme(theme_choice):
    return theme_choice

# =====================================================
# CALLBACK 2: TAB ROUTER
# =====================================================
@app.callback(
    Output("tab-content", "children"),
    Input("dashboard-tabs", "value")
)
def render_tab(tab):
    if tab == "executive":
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.Div(id="total-kpi"), width=3),
                dbc.Col(html.Div(id="critical-kpi"), width=3),
                dbc.Col(html.Div(id="customer-kpi"), width=3),
                dbc.Col(html.Div(id="ai-kpi"), width=3)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(id="sunburst-chart"), width=6),
                dbc.Col(dcc.Graph(id="treemap-chart"), width=6)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(id="status-chart"), width=12)
            ])
        ], fluid=True)
        
    elif tab == "risk":
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id="heatmap-chart"), width=6),
                dbc.Col(dcc.Graph(id="module-chart"), width=6)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(id="rootcause-chart"), width=12)
            ])
        ], fluid=True)
        
    elif tab == "delivery":
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id="vendor-chart"), width=12)
            ])
        ], fluid=True)
        
    elif tab == "ai":
        return dbc.Container([
            html.H3("AI Generated Quality Intelligence"),
            html.Hr(),
            html.Div(id="ai-insight-panel", style={"padding": "20px", "borderRadius": "10px"})
        ], fluid=True)

# =====================================================
# FILTER HELPERS SHAREDBY VISUALIZATIONS
# =====================================================
def get_filtered_data(environments, vendors, modules, risks):
    filtered = df.copy()
    if environments:
        filtered = filtered[filtered["Environment"].isin(environments)]
    if vendors:
        filtered = filtered[filtered["FixingVendor"].isin(vendors)]
    if modules:
        filtered = filtered[filtered["ModuleName"].isin(modules)]
    if risks:
        filtered = filtered[filtered["RiskLevel"].isin(risks)]
    return filtered

# =====================================================
# CALLBACK 3: EXECUTIVE TAB UPDATES
# =====================================================
@app.callback(
    [
        Output("total-kpi", "children"),
        Output("critical-kpi", "children"),
        Output("customer-kpi", "children"),
        Output("ai-kpi", "children"),
        Output("sunburst-chart", "figure"),
        Output("treemap-chart", "figure"),
        Output("status-chart", "figure")
    ],
    [
        Input("environment-filter", "value"),
        Input("vendor-filter", "value"),
        Input("module-filter", "value"),
        Input("risk-filter", "value"),
        Input("theme-selector", "value")
    ]
)
def update_executive_tab(environments, vendors, modules, risks, theme_choice):
    filtered = get_filtered_data(environments, vendors, modules, risks)
    template, layout_adjustments = get_chart_template(theme_choice)
    
    total = len(filtered)
    critical = len(filtered[filtered["RiskLevel"] == "Critical"])
    customer = len(filtered[filtered["CustomerImpact"] == "Yes"])
    ai_score = round(filtered["NumericRiskScore"].mean(), 1) if not filtered.empty else 0

    sunburst = px.sunburst(filtered, path=["RiskLevel", "ModuleName", "FixingVendor"], title="Risk Concentration Intelligence", template=template) if not filtered.empty else go.Figure()
    treemap = px.treemap(filtered, path=["ModuleName", "DefectCategory"], title="Defect Portfolio Landscape", template=template) if not filtered.empty else go.Figure()
    status_chart = px.bar(filtered, x="DefectStatus", title="Defect Status Distribution", template=template) if "DefectStatus" in filtered.columns and not filtered.empty else go.Figure()

    # Dynamic styling injection
    for fig in [sunburst, treemap, status_chart]:
        if not filtered.empty and layout_adjustments:
            fig.update_layout(**layout_adjustments)

    return (
        create_kpi_card("Total Defects", total, "Current portfolio size"),
        create_kpi_card("Critical Exposure", critical, "Immediate attention"),
        create_kpi_card("Customer Impact", customer, "Customer facing defects"),
        create_kpi_card("AI Risk Index", f"{ai_score}%", "Predictive risk score"),
        sunburst, treemap, status_chart
    )

# =====================================================
# CALLBACK 4: RISK TAB UPDATES
# =====================================================
@app.callback(
    [
        Output("heatmap-chart", "figure"),
        Output("module-chart", "figure"),
        Output("rootcause-chart", "figure")
    ],
    [
        Input("environment-filter", "value"),
        Input("vendor-filter", "value"),
        Input("module-filter", "value"),
        Input("risk-filter", "value"),
        Input("theme-selector", "value")
    ]
)
def update_risk_tab(environments, vendors, modules, risks, theme_choice):
    filtered = get_filtered_data(environments, vendors, modules, risks)
    template, layout_adjustments = get_chart_template(theme_choice)
    
    if filtered.empty:
        return go.Figure(), go.Figure(), go.Figure()

    temp = filtered.groupby(["ModuleName", "Priority"]).size().reset_index(name="Count")
    heatmap = px.density_heatmap(temp, x="Priority", y="ModuleName", z="Count", title="Module Risk Heatmap", template=template)
    
    modules_df = filtered["ModuleName"].value_counts().reset_index()
    modules_df.columns = ["Module", "Defects"]
    module_chart = px.bar(modules_df, x="Module", y="Defects", title="Module Risk Exposure", template=template)
    
    rc = filtered["RootCause"].value_counts().reset_index() if "RootCause" in filtered.columns else pd.DataFrame(columns=["index", "count"])
    rc.columns = ["RootCause", "Count"]
    rootcause = px.bar(rc, x="RootCause", y="Count", title="Root Cause Intelligence", template=template)

    for fig in [heatmap, module_chart, rootcause]:
        if layout_adjustments:
            fig.update_layout(**layout_adjustments)

    return heatmap, module_chart, rootcause

# =====================================================
# CALLBACK 5: DELIVERY TAB UPDATES
# =====================================================
@app.callback(
    Output("vendor-chart", "figure"),
    [
        Input("environment-filter", "value"),
        Input("vendor-filter", "value"),
        Input("module-filter", "value"),
        Input("risk-filter", "value"),
        Input("theme-selector", "value")
    ]
)
def update_delivery_tab(environments, vendors, modules, risks, theme_choice):
    filtered = get_filtered_data(environments, vendors, modules, risks)
    template, layout_adjustments = get_chart_template(theme_choice)
    
    if filtered.empty:
        return go.Figure()
        
    vendor_df = filtered.groupby("FixingVendor").agg(Defects=("FixingVendor", "count"), AvgAge=("DefectAge", "mean")).reset_index()
    vendor_chart = px.scatter(vendor_df, x="AvgAge", y="Defects", size="Defects", hover_name="FixingVendor", title="Vendor Performance Intelligence", template=template)
    
    if layout_adjustments:
        vendor_chart.update_layout(**layout_adjustments)
        
    return vendor_chart

# =====================================================
# CALLBACK 6: AI INSIGHTS TAB UPDATES
# =====================================================
@app.callback(
    Output("ai-insight-panel", "children"),
    [
        Input("environment-filter", "value"),
        Input("vendor-filter", "value"),
        Input("module-filter", "value"),
        Input("risk-filter", "value")
    ]
)
def update_ai_tab(environments, vendors, modules, risks):
    filtered = get_filtered_data(environments, vendors, modules, risks)
    
    if filtered.empty:
        return [html.P("No records available for selected filters.", className="text-muted")]
        
    total = len(filtered)
    critical = len(filtered[filtered["RiskLevel"] == "Critical"])
    customer_impact = len(filtered[filtered["CustomerImpact"] == "Yes"])
    top_module = filtered["ModuleName"].value_counts().idxmax() if not filtered["ModuleName"].empty else "N/A"
    top_vendor = filtered["FixingVendor"].value_counts().idxmax() if not filtered["FixingVendor"].empty else "N/A"
    aging = len(filtered[filtered["DefectAge"] > 45])

    insights = [
        f"Analysis covers {total} defects currently under review.",
        f"{critical} defects are classified as Critical risk requiring priority attention.",
        f"{top_module} has the highest defect concentration.",
        f"{top_vendor} owns the largest defect volume.",
        f"{customer_impact} defects have customer impact exposure.",
        f"{aging} defects are aging beyond 45 days and may require escalation."
    ]
    
    return [html.H5("AI Generated Recommendations", className="text-info mb-3")] + [html.P(f"• {item}") for item in insights]


if __name__ == "__main__":
    app.run(debug=True)