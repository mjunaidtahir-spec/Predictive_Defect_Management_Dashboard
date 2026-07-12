import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

import pandas as pd
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go


# =====================================================
# AI DEFECT COMMAND CENTER
# Predictive Quality Intelligence Platform
# =====================================================


# =====================================================
# DATA LOADING
# =====================================================

data_path = (
    Path("..")
    / "Data"
    / "Defects Database Sample.xlsx"
)


df = pd.read_excel(data_path)
# Clean column names
df.columns = df.columns.str.strip()


# =====================================================
# DATA INTELLIGENCE ENGINE
# =====================================================


# Dynamic Risk Classification

def assign_risk(row):

    score = 0


    # Priority contribution

    if row["Priority"] == "Critical":
        score += 40

    elif row["Priority"] == "High":
        score += 30

    elif row["Priority"] == "Med":
        score += 20

    else:
        score += 10



    # Customer Impact

    if row["CustomerImpact"] == "Yes":
        score += 30



    # Aging

    if row["DefectAge"] >= 45:
        score += 20

    elif row["DefectAge"] >= 30:
        score += 10



    # Comments / discussion activity

    if row["CommentsCount"] >= 35:
        score += 10



    if score >= 75:
        return "Critical"

    elif score >= 55:
        return "High"

    elif score >= 35:
        return "Medium"

    else:
        return "Low"



df["RiskScore"] = df.apply(
    lambda x: assign_risk(x),
    axis=1
)



# =====================================================
# AI INSIGHT ENGINE
# =====================================================


def generate_ai_insights(data):


    total = len(data)


    critical = len(
        data[
            data["RiskScore"]=="Critical"
        ]
    )


    top_module = (
        data["ModuleName"]
        .value_counts()
        .idxmax()
    )


    top_vendor = (
        data["FixingVendor"]
        .value_counts()
        .idxmax()
    )


    impact_count = len(
        data[
            data["CustomerImpact"]=="Yes"
        ]
    )



    insights = [

        f"Analysis completed on {total} defects.",


        f"{critical} defects are classified as Critical risk.",


        f"{top_module} contains the highest defect concentration.",


        f"{top_vendor} has the highest defect ownership volume.",


        f"{impact_count} defects have customer impact exposure."

    ]


    return insights



# =====================================================
# VISUALIZATION FUNCTIONS
# =====================================================



# -------------------------------
# Risk Sunburst
# -------------------------------


def create_risk_sunburst(data):


    fig = px.sunburst(

        data,

        path=[

            "RiskScore",

            "ModuleName",

            "FixingVendor"

        ],

        title="Risk Concentration Intelligence"

    )


    return fig



# -------------------------------
# Defect Treemap
# -------------------------------


def create_treemap(data):


    fig = px.treemap(

        data,

        path=[

            "ModuleName",

            "DefectCategory"

        ],

        title="Defect Portfolio Landscape"

    )


    return fig



# -------------------------------
# Risk Heatmap
# -------------------------------


def create_heatmap(data):


    temp = (

        data

        .groupby(

            [

                "ModuleName",

                "Priority"

            ]

        )

        .size()

        .reset_index(

            name="Count"

        )

    )


    fig = px.density_heatmap(

        temp,

        x="Priority",

        y="ModuleName",

        z="Count",

        title="Module Risk Heatmap"

    )


    return fig



# -------------------------------
# Vendor Intelligence
# -------------------------------


def create_vendor_chart(data):


    vendor = (

        data

        .groupby("FixingVendor")

        .agg(

            Defects=("FixingVendor","count"),

            AvgAge=("DefectAge","mean")

        )

        .reset_index()

    )



    fig = px.scatter(

        vendor,

        x="AvgAge",

        y="Defects",

        size="Defects",

        hover_name="FixingVendor",

        title="Vendor Performance Intelligence"

    )


    return fig



# -------------------------------
# Root Cause Analysis
# -------------------------------


