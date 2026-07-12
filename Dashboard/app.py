import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import plotly.express as px


# -----------------------------
# Load Data
# -----------------------------

data_path = Path("..") / "Output" / "escalation_predictions.xlsx"

df = pd.read_excel(data_path)


# -----------------------------
# Risk Classification
# -----------------------------

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


# -----------------------------
# Create Dashboard
# -----------------------------

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP
    ]
)


# -----------------------------
# KPI Calculations
# -----------------------------

total_defects = len(df)

critical_defects = len(
    df[df["RiskLevel"] == "Critical"]
)

high_risk = len(
    df[df["RiskLevel"] == "High"]
)


# AI predicted escalations

if "Predicted" in df.columns:
    predicted_escalations = len(
        df[df["Predicted"] == "Yes"]
    )
else:
    predicted_escalations = 0



# -----------------------------
# Reusable KPI Card
# -----------------------------

def create_kpi_card(title, value):

    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(
                    title,
                    className="text-muted"
                ),

                html.H2(
                    value,
                    className="fw-bold"
                )
            ]
        ),
        className="shadow-sm text-center"
    )


# -----------------------------
# Charts
# -----------------------------

risk_chart = px.pie(
    df,
    names="RiskLevel",
    title="Defect Risk Distribution",
    hole=0.4
)


priority_chart = px.bar(
    df,
    x="Priority",
    title="Defects by Priority"
)



# -----------------------------
# Dashboard Layout
# -----------------------------

app.layout = dbc.Container(
    [

        # Header

        html.Div(
            [

                html.H1(
                    "AI Predictive Defect Management Command Center",
                    className="text-center mt-4 fw-bold"
                ),

                html.P(
                    "Machine Learning powered defect risk analysis and escalation prediction",
                    className="text-center text-muted"
                )

            ]
        ),


        html.Br(),



        # KPI Row

        dbc.Row(
            [

                dbc.Col(
                    create_kpi_card(
                        "Total Defects",
                        total_defects
                    ),
                    width=3
                ),


                dbc.Col(
                    create_kpi_card(
                        "Critical Risk",
                        critical_defects
                    ),
                    width=3
                ),


                dbc.Col(
                    create_kpi_card(
                        "High Risk",
                        high_risk
                    ),
                    width=3
                ),


                dbc.Col(
                    create_kpi_card(
                        "AI Predicted Escalations",
                        predicted_escalations
                    ),
                    width=3
                )

            ],

            className="mb-4"

        ),



        # Charts Row

        dbc.Row(
            [

                dbc.Col(
                    dcc.Graph(
                        figure=risk_chart
                    ),
                    width=6
                ),


                dbc.Col(
                    dcc.Graph(
                        figure=priority_chart
                    ),
                    width=6
                )

            ]

        )

    ],

    fluid=True
)



# -----------------------------
# Run Application
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)