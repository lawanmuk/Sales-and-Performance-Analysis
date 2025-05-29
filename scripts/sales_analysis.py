import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

# Load data
df = pd.read_csv("../data/train.csv")

print(df.head())

# Check for missing values
print("\nMissing values:\n", df.isnull().sum())

# Convert 'Order Date' to datetime
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

# Extract year/month for analysis
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month_name()

# Group by category
sales_by_category = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)

# Plot
plt.figure(figsize=(10, 6))
sales_by_category.plot(kind='bar', color=['skyblue', 'orange', 'green'])
plt.title("Total Sales by Category")
plt.xlabel("Category")
plt.ylabel("Sales ($)")
plt.savefig("../visuals/sales_by_category.png")
plt.show()


# Group by month/year
monthly_sales = df.groupby(['Year', 'Month'])['Sales'].sum().reset_index()

# Plot
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_sales, x='Month', y='Sales', hue='Year', marker='o')
plt.title("Monthly Sales Trend")
plt.xticks(rotation=45)
plt.savefig("../visuals/monthly_sales.png")
plt.show()

top_products = df.groupby('Product Name')['Sales'].sum().nlargest(5)

plt.figure(figsize=(10, 6))
ax = top_products.plot(kind='barh', color='blue')
plt.title("Top 5 Profitable Products", pad=20)

# Customize labels and margins
ax.set_xlabel("Profit ($)", labelpad=10)
plt.subplots_adjust(left=0.3, bottom=0.1)

plt.savefig("../visuals/top_products.png", bbox_inches='tight', dpi=300)
plt.show()


fig = px.bar(top_products,
             x=top_products.values,
             y=top_products.index,
             title="Top 5 Profitable Products (Interactive)",
             labels={'x': 'Profit ($)', 'y': 'Product'},
             color_discrete_sequence=['purple'])
fig.write_html("../visuals/top_products_interactive.html")
fig.show()
