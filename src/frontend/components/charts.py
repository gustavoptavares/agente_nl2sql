import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, Optional

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    return px.bar(df, x=x, y=y, title=title)

def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    return px.line(df, x=x, y=y, title=title)

def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str = "") -> go.Figure:
    return px.pie(df, names=names, values=values, title=title)

def create_scatter_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    return px.scatter(df, x=x, y=y, title=title)

def auto_chart(data: list, config: Dict[str, Any]) -> Optional[go.Figure]:
    if not data:
        return None
    
    df = pd.DataFrame(data)
    chart_type = config.get("chart_type", "bar")
    x_col = config.get("x_column", df.columns[0])
    y_col = config.get("y_column", df.columns[1] if len(df.columns) > 1 else df.columns[0])
    title = config.get("title", "")
    
    chart_functions = {
        "bar": create_bar_chart,
        "line": create_line_chart,
        "pie": lambda df, x, y, t: create_pie_chart(df, x, y, t),
        "scatter": create_scatter_chart
    }
    
    func = chart_functions.get(chart_type, create_bar_chart)
    return func(df, x_col, y_col, title)