def create_rootcause_chart(data):


    rc = (

        data["RootCause"]

        .value_counts()

        .reset_index()

    )


    rc.columns=[

        "RootCause",

        "Count"

    ]



    fig = px.bar(

        rc,

        x="RootCause",

        y="Count",

        title="Root Cause Intelligence"

    )


    return fig



# -------------------------------
# Module Intelligence
# -------------------------------


def create_module_chart(data):


    modules=(

        data["ModuleName"]

        .value_counts()

        .reset_index()

    )


    modules.columns=[

        "Module",

        "Defects"

    ]


    fig=px.bar(

        modules,

        x="Module",

        y="Defects",

        title="Module Risk Exposure"

    )


    return fig


priority_score = {

    "Critical":100,
    "High":75,
    "Med":50,
    "Low":25

}


df["PriorityScore"] = (

    df["Priority"]
    .map(priority_score)
    .fillna(25)

)



customer_score = {

    "Yes":100,
    "No":0

}


df["CustomerImpactScore"] = (

    df["CustomerImpact"]
    .map(customer_score)
    .fillna(0)

)



df["AgeScore"] = (

    df["DefectAge"]
    .clip(upper=60)
    /
    60
    *
    100

)



escalation_score = {

    "Yes":100,
    "No":0

}


df["EscalationScore"] = (

    df["EscalationFlag (Yes/No)"]
    .map(escalation_score)
    .fillna(0)

)



df["NumericRiskScore"] = (

    df["PriorityScore"] * 0.35 +

    df["CustomerImpactScore"] * 0.30 +

    df["AgeScore"] * 0.20 +

    df["EscalationScore"] * 0.15

)



def risk_category(score):

    if score >= 80:
        return "Critical"

    elif score >=60:
        return "High"

    elif score >=40:
        return "Medium"

    else:
        return "Low"



df["RiskLevel"] = (

    df["NumericRiskScore"]
    .apply(risk_category)

)

# =====================================================
# APPLICATION INITIALIZATION
# =====================================================


app = Dash(

    __name__,

    external_stylesheets=[

        dbc.themes.DARKLY

    ]

)



app.title = (
    "AI Defect Command Center | "
    "Predictive Quality Intelligence Platform"
)



# =====================================================
# FILTER OPTIONS
# =====================================================


environment_options = [

    {
        "label": x,
        "value": x
    }

    for x in sorted(
        df["Environment"].dropna().unique()
    )

]


vendor_options = [

    {
        "label": x,
        "value": x
    }

    for x in sorted(
        df["FixingVendor"].dropna().unique()
    )

]


module_options = [

    {
        "label": x,
        "value": x
    }

    for x in sorted(
        df["ModuleName"].dropna().unique()
    )

]


risk_options = [

    {
        "label": x,
        "value": x
    }

    for x in [

        "Critical",
        "High",
        "Medium",
        "Low"

    ]

]



# =====================================================
# KPI CARD COMPONENT
# =====================================================


def create_kpi_card(
        title,
        value,
        description
):


    return dbc.Card(

        [

            html.H6(

                title,

                className="kpi-title"

            ),


            html.H2(

                value,

                className="kpi-value"

            ),


            html.P(

                description,

                className="kpi-description"

            )

        ],

        className="kpi-card"

    )



# =====================================================
# SIDEBAR
# =====================================================


sidebar = dbc.Col(

    [

        html.H4(

            "Dashboard Filters",

            className="sidebar-title"

        ),


        html.Hr(),



        html.Label(
            "Environment"
        ),


        dcc.Checklist(

            id="environment-filter",

            options=environment_options,

            value=[],

            className="filter-list"

        ),



        html.Br(),



        html.Label(
            "Vendor"
        ),


        dcc.Checklist(

            id="vendor-filter",

            options=vendor_options,

            value=[],

            className="filter-list"

        ),



        html.Br(),



        html.Label(
            "Module"
        ),


        dcc.Checklist(

            id="module-filter",

            options=module_options,

            value=[],

            className="filter-list"

        ),



        html.Br(),



        html.Label(
            "Risk Level"
        ),


        dcc.Checklist(

            id="risk-filter",

            options=risk_options,

            value=[],

            className="filter-list"

        )


    ],


    width=3,


    className="sidebar"

)



