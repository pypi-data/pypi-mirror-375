from attachments import attach, load, present


def test_excel_to_csv():
    """Ensure LibreOffice-based CSV extraction works and returns the expected rows."""
    xlsx = "src/attachments/data/test_workbook.xlsx"

    att = attach(f"{xlsx}[format:csv]") | load.excel_to_libreoffice | present.csv

    csv_text = str(att)

    # --- basic sanity checks -------------------------------------------------
    # Header row
    assert "Product,Sales,Region" in csv_text
    # Two known data rows
    assert "Widget A,1000,North" in csv_text
    assert "Widget B,1500,South" in csv_text
    # No LibreOffice conversion error
    assert att.metadata.get("libreoffice_error") is None
