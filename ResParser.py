import streamlit as st
import pdfplumber
import docx
import re
import spacy
import fitz  # PyMuPDF
import dateparser

import nltk
nltk.download('punkt')  # Downloads missing NLTK tokenizer

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(file):
    """Extract text from a PDF file"""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file):
    """Extract text from a DOCX file"""
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text(file):
    """Extract text based on file type"""
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    return None


def extract_email(text):
    """Extract email from text"""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone_number(text):
    """Extract phone number from text"""
    match = re.search(r"\b(\+?\d{1,3}[-.\s]?)?(\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4})\b", text)
    return match.group(0) if match else None


# def extract_name(text):
#     """Extract name using spaCy's Named Entity Recognition (NER)"""
#     doc = nlp(text)
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             return ent.text
#     return None

def extract_name(text):
    """Improved Name Extraction from Resume"""
    # Extract first few lines
    lines = text.split("\n")[:5]

    # Use spaCy NER
    doc = nlp("\n".join(lines))
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    # Fallback: Extract capitalized words from the first lines
    for line in lines:
        words = line.split()
        if len(words) < 5:  # Assume name is short (not a full sentence)
            return " ".join(words).strip()

    return None


def extract_education(text):
    """Extract latest education using regex and keyword matching"""
    education_keywords = ["B.E", "B.Tech", "M.E", "M.Tech", "B.Sc", "M.Sc", "MBA", "BBA", "PhD", "Bachelor", "Master",
                          "Diploma"]
    lines = text.split("\n")
    for line in reversed(lines):
        if any(edu in line for edu in education_keywords):
            return line.strip()
    return None


# def extract_experience(text):
#     """Extract latest experience and total years of experience"""
#     experience_pattern = re.compile(r"(\b\d{1,2}\+?\s?(?:years?|yrs?)\b)", re.IGNORECASE)
#     matches = experience_pattern.findall(text)
#
#     latest_exp = matches[-1] if matches else None
#     total_exp = sum([int(re.search(r"\d+", exp).group()) for exp in matches]) if matches else 0
#     return latest_exp, total_exp


def extract_experience(text):
    """Extract latest company name and total years of experience"""

    # Experience pattern (captures years of experience)
    experience_pattern = re.compile(r"(\b\d{1,2}\+?\s?(?:years?|yrs?)\b)", re.IGNORECASE)
    exp_matches = experience_pattern.findall(text)

    total_exp = sum([int(re.search(r"\d+", exp).group()) for exp in exp_matches]) if exp_matches else 0

    # Work experience section patterns (extract latest company)
    company_pattern = re.compile(
        r"(?i)(?:at|in|with|for)\s+([A-Z][\w&.,\s-]+)\s*(?:\b(?:since|from|joined|–|to|until|present|current|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b)")
    company_matches = company_pattern.findall(text)

    latest_company = company_matches[-1].strip() if company_matches else None

    return latest_company, total_exp


def parse_resume(file):
    """Parse the resume and extract details"""
    text = extract_text(file)
    if not text:
        return None

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone_number(text)
    latest_education = extract_education(text)
    latest_experience, total_experience = extract_experience(text)

    return {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Latest Education": latest_education,
        "Latest Experience": latest_experience,
        "Total Experience (Years)": total_experience
    }


# Streamlit UI
st.title("📄 Resume Parser")
st.markdown("Upload a **PDF or DOCX** resume to extract key details.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file:
    with st.spinner("Parsing Resume..."):
        parsed_data = parse_resume(uploaded_file)

    if parsed_data:
        st.success("✅ Resume Parsed Successfully!")
        st.write("### Extracted Details:")
        for key, value in parsed_data.items():
            st.write(f"**{key}:** {value if value else 'Not Found'}")
    else:
        st.error("⚠️ Failed to extract details. Try a different file.")
