import numpy as np
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

from lumiere.frontend.config import LOGO_COLOR


def plot_effective_prior(
    effective_prior: list[float],
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]
            x=effective_prior,
            histnorm="probability density",
            nbinsx=100,
            opacity=0.75,
            marker_color=LOGO_COLOR,
            hovertemplate="Range: %{x}<br>Prior: %{y}<extra></extra>",
        )
    )

    if effective_prior:
        kde = gaussian_kde(effective_prior)
        x_kde = np.linspace(min(effective_prior), max(effective_prior), 100)
        y_kde = np.asarray(kde(x_kde), dtype=np.float64)
        fig.add_trace(
            go.Scatter(
                x=x_kde,
                y=y_kde,
                mode="lines",
                line=dict(width=4, color=LOGO_COLOR),
                hovertemplate="Value: %{x}<br>Prior: %{y}<extra></extra>",
            )
        )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0),
        title=dict(
            text="Effective prior",
            font=dict(size=32, color="black"),
        ),
        xaxis=dict(
            title=dict(
                text="MLP output",
                font=dict(size=18, color="black"),
            ),
            tickfont=dict(size=14, color="black"),
        ),
        yaxis=dict(
            title=dict(
                text="Prior",
                font=dict(size=18, color="black"),
            )
        ),
        plot_bgcolor="whitesmoke",
    )
    return fig
