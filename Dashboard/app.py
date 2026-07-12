import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import plotly.express as px


# -----------------------------
# Load Data
# -----------------------------

data_path = Path("..") / "Output" / "escalation_predictions.xlsx"

df = pd.read_excel(data_path)
# Create Risk Level from Risk Score

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

app = dash.Dash(
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


# -----------------------------
# Charts
# -----------------------------

risk_chart = px.pie(
    df,
    names="RiskLevel",
    title="Defect Risk Distribution"
)


priority_chart = px.bar(
    df,
    x="Priority",
    title="Defects by Priority"
)


# -----------------------------
# Layout
# -----------------------------

app.layout = dbc.Container(
    [

        html.H1(
            "Intelligent Software Quality & Delivery Dashboard",
            className="text-center mt-4"
        ),


        dbc.Row(
            [

                dbc.Col(
                    dbc.Card(
                        [
                            html.H4("Total Defects"),
                            html.H2(total_defects)
                        ],
                        body=True
                    ),
                    width=4
                ),


                dbc.Col(
                    dbc.Card(
                        [
                            html.H4("Critical Risk"),
                            html.H2(critical_defects)
                        ],
                        body=True
                    ),
                    width=4
                ),


                dbc.Col(
                    dbc.Card(
                        [
                            html.H4("High Risk"),
                            html.H2(high_risk)
                        ],
                        body=True
                    ),
                    width=4
                ),

            ]
        ),


        html.Br(),


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
                ),

            ]
        )


    ],
    fluid=True
)



# -----------------------------
# Run App
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)