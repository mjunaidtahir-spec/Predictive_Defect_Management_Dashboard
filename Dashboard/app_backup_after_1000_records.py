import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go


# -------------------------------------------------
# Load Data
# -------------------------------------------------

data_path = Path("..") / "Data" / "Defects Database Sample.xlsx"

df = pd.read_excel(data_path)

# -------------------------------------------------
# Dashboard Risk Intelligence Layer
# -------------------------------------------------

# Priority scoring

priority_score = {
    "Critical": 100,
    "High": 75,
    "Med": 50,
    "Low": 25
}

df["PriorityScore"] = (
    df["Priority"]
    .map(priority_score)
    .fillna(25)
)


# Customer impact scoring

customer_score = {
    "Yes": 100,
    "No": 0
}

df["CustomerImpactScore"] = (
    df["CustomerImpact"]
    .map(customer_score)
    .fillna(0)
)


# Defect age contribution

df["AgeScore"] = (
    df["DefectAge"]
    .clip(upper=60)
    / 60
    * 100
)


# Escalation contribution

escalation_score = {
    "Yes": 100,
    "No": 0
}

df["EscalationScore"] = (
    df["EscalationFlag (Yes/No)"]
    .map(escalation_score)
    .fillna(0)
)


# Combined Risk Score

df["RiskScore"] = (

    df["PriorityScore"] * 0.35 +

    df["CustomerImpactScore"] * 0.30 +

    df["AgeScore"] * 0.20 +

    df["EscalationScore"] * 0.15

)


# Risk Classification

def assign_risk(score):

    if score >= 80:
        return "Critical"

    elif score >= 60:
        return "High"

    elif score >= 40:
        return "Medium"

    else:
        return "Low"


df["RiskLevel"] = df["RiskScore"].apply(assign_risk)


# Simulated AI escalation probability
# (for dashboard storytelling)

df["EscalationProbability"] = (
    df["RiskScore"]
    .clip(0,100)
)


# Create Risk Level from Risk Score


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
# Dropdown Options
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

app.layout = dbc.Container(

    [

        dbc.Row(

            [

                # -----------------------------
                # Sidebar Filters
                # -----------------------------

                dbc.Col(

                    [

                        html.H4(
                            "Dashboard Filters"
                        ),

                        html.Hr(),


                        html.Label(
                            "Environment"
                        ),

                        dcc.Dropdown(

                            id="environment-filter",

                            options=environment_options,

                            multi=True,

                            placeholder="Select Environment"

                        ),


                        html.Br(),


                        html.Label(
                            "Vendor"
                        ),

                        dcc.Dropdown(

                            id="vendor-filter",

                            options=vendor_options,

                            multi=True,

                            placeholder="Select Vendor"

                        ),


                        html.Br(),


                        html.Label(
                            "Module"
                        ),

                        dcc.Dropdown(

                            id="module-filter",

                            options=module_options,

                            multi=True,

                            placeholder="Select Module"

                        ),


                        html.Br(),


                        html.Label(
                            "Risk Level"
                        ),

                        dcc.Dropdown(

                            id="risk-filter",

                            options=risk_options,

                            multi=True,

                            placeholder="Select Risk"

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
                # Main Dashboard Area
                # -----------------------------

                dbc.Col(

                    [

                        html.H1(

                            "AI-Powered Predictive Defect Management Dashboard",

                            className="text-center"

                        ),


                        html.H5(

                            "Machine Learning Driven Quality Risk Assessment & Escalation Intelligence",

                            className="text-center text-muted"

                        ),


                        html.Br(),



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

                            ],

                            className="g-4"

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


                        dbc.Row(

                            [

                                dbc.Col(

                                    dcc.Graph(
                                        id="gauge-chart"
                                    ),

                                    width=12

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


    style={

        "backgroundColor": "#0F172A",

        "minHeight": "100vh"

    }

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