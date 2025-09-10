# FAONet

**FAONet** is a Python package for building and analyzing **bipartite trade networks** using data from [FAOSTAT](https://www.fao.org/faostat/).  
It provides tools for:

- Importing and filtering trade data.
- Building weighted bipartite networks.
- Calculating structural metrics: degree, strength, clustering, betweenness.
- Visualizing trade matrices, degree distributions, and centrality.

---

## 📦 Installation

Clone the repository and install with `pip`:

```bash
git clone https://github.com/galeanojav/FAONet.git
cd FAONet
pip install .
```

---

## 🚀 Quick Start

```python
from faonet.io import load_file
from faonet.filtering import filter_top_percentile
from faonet.network import build_bipartite_network
from faonet.metrics import compute_degree_and_strength
from faonet.plots import plot_weight_matrix

# Load FAOSTAT CSVs
df = load_file("examples/Data/Green_Coffe_FAO_allyears.csv")

# Filter 90% of the market
df_filtered = filter_top_percentile(df, value_column="Value", percentile=0.9)

# Build a bipartite graph
G, reporters, partners = build_bipartite_network(df_filtered, "Reporter Countries", "Partner Countries", "Value")

# Compute degree and strength
df_exporters, df_importers = compute_degree_and_strength(G, reporters, partners)

# Visualize matrix
plot_weight_matrix(df_filtered)
```

---

## 📁 Example

A complete analysis notebook is available in:

📍 [`examples/FAONet_example.ipynb`](examples/FAONet_example.ipynb)

It includes:

- Data loading and filtering
- Network construction
- All main metrics (degree, strength, clustering, betweenness)
- Fitted models and visualizations

The example uses FAOSTAT coffee trade data (CSV files in `examples/Data/`).

---

## 🧪 Testing

Run the test suite with:

```bash
pytest tests/
```

---

## 📄 License

MIT License.