# =====================================================
# EXECUTIVE OVERVIEW TAB
# =====================================================


executive_tab = dbc.Container(

    [

        dbc.Row(

            [

                dbc.Col(
                    html.Div(id="total-kpi"),
                    width=3
                ),


                dbc.Col(
                    html.Div(id="critical-kpi"),
                    width=3
                ),


                dbc.Col(
                    html.Div(id="customer-kpi"),
                    width=3
                ),


                dbc.Col(
                    html.Div(id="ai-kpi"),
                    width=3
                )


            ],

            className="g-4"

        ),


        html.Br(),



        dbc.Row(

            [

                dbc.Col(

                    dcc.Graph(
                        id="sunburst-chart"
                    ),

                    width=6

                ),


                dbc.Col(

                    dcc.Graph(
                        id="treemap-chart"
                    ),

                    width=6

                )

            ]

        ),



        html.Br(),



        dbc.Row(

            [

                dbc.Col(

                    dcc.Graph(
                        id="status-chart"
                    ),

                    width=12

                )

            ]

        )


    ],

    fluid=True

)



# =====================================================
# RISK INTELLIGENCE TAB
# =====================================================


risk_tab = dbc.Container(

    [

        dbc.Row(

            [

                dbc.Col(

                    dcc.Graph(
                        id="heatmap-chart"
                    ),

                    width=6

                ),


                dbc.Col(

                    dcc.Graph(
                        id="module-chart"
                    ),

                    width=6

                )


            ]

        ),



        html.Br(),



        dbc.Row(

            [

                dbc.Col(

                    dcc.Graph(
                        id="rootcause-chart"
                    ),

                    width=12

                )

            ]

        )

    ],

    fluid=True

)



# =====================================================
# DELIVERY ANALYTICS TAB
# =====================================================


delivery_tab = dbc.Container(

    [

        dbc.Row(

            [

                dbc.Col(

                    dcc.Graph(
                        id="vendor-chart"
                    ),

                    width=6

                ),


                dbc.Col(

                    dcc.Graph(
                        id="environment-chart"
                    ),

                    width=6

                )


            ]

        )

    ],

    fluid=True

)



# =====================================================
# AI INSIGHTS TAB
# =====================================================


ai_tab = dbc.Container(

    [

        html.H3(

            "AI Generated Quality Intelligence"

        ),



        html.Div(

            id="ai-insight-panel",

            className="ai-panel"

        )


    ],

    fluid=True

)



# =====================================================
# MAIN APPLICATION LAYOUT
# =====================================================


app.layout = dbc.Container(

    [

        dbc.Row(

            [

                sidebar,


                dbc.Col(

                    [

                        html.H1(

                            "AI Defect Command Center",

                            className="main-title"

                        ),


                        html.H5(

                            "Predictive Quality Intelligence Platform",

                            className="subtitle"

                        ),


                        html.Hr(),



                        dcc.Tabs(

                            [

                                dcc.Tab(

                                    label="Executive Overview",

                                    children=executive_tab

                                ),



                                dcc.Tab(

                                    label="Risk Intelligence",

                                    children=risk_tab

                                ),



                                dcc.Tab(

                                    label="Delivery Analytics",

                                    children=delivery_tab

                                ),



                                dcc.Tab(

                                    label="AI Insights",

                                    children=ai_tab

                                )


                            ]

                        )


                    ],


                    width=9


                )

            ]

        )

    ],


    fluid=True,

    className="app-container"

)





