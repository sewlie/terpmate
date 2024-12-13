import pdfplumber
import csv
import os
import re

# Path to the folder containing PDFs
PDF_FOLDER = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\TERPbot\terpmate\COAs"
# Path to the output CSV file
CSV_FILE = "terpene_data_summary.csv"

# Valid terpene names
VALID_TERPENES = {
    "3-Carene", "alpha-Bisabolol", "alpha-Humulene", "alpha-Phellandrene", "alpha-Pinene",
    "alpha-Terpinene", "alpha-Terpineol", "beta-Myrcene", "beta-Pinene", "Borneol",
    "Camphene", "Camphor", "Caryophyllene oxide", "Cedrene", "Cedrol",
    "cis-Nerolidol", "cis-Ocimene", "Eucalyptol", "Farnesene", "Fenchone",
    "gamma-Terpinene", "gamma-Terpineol", "Geraniol", "Geranyl acetate", "Guaiol",
    "Isoborneol", "Isopulegol", "Limonene", "Linalool", "Menthol",
    "Nerol", "Pulegone (+)", "Sabinene", "Sabinene Hydrate", "Terpinolene",
    "trans-b-Ocimene", "trans-Caryophyllene", "trans-Nerolidol", "Valencene"
}

def extract_terpenes_from_phytofarma(text):
    """
    Extract terpene information specific to the Phytofarma PDF format.
    Looks for terpene names, LOQ %, and Results %.
    """
    terpene_data = {}
    for line in text.split("\n"):
        # Adjusted regex to handle spaces, LOQ, and Results correctly
        match = re.match(r"([\w\-\+\(\)\s]+)\s+([\d\.eE\-]+)\s+([\d\.]+|<LOQ)", line)
        if match:
            terpene_name = match.group(1).strip()
            result_value = match.group(3).strip()

            if terpene_name in VALID_TERPENES:
                # Skip "<LOQ" and set result as 0
                terpene_data[terpene_name] = "0" if result_value == "<LOQ" else result_value
    return terpene_data

def extract_strain_name(text, pdf_file):
    """Extract strain name from the PDF text or fallback to file name."""
    # Default to PDF file name if no strain name is found
    return os.path.basename(pdf_file).replace(".pdf", "").strip()

def extract_terpenes_and_total(pdf_path):
    """Extract strain name, terpene concentrations, and total terpene percentage from the provided PDF."""
    strain_name = "Unknown"
    terpene_data = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Extract strain name from the text or fallback to file name
            if strain_name == "Unknown":
                strain_name = extract_strain_name(text, pdf_path)

            # Extract terpene data from the specific format
            terpene_data.update(extract_terpenes_from_phytofarma(text))

    # Filter only valid terpenes
    filtered_terpene_data = {k: v for k, v in terpene_data.items() if k in VALID_TERPENES}

    # Calculate total terpene percentage
    total_terpenes = sum(
        float(value) for value in filtered_terpene_data.values() if value.replace('.', '', 1).isdigit()
    )
    filtered_terpene_data["Total Terpenes (%)"] = f"{total_terpenes:.4f}"

    return strain_name, filtered_terpene_data

def save_to_csv(rows, all_terpenes, csv_file):
    """Save the extracted data to a CSV file."""
    sorted_terpenes = sorted(all_terpenes)

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the header
        header = ["Name", "Total Terpenes (%)"] + sorted_terpenes
        writer.writerow(header)

        # Write the rows
        for row in rows:
            aligned_row = [row["Name"], row.get("Total Terpenes (%)", "0")]
            for terpene in sorted_terpenes:
                value = row.get(terpene, "0")
                aligned_row.append(value)
            writer.writerow(aligned_row)

def process_all_pdfs(folder_path):
    """Process all PDFs in the specified folder and save to CSV."""
    pdf_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".pdf")]
    rows = []
    all_terpenes = set()

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")
        strain_name, terpene_data = extract_terpenes_and_total(pdf_file)

        all_terpenes.update(terpene_data.keys())

        row = {"Name": strain_name}
        row.update(terpene_data)
        rows.append(row)

    save_to_csv(rows, all_terpenes, CSV_FILE)
    print(f"Data saved to {CSV_FILE}")

if __name__ == "__main__":
    process_all_pdfs(PDF_FOLDER)
