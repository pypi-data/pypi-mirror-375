import base64
import io

import dash
import polars as pl


def upload_features_grid(contents: str | None, n_clicks_remove: int, filename: str):
    if n_clicks_remove or contents is None:
        return (
            None,  # features-grid-upload.contents
            None,  # features-grid-store.data
            {"display": "flex"},  # features-grid-upload-container.style
            {"display": "none"},  # features-grid-uploaded.style
            "",  # features-grid-filename.children
            0,  # features-grid-remove.n_clicks
        )

    _, content_string = contents.split(",")
    decoded = io.BytesIO(base64.b64decode(content_string))
    df = pl.read_csv(decoded)
    return (
        contents,  # features-grid-upload.contents
        df.to_numpy().tolist(),  # features-grid-store.data
        {"display": "none"},  # features-grid-upload-container.style
        {"display": "flex"},  # features-grid-uploaded.style
        filename,  # features-grid-filename.children
        dash.no_update,  # features-grid-remove.n_clicks
    )