# -------------------------------------------------
# Application
# -------------------------------------------------

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY
    ]
)


# -------------------------------------------------
# CheckList Options
# -------------------------------------------------

environment_options = [
    {"label": x, "value": x}
    for x in sorted(df["Environment"].unique())
]

vendor_options = [
    {"label": x, "value": x}
    for x in sorted(df["FixingVendor"].unique())
]

module_options = [
    {"label": x, "value": x}
    for x in sorted(df["ModuleName"].unique())
]

risk_options = [
    {"label": x, "value": x}
    for x in sorted(df["RiskLevel"].unique())
]


# -------------------------------------------------
# KPI Card
# -------------------------------------------------

def create_card(title, value, subtitle):

    return dbc.Card(

        [

            html.H6(
                title,
                className="text-uppercase"
            ),

            html.H2(
                value,
                className="mt-3"
            ),

            html.P(
                subtitle,
                className="text-muted"
            )

        ],

        style={
            "backgroundColor": "#1B263B",
            "borderRadius": "15px",
            "padding": "20px",
            "height": "150px"
        }

    )


# -------------------------------------------------
# Layout
# -------------------------------------------------

# -------------------------------------------------
# Layout
# -------------------------------------------------

app.layout = dbc.Container(

    [

        dbc.Row(

            [

                # -----------------------------
                # Sidebar
                # -----------------------------

                dbc.Col(

                    [

                        html.H4(
                            "Dashboard Filters",
                            className="mb-4"
                        ),


                        html.H6("Environment"),

                        dcc.Checklist(

                            id="environment-filter",

                            options=environment_options,

                            value=[],

                            className="mb-3"

                        ),


                        html.H6("Vendor"),

                        dcc.Checklist(

                            id="vendor-filter",

                            options=vendor_options,

                            value=[],

                            className="mb-3"

                        ),


                        html.H6("Module"),

                        dcc.Checklist(

                            id="module-filter",

                            options=module_options,

                            value=[],

                            className="mb-3"

                        ),


                        html.H6("Risk Level"),

                        dcc.Checklist(

                            id="risk-filter",

                            options=risk_options,

                            value=[],

                            className="mb-3"

                        )

                    ],


                    width=3,


                    style={

                        "backgroundColor": "#111827",

                        "padding": "25px",

                        "minHeight": "100vh"

                    }

                ),



                # -----------------------------
                # Main Area
                # -----------------------------

                dbc.Col(

                    [

                        html.H1(

                            "AI-Powered Predictive Defect Management Dashboard",

                            className="text-center"

                        ),


                        html.P(

                            "Machine Learning Driven Quality Risk Assessment & Delivery Intelligence",

                            className="text-center text-muted"

                        ),


                        html.Br(),



                        # Tabs

                        dcc.Tabs(

                            id="dashboard-tabs",

                            value="executive",

                            children=[


                                dcc.Tab(

                                    label="Executive Overview",

                                    value="executive"

                                ),


                                dcc.Tab(

                                    label="Risk Intelligence",

                                    value="risk"

                                ),


                                dcc.Tab(

                                    label="Delivery Analytics",

                                    value="delivery"

                                ),


                                dcc.Tab(

                                    label="AI Insights",

                                    value="ai"

                                )

                            ]

                        ),



                        html.Br(),



                        html.Div(

                            id="tab-content"

                        )

                    ],


                    width=9

                )

            ]

        )

    ],


    fluid=True,


    style={

        "backgroundColor": "#0F172A",

        "minHeight": "100vh"

    }

)

# -------------------------------------------------
# Tab Controller
# -------------------------------------------------

@app.callback(

    Output(
        "tab-content",
        "children"
    ),

    Input(
        "dashboard-tabs",
        "value"
    )

)


