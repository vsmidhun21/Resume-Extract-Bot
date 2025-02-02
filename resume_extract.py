import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import re
import nltk
from datetime import datetime

# Ensure necessary NLTK packages are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('words')

from nltk.tokenize import sent_tokenize


# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text


# Function to extract email
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group() if match else "Not found"


# Function to extract mobile number
# def extract_mobile_number(text):
#     match = re.search(r'\b\d{10}\b', text)
#     return match.group() if match else "Not found"

def extract_mobile_number(text):
    match = re.search(r'(\+?\d{1,4}[-\s]?)?(\(?\d{1,4}\)?[-\s]?\d{7,10})', text)
    return match.group() if match else "Not found"


# Function to extract name (Assumes first line is the name)
def extract_name(text):
    lines = text.split("\n")
    return lines[0].strip() if lines else "Not found"


# Function to extract education details
def extract_education(text):
    sentences = sent_tokenize(text, language="english")
    education_keywords = ["B.E", "B.Tech", "M.E", "M.Tech", "Bachelor", "Master", "Degree", "Diploma"]
    return [sent for sent in sentences if any(keyword.lower() in sent.lower() for keyword in education_keywords)]


# Function to extract work experience
def extract_experience(text):
    experience_keywords = ["worked at", "experience in", "years at", "previously worked", "position at", "role at",
                           "employed at"]
    sentences = sent_tokenize(text)
    experience = [sent for sent in sentences if any(keyword in sent.lower() for keyword in experience_keywords)]
    return experience if experience else ["Not found"]


# Function to estimate total years of experience
def extract_years_of_experience(text):
    years = []
    # Match patterns like "2015-2020" or "2015 to 2020"
    date_matches = re.findall(r'(\d{4})\s*(?:-|to)\s*(\d{4})', text)
    for start, end in date_matches:
        if start.isdigit() and end.isdigit():
            years.append(int(end) - int(start))

    # Match patterns like "5 years", "3 yrs", "7 year"
    num_matches = re.findall(r'(\d+)\s*(?:years|yrs|year|yr)', text, re.IGNORECASE)
    years.extend(map(int, num_matches))

    return sum(years) if years else 0


# Streamlit UI
st.title("📄 Resume Information Extractor")
st.write("Upload a PDF resume to extract details like Name, Email, Mobile, Education, and Work Experience.")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)

    name = extract_name(extracted_text)
    email = extract_email(extracted_text)
    mobile = extract_mobile_number(extracted_text)
    education = extract_education(extracted_text)
    work_experience = extract_experience(extracted_text)
    total_experience = extract_years_of_experience(extracted_text)

    st.subheader("Extracted Information")
    st.write(f"**📛 Name:** {name}")
    st.write(f"**📧 Email:** {email}")
    st.write(f"**📱 Mobile:** {mobile}")
    st.write(f"**🎓 Education:** {', '.join(education)}")
    st.write(f"**💼 Work Experience:** {', '.join(work_experience)}")
    st.write(f"**📅 Total Experience:** {total_experience} years")
