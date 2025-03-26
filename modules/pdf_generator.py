from fpdf import FPDF

def save_summary_as_pdf(summary_text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    pdf.set_font("Arial", size=12)

    for line in summary_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.output(output_path)