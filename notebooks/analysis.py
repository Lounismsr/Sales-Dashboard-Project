"""
Analyse du dataset de ventes — reproduit et complète l'analyse faite dans Power BI.

Usage :
    python notebooks/analysis.py

Entrée  : ../data/raw/input_data.csv, ../data/raw/master_data.csv
Sortie  : ../data/sales_merged.csv + graphiques dans ../images/
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Chargement et jointure
# ---------------------------------------------------------------------------
transactions = pd.read_csv("../data/raw/input_data.csv", parse_dates=["DATE"])
products = pd.read_csv("../data/raw/master_data.csv")

data = transactions.merge(products, on="PRODUCT ID", how="left")

# ---------------------------------------------------------------------------
# 2. Calcul des indicateurs (équivalent des mesures DAX du dashboard Power BI)
# ---------------------------------------------------------------------------
data["NET_SALES"] = data["QUANTITY"] * data["SELLING PRICE"] * (1 - data["DISCOUNT %"] / 100)
data["COST"] = data["QUANTITY"] * data["BUYING PRIZE"]
data["PROFIT"] = data["NET_SALES"] - data["COST"]
data["YEAR"] = data["DATE"].dt.year
data["MONTH"] = data["DATE"].dt.month
data["PERIOD"] = data["DATE"].dt.to_period("M").astype(str)

data.to_csv("../data/sales_merged.csv", index=False)

total_sales = data["NET_SALES"].sum()
total_profit = data["PROFIT"].sum()
margin = total_profit / total_sales * 100

print(f"Chiffre d'affaires total : {total_sales:,.2f} €")
print(f"Profit total             : {total_profit:,.2f} €")
print(f"Marge globale            : {margin:.2f} %")

# ---------------------------------------------------------------------------
# 3. Analyses par axe (catégorie, type de vente, paiement, produit, temps)
# ---------------------------------------------------------------------------
by_category = (
    data.groupby("CATEGORY")
    .agg(sales=("NET_SALES", "sum"), profit=("PROFIT", "sum"))
    .assign(margin=lambda d: d.profit / d.sales * 100)
    .sort_values("sales", ascending=False)
)

by_sale_type = data.groupby("SALE TYPE").agg(sales=("NET_SALES", "sum"))
by_payment = data.groupby("PAYMENT MODE").agg(sales=("NET_SALES", "sum"))
by_month = data.groupby(["YEAR", "PERIOD"]).agg(sales=("NET_SALES", "sum")).reset_index()
top_products = (
    data.groupby("PRODUCT").agg(sales=("NET_SALES", "sum")).sort_values("sales", ascending=False).head(10)
)

print("\n--- Chiffre d'affaires et marge par catégorie ---")
print(by_category)

# ---------------------------------------------------------------------------
# 4. Graphiques
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})

fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.bar(by_category.index, by_category["sales"], color="#2E5266")
ax1.set_ylabel("Chiffre d'affaires (€)")
ax2 = ax1.twinx()
ax2.plot(by_category.index, by_category["margin"], color="#D9752E", marker="o", linewidth=2.5)
ax2.set_ylabel("Marge (%)")
ax1.set_title("Chiffre d'affaires et marge par catégorie")
fig.tight_layout()
fig.savefig("../images/category_margin.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 5))
ax.pie(by_sale_type["sales"], labels=by_sale_type.index, autopct="%1.0f%%", startangle=90)
ax.set_title("Répartition du CA par type de vente")
fig.tight_layout()
fig.savefig("../images/sales_by_type.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(by_month["PERIOD"], by_month["sales"], color="#2E5266", marker="o", linewidth=2)
ax.set_xticks(range(0, len(by_month), 2))
ax.set_xticklabels(by_month["PERIOD"][::2], rotation=45, ha="right")
ax.set_title("Évolution mensuelle du chiffre d'affaires")
fig.tight_layout()
fig.savefig("../images/monthly_trend.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(top_products.index[::-1], top_products["sales"][::-1], color="#2E5266")
ax.set_xlabel("Chiffre d'affaires (€)")
ax.set_title("Top 10 des produits par chiffre d'affaires")
fig.tight_layout()
fig.savefig("../images/top_products.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 5))
ax.pie(by_payment["sales"], labels=by_payment.index, autopct="%1.0f%%", startangle=90)
ax.set_title("Répartition du CA par mode de paiement")
fig.tight_layout()
fig.savefig("../images/payment_split.png", dpi=150)
plt.close(fig)

print("\nGraphiques générés dans ../images/")
