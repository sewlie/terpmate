from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

CSV_FILE = "terpene_data_summary.csv"
data = pd.read_csv(CSV_FILE).replace("ND", "0") if CSV_FILE else pd.DataFrame()

# Terpene color mapping
TERPENE_COLORS = {
    "Limonene": "#FFD700",  # Gold
    "Beta-myrcene": "#FF4500",  # OrangeRed
    "Linalool": "#9370DB",  # MediumPurple
    "Beta-caryophyllene": "#32CD32",  # LimeGreen
    "Alpha-pinene": "#228B22",  # ForestGreen
    "Alpha-humulene": "#A0522D",  # Sienna
    "Beta-pinene": "#2E8B57",  # SeaGreen
    "Terpinolene": "#00CED1",  # DarkTurquoise
    # Add more terpene colors as needed
}

def terpene_color(terpene):
    """Return the color associated with a terpene."""
    return TERPENE_COLORS.get(terpene, "#D3D3D3")  # Default to light gray

@app.route('/')
def index():
    terpenes = list(data.columns[2:])  # Skip "Name" and "Total Terpenes (%)"
    return render_template('index.html', terpenes=terpenes, terpene_color=terpene_color)

@app.route('/filter', methods=['POST'])
def filter_products():
    selected_terpenes = request.form.getlist('terpenes')
    min_concentration = float(request.form.get('min_concentration', 0.01))

    filtered_data = data.copy()
    for terpene in selected_terpenes:
        if terpene in filtered_data.columns:
            filtered_data = filtered_data[
                filtered_data[terpene].apply(lambda x: float(str(x).replace('%', '')) >= min_concentration)
            ]

    return render_template(
        'results.html',
        tables=[filtered_data.to_html(classes='data', index=False)],
        titles=filtered_data.columns.values,
    )

if __name__ == "__main__":
    app.run(debug=True)
