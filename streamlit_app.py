# -*- coding: utf-8 -*-
# Copyright 2018-2021 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
# NYC Uber Ridesharing Data

Examining how Uber pickups vary over time in New York City's and at its major regional
airports.  By sliding the slider on the left you can view different slices of time and
explore different transportation trends. 
"""

import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk

# Set the page config to widemoe.
st.set_page_config(layout="wide")
st.expander = st.beta_expander
URL = "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"


@st.cache(persist=True)
def load_data(nrows):
    """Load `nrows` rows of Uber ride pickup data."""
    data: pd.DataFrame = pd.read_csv(URL, nrows=nrows)  # type: ignore
    date_time = pd.to_datetime(data["Date/Time"])  # type: ignore
    data["hour"] = date_time.dt.hour
    data["minute"] = date_time.dt.minute
    return data


def map(data, lat, lon, zoom) -> pdk.Deck:
    """Returns a nice looking PyDeck map focused on one part of the data."""
    MAP_STYLE = "mapbox://styles/mapbox/light-v9"
    view_state = dict(latitude=lat, longitude=lon, zoom=zoom, pitch=40)
    data_config = dict(data=data, get_position=["Lon", "Lat"])
    hex_config = dict(radius=75, elevation_scale=5, elevation_range=[0, 1000])
    mouse_config = dict(pickable=False, extruded=True)
    layer = pdk.Layer("HexagonLayer", **data_config, **hex_config, **mouse_config)
    return pdk.Deck(map_style=MAP_STYLE, initial_view_state=view_state, layers=[layer])


maps = {
    "New York City": (40.7359, -73.9780, 12),
    "La Guardia Airport": (40.7900, -73.8700, 12),
    "JFK Airport": (40.6650, -73.7821, 12),
    "Newark Airport": (40.7090, -74.1805, 12),
}

# Layout the top section of the app
col1, col2 = st.beta_columns(2)
col1.write(__doc__)
col2.subheader("")
hour_selected = col2.slider("Select hour of pickup", 0, 23)
names = col2.multiselect("Location", list(maps), list(maps)[:-1])
st.write("---")

# Display the maps
data = load_data(50000)
data = data[data.hour == hour_selected]
for name, col in zip(names, st.beta_columns(len(names))):
    lat, lon, zoom = maps[name]
    with col:
        st.write(f"**{name}**", map(data, lat, lon, zoom))

# Display the histogram
st.altair_chart(
    alt.Chart(data)
    .mark_area(color="lightblue", interpolate="step-after", line=True)
    .encode(
        x=alt.X("minute:Q", title="Minute", scale=alt.Scale(nice=False)),
        y=alt.Y("count()", title="Rides"),
        tooltip=["minute", "count():Q"],
    ),
    use_container_width=True,
)
