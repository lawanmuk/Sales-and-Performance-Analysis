#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 29 08:54:07 2025

@author: lawanmuk
"""

import plotly.express as px

# Load data (if not already loaded)
import pandas as pd
df = pd.read_csv("../data/train.csv")

# Group data
top_products = df.groupby('Product Name')['Sales'].sum().nlargest(5).reset_index()

# Create interactive bar chart
fig = px.bar(top_products,
             x='Sales',
             y='Product Name',
             title='Top 5 Profitable Products (Interactive)',
             color='Sales',
             color_continuous_scale='reds')

# Customize layout
fig.update_layout(
    yaxis_title="Product",
    xaxis_title="Sales ($)",
    hovermode="y unified"
)

# Save the figure as an HTML file
fig.write_html("../visuals/refactor_top_products_interactive.html")


fig.show()
