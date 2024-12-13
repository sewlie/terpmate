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
    "Limonene", "Beta-myrcene", "Linalool", "Beta-caryophyllene", "Alpha-pinene",
    "Alpha-humulene", "Beta-pinene", "Terpinolene", "Ocimene", "Alpha-bisabolol",
    "Caryophyllene-oxide", "Geraniol", "Camphene", "Guaiol", "Alpha-terpinene",
    "Terpineol", "Fenchol", "Valencene", "Alpha-phellandrene", "Farnesene","3-Carene", "alpha-Bisabolol", "alpha-Humulene", "alpha-Phellandrene", "alpha-Pinene",
    "alpha-Terpinene", "alpha-Terpineol", "beta-Myrcene", "beta-Pinene", "Borneol",
    "Camphene", "Camphor", "Caryophyllene oxide", "Cedrene", "Cedrol",
    "cis-Nerolidol", "cis-Ocimene", "Eucalyptol", "Farnesene", "Fenchone",
    "gamma-Terpinene", "gamma-Terpineol", "Geraniol", "Geranyl acetate", "Guaiol",
    "Isoborneol", "Isopulegol", "Limonene", "Linalool", "Menthol",
    "Nerol", "Pulegone (+)", "Sabinene", "Sabinene Hydrate", "Terpinolene",
    "trans-b-Ocimene", "trans-Caryophyllene", "trans-Nerolidol", "Valencene"
}

def extract_strain_name(text, pdf_file):
    """Extract strain name from PDF text or fallback to file name."""
    # Extract strain name under "Report #"
    report_match = re.search(r"Report #\s+(.+)", text)
    if report_match:
        return report_match.group(1).strip()

    # Extract strain name to the right of "Sample #"
    sample_match = re.search(r"Sample #\s+.+\s+(.+)", text)
    if sample_match:
        return sample_match.group(1).strip()

    # Default to PDF file name if no strain name is found
    return os.path.basename(pdf_file).replace(".pdf", "").strip()

def extract_terpenes_and_total(pdf_path):
    """Extract strain name, terpene concentrations, and total terpene percentage from the provided PDF."""
    strain_name = "Unknown"
    terpene_data = {}
    total_terpenes = 0.0
    within_terpene_section = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Extract strain name from the text or fallback to file name
            if strain_name == "Unknown":
                strain_name = extract_strain_name(text, pdf_path)

            lines = text.split("\n")
            for line in lines:
                # Detect the start of the terpene section
                if "Terpenes by HS-GC-MS" in line:
                    within_terpene_section = True
                    continue

                # Process lines within the terpene section
                if within_terpene_section:
                    if line.strip() == "" or "Foreign Matter by Microscopy" in line:
                        within_terpene_section = False
                        break

                    # Preprocess the line to separate numbers from text
                    line = re.sub(r"(\d)([A-Za-z])", r"\1 \2", line)

                    # Parse terpene data
                    parts = line.split()
                    if len(parts) >= 5:  # Ensure sufficient data in the line
                        terpene_name = parts[1]
                        concentration = parts[4]  # Correct concentration column

                        # Validate terpene name and concentration value
                        if terpene_name in VALID_TERPENES:
                            if concentration.replace('.', '', 1).isdigit():
                                concentration = f"{float(concentration):.4f}%"
                                total_terpenes += float(parts[4])
                            else:
                                concentration = "0"
                            terpene_data[terpene_name] = concentration

    return strain_name, f"{total_terpenes:.4f}%", terpene_data

def save_to_csv(rows, all_terpenes, csv_file):
    """Save the extracted data to a CSV file."""
    existing_strains = set()
    if os.path.exists(csv_file):
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_strains.add(row["Name"])

    sorted_terpenes = sorted(all_terpenes)

    with open(csv_file, mode="w" if not existing_strains else "a", newline="") as file:
        writer = csv.writer(file)

        if not existing_strains:
            header = ["Name", "Total Terpenes (%)"] + sorted_terpenes
            writer.writerow(header)

        for row in rows:
            if row["Name"] not in existing_strains:
                aligned_row = [row["Name"], row["Total Terpenes (%)"]]
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
        strain_name, total_terpenes, terpene_data = extract_terpenes_and_total(pdf_file)

        all_terpenes.update(name for name in terpene_data.keys() if name in VALID_TERPENES)

        row = {"Name": strain_name, "Total Terpenes (%)": total_terpenes}
        row.update(terpene_data)
        rows.append(row)

    save_to_csv(rows, all_terpenes, CSV_FILE)
    print(f"Data saved to {CSV_FILE}")

if __name__ == "__main__":
    process_all_pdfs(PDF_FOLDER)