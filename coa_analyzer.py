import pdfplumber
import csv
import os
import re

PDF_FOLDER = r"C:\Users\lilma\OneDrive\Documentos\NICO CODE\TERPbot\terpmate\COAs"
CSV_FILE = "terpene_data_summary.csv"

# Valid terpene names
VALID_TERPENES = {
    "Limonene", "Beta-myrcene", "Linalool", "Beta-caryophyllene", "Alpha-pinene",
    "Alpha-humulene", "Beta-pinene", "Terpinolene", "Ocimene", "Alpha-bisabolol",
    "Caryophyllene-oxide", "Geraniol", "Camphene", "Guaiol", "Alpha-terpinene",
    "Terpineol", "Fenchol", "Valencene", "Alpha-phellandrene", "Farnesene",
    "Eucalyptol", "Nerolidol", "Borneol", "Isopulegol", "Sabinene", "Delta-3-Carene",
    "Phellandrene", "Cedrene", "Isoborneol", "Menthol", "Citral", "Camphor", "Thymol",
    "Carvacrol", "Perillyl Alcohol", "Dihydroterpineol", "Elemene", "Pulegone",
    "Delta-2-Carene", "Geranyl Acetate", "Sabinene Hydrate", "Nonyl Aldehyde",
    "Decanal", "Hexyl Acetate", "Isobutyl Acetate", "Cedrol", "Methyl Salicylate",
    "Longifolene", "Bisabolene", "Ledene"
}

def extract_strain_name(text, pdf_file):
    """Extract strain name from PDF text."""
    match = re.search(r"Report #\s+(.+)", text) or re.search(r"Sample #\s+.+\s+(.+)", text)
    return match.group(1).strip() if match else os.path.basename(pdf_file).replace(".pdf", "").strip()

def extract_terpenes_and_total(pdf_path):
    """Extract strain name, terpene data, and total terpene percentage."""
    strain_name, terpene_data, total_terpenes = "Unknown", {}, 0.0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if strain_name == "Unknown":
                strain_name = extract_strain_name(text, pdf_path)

            if "Terpenes by HS-GC-MS" in text:
                lines = text.split("\n")
                for line in lines:
                    if "Foreign Matter by Microscopy" in line:
                        break
                    parts = re.split(r"\s+", re.sub(r"(\d)([A-Za-z])", r"\1 \2", line))
                    if len(parts) >= 5 and parts[1] in VALID_TERPENES:
                        value = parts[4]
                        terpene_data[parts[1]] = f"{float(value):.4f}%" if value.replace('.', '', 1).isdigit() else "0"
                        total_terpenes += float(value) if value.replace('.', '', 1).isdigit() else 0

    return strain_name, f"{total_terpenes:.4f}%", terpene_data

def save_to_csv(rows, all_terpenes, csv_file):
    """Save data to a CSV file."""
    existing_strains = set()
    if os.path.exists(csv_file):
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            existing_strains = {row["Name"] for row in reader}

    sorted_terpenes = sorted(all_terpenes)
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Total Terpenes (%)"] + sorted_terpenes)
        for row in rows:
            if row["Name"] not in existing_strains:
                writer.writerow([row["Name"], row["Total Terpenes (%)"]] + [row.get(t, "0") for t in sorted_terpenes])

def process_all_pdfs(folder_path):
    """Process all PDFs in the given folder."""
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]
    rows, all_terpenes = [], set()

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")
        strain_name, total_terpenes, terpene_data = extract_terpenes_and_total(pdf_file)
        all_terpenes.update(terpene_data.keys())
        rows.append({"Name": strain_name, "Total Terpenes (%)": total_terpenes, **terpene_data})

    save_to_csv(rows, all_terpenes, CSV_FILE)
    print(f"Data saved to {CSV_FILE}")

if __name__ == "__main__":
    process_all_pdfs(PDF_FOLDER)
