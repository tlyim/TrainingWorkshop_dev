# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.4.3",
#     "pandas>=3.0.1",
#     "pyreadr>=0.5.4",
#     "pyzmq>=27.1.0",
#     "stargazer>=0.0.7",
#     "statsmodels>=0.14.6",
# ]
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import pyreadr
    import statsmodels.formula.api as smf
    from stargazer.stargazer import Stargazer

    return Stargazer, mo, np, pd, pyreadr, smf


@app.cell
def _(pd, pyreadr):
    # Read from CSV; load RData
    esg_tq = pd.read_csv("public/ESGscore_TobinsQ.csv")
    esg_data = list(pyreadr.read_r("public/ESG_data.RData").values())[0]
    return esg_data, esg_tq


@app.cell
def _(esg_data, esg_tq, np):
    # Merge and engineer features
    df = (
        esg_data
        .assign(date=lambda x: x["date"].astype(str))
        .merge(esg_tq, left_on=["instrument", "date"], right_on=["tic", "datadate"], how="left")
        .assign(
            at_pos   = lambda x: x["at"].where(x["at"] > 0),
            ceq_pos  = lambda x: x["ceq"].where(x["ceq"] > 0),
            q        = lambda x: (x["prcc_f"] * x["csho"] + x["dltt"] + x["dlc"]) / x["at_pos"],
            ESGscore = lambda x: x["esg_metric"],
            Firm_Size= lambda x: np.log(x["at"]),
            Leverage = lambda x: (x["dltt"] + x["dlc"]) / x["ceq_pos"],
            Year     = lambda x: x["fyear"],
            Industry = lambda x: x["sich"],
        )
        [["source", "q", "ESGscore", "Firm_Size", "Leverage", "Year", "Industry"]]
        .dropna()
    )
    df_B = df[df["source"] == "Provider_B"].drop(columns="source").reset_index(drop=True)
    df_A = df[df["source"] == "Provider_A"].drop(columns="source").reset_index(drop=True)
    return df_A, df_B


@app.cell
def _(df_B):
    # Summary statistics
    df_B.describe()
    return


@app.cell
def _(df_B, mo):
    # Descriptive statistics table
    cols = ["q", "ESGscore", "Firm_Size", "Leverage"]
    desc = (
        df_B[cols]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .T.rename(columns={"count": "N", "mean": "Mean", "median": "Median",
                            "std": "SD", "min": "Min", "max": "Max"})
        .assign(N=lambda x: x["N"].astype(int))
        .round(3)
        .reset_index()
        .rename(columns={"index": "Variable"})
    )
    mo.ui.table(desc)
    return


@app.cell
def _(df_B, mo):
    # Correlation table
    corr = (
        df_B[["q", "ESGscore", "Firm_Size", "Leverage"]]
        .corr()
        .round(3)
        .reset_index()
        .rename(columns={"index": ""})
    )
    mo.ui.table(corr)
    return


@app.cell
def _(df_A, df_B, smf):
    # Fit all regression models
    m1     = smf.ols("q ~ ESGscore", data=df_B).fit()
    m2     = smf.ols("q ~ ESGscore + Firm_Size + Leverage", data=df_B).fit()
    m3     = smf.ols("q ~ ESGscore + Firm_Size + Leverage + C(Industry)", data=df_B).fit()
    m4     = smf.ols("q ~ ESGscore + Firm_Size + Leverage + C(Industry) + C(Year)", data=df_B).fit()
    m_alt  = smf.ols("q ~ ESGscore + Firm_Size + Leverage + C(Industry) + C(Year)", data=df_A).fit()
    m_large= smf.ols("q ~ ESGscore + Firm_Size + Leverage + C(Industry) + C(Year)",
                     data=df_B[df_B["Firm_Size"] > df_B["Firm_Size"].median()]).fit()
    m_1019 = smf.ols("q ~ ESGscore + Firm_Size + Leverage + C(Industry) + C(Year)",
                     data=df_B[df_B["Year"].between(2010, 2019)]).fit()
    return m1, m2, m3, m4, m_1019, m_alt, m_large


@app.cell
def _(Stargazer, m1, m2, m3, m4, mo):
    # Main results table
    sg = Stargazer([m1, m2, m3, m4])
    sg.title("MAIN RESULTS")
    sg.dependent_variable_name("q")
    sg.custom_columns(["Model 1", "Model 2", "Model 3", "Model 4"], [1, 1, 1, 1])
    sg.covariate_order(["ESGscore", "Firm_Size", "Leverage"])
    sg.rename_covariates({"Firm_Size": "Firm Size"})
    sg.add_line("Industry Indicators", ["No", "No", "Yes", "Yes"])
    sg.add_line("Year Indicators",     ["No", "No", "No",  "Yes"])
    sg.show_degrees_of_freedom(False)
    mo.Html(sg.render_html())
    return


@app.cell
def _(Stargazer, m4, m_1019, m_alt, m_large, mo):
    # Robustness analysis table
    sg2 = Stargazer([m4, m_alt, m_large, m_1019])
    sg2.title("ROBUSTNESS ANALYSIS")
    sg2.dependent_variable_name("q")
    sg2.custom_columns(["Main Results", "Alt. ESG Score", "Large Firms", "2010-2019"], [1, 1, 1, 1])
    sg2.covariate_order(["ESGscore"])
    sg2.add_line("Controls",             ["Yes", "Yes", "Yes", "Yes"])
    sg2.add_line("Industry Indicators",  ["Yes", "Yes", "Yes", "Yes"])
    sg2.add_line("Year Indicators",      ["Yes", "Yes", "Yes", "Yes"])
    sg2.show_degrees_of_freedom(False)
    mo.Html(sg2.render_html())
    return


if __name__ == "__main__":
    app.run()
