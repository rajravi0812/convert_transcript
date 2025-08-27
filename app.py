import re
import streamlit as st
from docx import Document
from docx.shared import RGBColor
from io import BytesIO

# -----------------------------
# Processing Functions
# -----------------------------
def clean_and_structure(raw_text: str):
    """Clean SRT text and classify into headings, subheadings, bullets, normal."""
    # Remove timestamps and indexes
    cleaned = re.sub(r"^\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}", "", raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r"^\d+\s*\n", "", cleaned, flags=re.MULTILINE)

    # Join all lines into a single line to remove breaks
    text = " ".join(line.strip() for line in cleaned.splitlines() if line.strip())

    # Split text into sentences by period (.) but keep things like "Input Text:" intact
    sentences = re.split(r"(?<=\.)\s+", text)
    structured = []

    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue

        # Split by bullet '•' if multiple bullets exist
        parts = re.split(r"•", s_clean)
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Heading: numbered headings OR Module <digit>:
            if re.match(r"^\d+(\.\d+)*\s", part) or re.search(r"Module\s\d+:", part, re.IGNORECASE):
                structured.append(("heading", part))

            # Subheading: ends with colon OR starts with Example / Case Study / Contents
            elif part.endswith(":") or re.match(r"(Example|Case Study|Contents)\s?\d*:", part, re.IGNORECASE):
                structured.append(("subheading", part))

            # Bullet: starts with bullet but NOT ending with colon
            elif part.startswith("·") or part.startswith("•"):
                structured.append(("bullet", part))

            # Normal text
            else:
                structured.append(("normal", part))

    return structured

def build_word_doc(structured):
    """Generate Word document with formatting."""
    doc = Document()

    for typ, text in structured:
        if typ == "heading":
            p = doc.add_paragraph()
            run = p.add_run(text)
            run.bold = True
            run.font.color.rgb = RGBColor(100, 149, 237)  # Soft blue

        elif typ == "subheading":
            p = doc.add_paragraph()
            run = p.add_run(text)
            run.bold = True
            # run.underline = True
            run.font.color.rgb = RGBColor(0, 0, 0)  # Black

        elif typ == "bullet":
            p = doc.add_paragraph()
            run = p.add_run(text)
            run.bold = True

        else:  # normal sentence
            p = doc.add_paragraph()
            run = p.add_run(text)
            run.font.color.rgb = RGBColor(0, 0, 0)

    # Save to BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------
# Streamlit App
# -----------------------------
st.title("📘 SRT Text Cleaner & Word Converter")

input_text = st.text_area("Paste your transcript text here:", height=400)

if st.button("Convert to Word"):
    if input_text.strip():
        structured = clean_and_structure(input_text)
        word_file = build_word_doc(structured)

        st.success("✅ Conversion complete!")
        st.download_button(
            label="📥 Download Word File",
            data=word_file,
            file_name="converted.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.error("⚠️ Please paste some text first!")