def render_tab(tab):


    if tab == "executive":

        return [

            html.H3(
                "Executive Overview"
            ),


            html.P(
                "Portfolio health overview of defect volume, risk exposure and delivery impact."
            ),


            dbc.Row(

                [

                    dbc.Col(
                        html.Div(id="total-card"),
                        width=3
                    ),


                    dbc.Col(
                        html.Div(id="critical-card"),
                        width=3
                    ),


                    dbc.Col(
                        html.Div(id="high-card"),
                        width=3
                    ),


                    dbc.Col(
                        html.Div(id="confidence-card"),
                        width=3
                    )

                ]

            ),


            html.Br(),


            dbc.Row(

                [

                    dbc.Col(

                        dcc.Graph(
                            id="risk-chart"
                        ),

                        width=6

                    ),


                    dbc.Col(

                        dcc.Graph(
                            id="priority-chart"
                        ),

                        width=6

                    )

                ]

            ),


            html.Br(),


            dcc.Graph(
                id="gauge-chart"
            )

        ]


    elif tab == "risk":

        return html.H3(
            "Risk Intelligence - Coming Next"
        )


    elif tab == "delivery":

        return html.H3(
            "Delivery Analytics - Coming Next"
        )


    else:

        return html.H3(
            "AI Insights - Coming Next"
        )

# -------------------------------------------------
# Callback - Dynamic Updates
# -------------------------------------------------

@app.callback(

    [

        Output("total-card","children"),

        Output("critical-card","children"),

        Output("high-card","children"),

        Output("confidence-card","children"),

        Output("risk-chart","figure"),

        Output("priority-chart","figure"),

        Output("gauge-chart","figure")

    ],


    [

        Input("environment-filter","value"),

        Input("vendor-filter","value"),

        Input("module-filter","value"),

        Input("risk-filter","value")

    ]

)


def update_dashboard(environment, vendor, module, risk):


    filtered_df = df.copy()



    if environment:
        filtered_df = filtered_df[
            filtered_df["Environment"].isin(environment)
        ]


    if vendor:
        filtered_df = filtered_df[
            filtered_df["FixingVendor"].isin(vendor)
        ]


    if module:
        filtered_df = filtered_df[
            filtered_df["ModuleName"].isin(module)
        ]


    if risk:
        filtered_df = filtered_df[
            filtered_df["RiskLevel"].isin(risk)
        ]



    total = len(filtered_df)


    critical = len(
        filtered_df[
            filtered_df["RiskLevel"]=="Critical"
        ]
    )


    high = len(
        filtered_df[
            filtered_df["RiskLevel"]=="High"
        ]
    )


    confidence = round(

        filtered_df[
            "EscalationProbability"
        ].mean(),

        1

    )



    # -----------------------------
    # Charts
    # -----------------------------


    risk_chart = px.pie(

        filtered_df,

        names="RiskLevel",

        hole=0.45,

        title="AI Risk Distribution"

    )


    risk_chart.update_layout(

        template="plotly_dark",

        paper_bgcolor="#1B263B"

    )



    priority_chart = px.bar(

        filtered_df,

        x="Priority",

        title="Defects by Priority",

        color="Priority"

    )


    priority_chart.update_layout(

        template="plotly_dark",

        paper_bgcolor="#1B263B"

    )



    gauge = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=confidence,

            title={
                "text":
                "AI Escalation Probability"
            },

            gauge={

                "axis":
                {
                    "range":[0,100]
                }

            }

        )

    )


    gauge.update_layout(

        template="plotly_dark",

        paper_bgcolor="#1B263B"

    )



    return (

        create_card(
            "Total Defects",
            total,
            "Filtered records"
        ),


        create_card(
            "Critical Risk",
            critical,
            "Immediate attention"
        ),


        create_card(
            "High Risk",
            high,
            "Review required"
        ),


        create_card(
            "AI Confidence",
            f"{confidence}%",
            "Prediction probability"
        ),


        risk_chart,

        priority_chart,

        gauge

    )



# -------------------------------------------------
# Run
# -------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)