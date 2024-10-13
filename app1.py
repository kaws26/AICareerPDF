import streamlit as st
from fpdf import FPDF
from huggingface_hub import InferenceClient



client = InferenceClient(
    "mistralai/Mistral-Nemo-Instruct-2407",
    token="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",
)

def sanitize_text(text):
    replacements = {
        '\u2013': '-',  # en-dash
        '\u2014': '-',  # em-dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201C': '"',  # left double quote
        '\u201D': '"',  # right double quote
        '\u2026': '...',  # ellipsis
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def get_career_recommendations(skills, stream, favourite_subject):
    messages=[]
    for message in client.chat_completion(
        messages=[{
            "role": "system", "content": "You are a helpful career guidance AI assistant for school children and remain focused on that domain.",
            "role": "user", "content": f"The student data is: skills: {skills}, stream: {stream}, favourite subject: {favourite_subject}. Based on this data, recommend 10 career options to the student."
        }],
        max_tokens=500,
        stream=True,
    ):
        messages.append(message.choices[0].delta.content)
    return sanitize_text(''.join(messages))


import re

def format_bold_text(pdf, text):
    """
    Detect and format bold text using ** for bold markers.
    """
    parts = re.split(r'(\*\*.*?\*\*)', text)  # Split by bold markers
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            # Bold text
            pdf.set_font('Helvetica', 'B', 12)  # Bold font
            pdf.multi_cell(0, 10, part[2:-2])  # Remove the ** markers
        else:
            # Regular text
            pdf.set_font('Helvetica', '', 12)  # Regular font
            pdf.multi_cell(0, 10, part)

class ModernPDF(FPDF):
    def header(self):
        # Add a header with a background color
        self.set_fill_color(0, 121, 255)  # Blue background
        self.rect(0, 0, 210, 20, 'F')  # Rectangle for header
        self.set_text_color(255, 255, 255)  # White text
        self.set_font('Helvetica', 'B', 18)
        self.cell(0, 10, 'Career Guidance Report', ln=True, align='C')
        self.ln(10)

    def footer(self):
        # Add a footer with page number
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')

    def add_section_title(self, title):
        # Add section title with a background color
        self.set_fill_color(255, 217, 102)  # Light yellow background
        self.set_text_color(0, 0, 0)  # Black text
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(5)

    def add_text(self, text):
        # Add regular text
        self.set_font('Helvetica', '', 12)
        self.set_text_color(0, 0, 0)  # Black text
        self.multi_cell(0, 10, text)
        self.ln(2)

def generate_pdf_report(name, personal_details, skills, stream, favourite_subject, career_recommendations):
    pdf = ModernPDF()
    pdf.add_page()

    # Student Information Section
    pdf.add_section_title("Student Information")
    pdf.add_text(f"Name: {name}")
    pdf.add_text(f"Personal Details: {personal_details}")
    pdf.add_text(f"Skills: {skills}")
    pdf.add_text(f"Stream: {stream}")
    pdf.add_text(f"Favourite Subject: {favourite_subject}")

    # Career Recommendations Section
    pdf.add_section_title("Recommended Careers")

    # Parse and format career recommendations
    recommendations = career_recommendations.split("\n")
    for rec in recommendations:
        if rec.strip() and not rec.strip().isdigit():
            format_bold_text(pdf, sanitize_text(rec.strip()))

    # Conclusion text (optional)
    pdf.add_section_title("Conclusion")
    pdf.add_text("To excel in any of these careers, focus on gaining practical experience and keeping up with the latest trends.")

    # Save the PDF
    pdf_filename = f"{name}_career_guidance_report.pdf"
    pdf.output(pdf_filename)
    return pdf_filename



def main():
    st.title("Career Guidance Report Generator")
    
    # Collect student details
    name = st.text_input("Student Name")
    personal_details = st.text_area("Personal Details")
    skills = st.text_input("Skills (comma separated)", value="programming, public speaking, marketing, accounting")
    stream = st.selectbox("Stream", ["Science", "Commerce", "Arts"], index=1)
    favourite_subject = st.text_input("Favourite Subject", value="Information Technology")
    
    if st.button("Generate Report"):
        if name and personal_details:
            # Get career recommendations
            career_recommendations = get_career_recommendations(skills, stream, favourite_subject)
            
            # Generate PDF
            pdf_filename = generate_pdf_report(name, personal_details, skills, stream, favourite_subject, career_recommendations)
            
            # Provide download link
            with open(pdf_filename, "rb") as file:
                st.download_button(
                    label="Download PDF Report",
                    data=file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
        else:
            st.error("Please enter all required details.")
            
if __name__ == "__main__":
    main()
