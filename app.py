from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the CSV data
CSV_FILE = "terpene_data_summary.csv"

try:
    data = pd.read_csv(CSV_FILE, on_bad_lines="skip", sep=",").replace("ND", "0") if CSV_FILE else pd.DataFrame()
except pd.errors.ParserError as e:
    print(f"Error loading CSV: {e}")
    data = pd.DataFrame()  # Fallback to empty DataFrame if CSV is malformed

# Group and Color Mapping
MOOD_GROUPS = {
    "Energizing": ["Limonene", "Alpha-pinene", "Beta-pinene", "Terpinolene", "Ocimene", "Sabinene", "Alpha-phellandrene", "Pulegone"],
    "Balancing": ["Beta-caryophyllene", "Alpha-humulene", "Caryophyllene-oxide", "Eucalyptol", "Camphene", "Geraniol", "Fenchol", "Terpineol", "Borneol"],
    "Relaxing": ["Linalool", "Beta-myrcene", "Alpha-bisabolol", "Farnesene", "Guaiol", "Isopulegol", "Menthol", "Cedrol", "Camphor", "Valencene"],
}

GROUP_COLORS = {
    "Energizing": "#097a91", 
    "Balancing": "#469272",  
    "Relaxing": "#9b85af",  
}

@app.route('/')
def index():
    """Homepage with grouped terpene options."""
    return render_template('index.html', mood_groups=MOOD_GROUPS, group_colors=GROUP_COLORS)

@app.route('/filter', methods=['POST'])
def filter_products():
    """Filter and sort products based on selected terpenes."""
    selected_terpenes = request.form.getlist('terpenes')
    min_concentration = float(request.form.get('min_concentration', 0.01))

    # Debug: Show selected terpenes and available columns
    print("Selected terpenes:", selected_terpenes)
    print("Available columns in the CSV:", data.columns.tolist())

    # Filter data based on selected terpenes and minimum concentration
    filtered_data = data.copy()
    for terpene in selected_terpenes:
        if terpene in filtered_data.columns:
            filtered_data = filtered_data[
                filtered_data[terpene].apply(lambda x: float(str(x).replace('%', '')) >= min_concentration)
            ]
        else:
            print(f"Warning: Selected terpene '{terpene}' not found in the dataset.")

    if not filtered_data.empty:
        # Reorder columns based on selection order
        available_selected = [terpene for terpene in selected_terpenes if terpene in filtered_data.columns]
        initial_columns = ["Name", "Total Terpenes (%)"] + available_selected
        remaining_columns = [col for col in filtered_data.columns if col not in initial_columns]

        # Filtered view shows only the selected terpenes in order
        filtered_data_initial = filtered_data[initial_columns]

        # Full view includes all remaining columns
        filtered_data_full = filtered_data[initial_columns + remaining_columns]

        # Sort by the first selected terpene
        primary_terpene = available_selected[0] if available_selected else None
        if primary_terpene:
            filtered_data_initial = filtered_data_initial.sort_values(
                by=primary_terpene, 
                key=lambda x: x.apply(lambda y: float(str(y).replace('%', ''))), 
                ascending=False
            )
    else:
        filtered_data_initial = pd.DataFrame()  # Empty DataFrame
        filtered_data_full = pd.DataFrame()

    # Add classes for styled table rendering
    initial_table_html = (
        filtered_data_initial.to_html(classes="data styled-table", index=False)
        if not filtered_data_initial.empty else ""
    )
    full_table_html = (
        filtered_data_full.to_html(classes="data styled-table", index=False)
        if not filtered_data_full.empty else ""
    )

    return render_template(
        'results.html',
        initial_table=initial_table_html,
        full_table=full_table_html,
        titles=filtered_data.columns.values,
    )

if __name__ == "__main__":
    app.run(debug=True)
