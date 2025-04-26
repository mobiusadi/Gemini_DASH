import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import pandas as pd

# Sample data (replace with your fire incident data)
data = pd.DataFrame({
    'id': [1, 2, 3],
    'latitude': [53.3498, 53.3478, 53.3518],
    'longitude': [-6.2603, -6.2583, -6.2623],
    'report': ['Incident A details...', 'Incident B details...', 'Incident C details...']
})

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create map markers
markers = [dl.Marker(position=[row['latitude'], row['longitude']], id=f"marker-{row['id']}")
           for index, row in data.iterrows()]

# Create incident cards
cards = [dbc.Card(dbc.CardBody([html.H5(f"Incident {row['id']}", className="card-title"),
                                html.P(row['report'], className="card-text")]),
                  id=f"card-{row['id']}",
                  style={'marginBottom': '10px'})
         for index, row in data.iterrows()]

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(dl.Map(children=[dl.TileLayer(), dl.LayerGroup(id="marker-group", children=markers)],
                       center=[53.3498, -6.2603], zoom=13, id="incident-map"), md=6),
        dbc.Col(html.Div(cards, id="card-container"), md=6),
    ])
])

@app.callback(
    [Output("marker-group", "children"),
     Output("card-container", "children")],
    [Input("incident-map", "click_feature"),
     # Assuming you have a way to trigger card selection (e.g., clicks on the card container)
     Input("card-container", "n_clicks")],
    [State("card-container", "children"),
     State("marker-group", "children"),
     State("incident-map", "click_feature")]
)
def update_highlights(map_click_feature, card_clicks, current_cards, current_markers, last_map_click):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    updated_cards = list(current_cards)  # Make a mutable copy
    updated_markers = list(current_markers) # Make a mutable copy
    highlighted_id = None

    if triggered_id == "incident-map" and map_click_feature:
        highlighted_id = map_click_feature['id'].split('-')[1]
    elif triggered_id == "card-container" and card_clicks is not None:
        # **Important:** You'll need a way to identify *which* card was clicked.
        # This example assumes the n_clicks of the container increments, but you need
        # to determine the specific card. You might need to add click handlers to individual cards.
        # For now, let's just assume the last card in the list should be highlighted.
        if current_cards:
            highlighted_id = current_cards[-1]['props']['id'].split('-')[1]

    if highlighted_id:
        updated_cards = []
        for card in current_cards:
            card_id = card['props']['id'].split('-')[1]
            new_style = card['props'].get('style', {})
            if card_id == highlighted_id:
                new_style['backgroundColor'] = 'red'
            else:
                new_style.pop('backgroundColor', None)
            updated_cards.append(dbc.Card(dbc.CardBody([html.H5(f"Incident {card_id}", className="card-title"),
                                                       html.P(data[data['id'] == int(card_id)]['report'].iloc[0], className="card-text")]),
                                         id=f"card-{card_id}",
                                         style=new_style))

        updated_markers = []
        for marker in current_markers:
            marker_id = marker['props']['id'].split('-')[1]
            new_icon = dl.Icon(iconUrl='blue_marker.png') # Default
            if marker_id == highlighted_id:
                new_icon = dl.Icon(iconUrl='red_marker.png')
            updated_markers.append(dl.Marker(position=marker['props']['position'], id=f"marker-{marker_id}", icon=new_icon))

    return updated_markers, updated_cards

if __name__ == '__main__':
    app.run(debug=True)