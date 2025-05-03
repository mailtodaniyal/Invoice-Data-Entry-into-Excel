import pdfplumber
import re
import pandas as pd
import os

def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def parse_data(text):
    data = {
        "Invoice Number": None,
        "Date": None,
        "Client Name": None,
        "Client Address": None,
        "Description": None,
        "Total Amount": None,
        "Notes": None
    }

    invoice_num = re.search(r"(Numéro de facture|Invoice No\.?|No\. de facture|Reçu #)\s*([A-Z0-9-]+)", text)
    if invoice_num:
        data["Invoice Number"] = invoice_num.group(2).strip()

    date = re.search(r"(Payé le|DATE|Date de facture|Invoice Date)\s*([\d\/\sàéû]+\d{4}|\d{2}\/\d{2}\/\d{2,4})", text)
    if date:
        data["Date"] = date.group(2).strip()

    client = re.search(r"(Facturer à|FACTURÉ À|Client|Nom|DESTINATAIRE)\s*([^\n]+)", text)
    if client:
        data["Client Name"] = client.group(2).strip()

    address = re.search(r"(Adresse|Address|FACTURÉ À[^\n]+\n([^\n]+))", text)
    if address:
        data["Client Address"] = address.group(2).strip()

    description = re.search(r"(Description|DESCRIPTION|Domaine|SERVICE DATE)\s*([^\n]+)", text)
    if description:
        data["Description"] = description.group(2).strip()

    total = re.search(r"(Total|Montant payé|TOTAL|Amount Due)\s*([\d\.,]+)\s*C?\$?", text)
    if total:
        data["Total Amount"] = float(total.group(2).replace(",", "."))

    for key, value in data.items():
        if not value and key != "Notes":
            data["Notes"] = f"Missing {key}"

    return data

def process_invoices(folder_path):
    results = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}. Please add your PDF invoices there and run again.")
        return pd.DataFrame()
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            try:
                text = extract_text(os.path.join(folder_path, filename))
                invoice_data = parse_data(text)
                invoice_data["Filename"] = filename
                results.append(invoice_data)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    return pd.DataFrame(results)

output_file = "extracted_invoice_data.xlsx"
folder_path = "sample_invoices"

df = process_invoices(folder_path)
if not df.empty:
    df.to_excel(output_file, index=False)
    print(f"Success! Processed {len(df)} invoices. Results saved to {output_file}")
else:
    print(f"No invoices processed. Please add PDF files to the '{folder_path}' folder and run again.")