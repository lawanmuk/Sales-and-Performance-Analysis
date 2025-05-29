import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


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

top_products = df.groupby('Product Name')['Profit'].sum().nlargest(5)

# Plot
top_products.plot(kind='barh', color='purple')
plt.title("Top 5 Profitable Products")
plt.savefig("../visuals/top_products.png")
plt.show()