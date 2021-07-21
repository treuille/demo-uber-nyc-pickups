# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
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
import numpy as np
import altair as alt
import pydeck as pdk

# Set the page config to widemoe.
st.set_page_config(layout="wide")

# The column which holds the datetime data
DATE_TIME = "Date/Time"


@st.cache(persist=True)
def load_data(nrows):
    data: pd.DataFrame = pd.read_csv(
        "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/"
        "uber-raw-data-sep14.csv.gz",
        nrows=nrows,
    )  # type: ignore
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])  # type: ignore
    return data


data = load_data(500000)


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


# # Show the Streamilt veresion
# st.info(f"Streamlit version `{st.__version__}`")

# LAYING OUT THE TOP SECTION OF THE APP
col1, col2 = st.beta_columns(2)
col1.write(__doc__)
col2.subheader("")
hour_selected = col2.slider("Select hour of pickup", 0, 23)
names = ["New York City"] + col2.multiselect("Location", list(maps)[1:])
st.write("---")

# Display the maps
data = data[data[DATE_TIME].dt.hour == hour_selected]
for name, col in zip(names, st.beta_columns(len(names))):
    lat, lon, zoom = maps[name]
    with col:
        st.write(f"**{name}**", map(data, lat, lon, zoom))
    # break
# st.write(name, lat, lon, zoom, type(col)


# raise RuntimeError("Nothing.")
# # LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
# # row2_1, row2_2, row2_3, row2_4 =

# # # SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
# # la_guardia = [40.7900, -73.8700]
# # jfk = [40.6650, -73.7821]
# # newark = [40.7090, -74.1805]
# # zoom_level = 12
# # midpoint = [40.7359, -73.9780]
# # midpoint = (np.average(data["lat"]), np.average(data["lon"]))
# # st.write("midpoint", midpoint)


# with row2_1:
#     st.write(
#         "**All New York City from %i:00 and %i:00**"
#         % (hour_selected, (hour_selected + 1) % 24)
#     )
#     map(data, midpoint[0], midpoint[1], 11)

# with row2_2:
#     st.write("**La Guardia Airport**")
#     map(data, la_guardia[0], la_guardia[1], zoom_level)

# with row2_3:
#     st.write("**JFK Airport**")
#     map(data, jfk[0], jfk[1], zoom_level)

# with row2_4:
#     st.write("**Newark Airport**")
#     map(data, newark[0], newark[1], zoom_level)

# # FILTERING DATA FOR THE HISTOGRAM
# filtered = data[
#     (data[DATE_TIME].dt.hour >= hour_selected)  # type: ignore
#     & (data[DATE_TIME].dt.hour < (hour_selected + 1))  # type: ignore
# ]

# hist = np.histogram(
#     filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60)  # type: ignore
# )[0]

# chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

# # LAYING OUT THE HISTOGRAM SECTION

# st.write("")

# st.write(
#     "**Breakdown of rides per minute between %i:00 and %i:00**"
#     % (hour_selected, (hour_selected + 1) % 24)
# )

# st.altair_chart(
#     alt.Chart(chart_data)
#     .mark_area(
#         interpolate="step-after",
#     )
#     .encode(
#         x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
#         y=alt.Y("pickups:Q"),
#         tooltip=["minute", "pickups"],
#     )
#     .configure_mark(opacity=0.5, color="red"),
#     use_container_width=True,
# )
