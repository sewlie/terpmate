from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the CSV data and replace "ND" with 0
CSV_FILE = "terpene_data_summary.csv"
data = pd.read_csv(CSV_FILE).replace("ND", "0")

@app.route('/')
def index():
    """Homepage with filter options."""
    terpenes = list(data.columns[2:])  # Skip "Name" and "Total Terpenes (%)"
    return render_template('index.html', terpenes=terpenes)

@app.route('/filter', methods=['POST'])
def filter_products():
    """Filter products based on selected terpenes."""
    selected_terpenes = request.form.getlist('terpenes')
    min_concentration = float(request.form.get('min_concentration', 0.01))
    
    # Filter data
    filtered_data = data.copy()
    for terpene in selected_terpenes:
        if terpene in filtered_data.columns:  # Validate terpene exists in the data
            filtered_data = filtered_data[filtered_data[terpene].apply(
                lambda x: float(str(x).replace('%', '')) >= min_concentration
            )]
        else:
            print(f"Warning: Terpene '{terpene}' not found in data.")

    # Convert to HTML for display
    return render_template('results.html', tables=[filtered_data.to_html(classes='data', index=False)], titles=filtered_data.columns.values)

if __name__ == "__main__":
    app.run(debug=True)
