import os
import re
import csv
import PyPDF2
import pytesseract
import streamlit as st
import pdf2image
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found. Please check your .env file.")

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text + "\n"
    # If no text was extracted, use OCR as fallback
    if not text.strip():
        text = extract_text_with_ocr(pdf_file)
    return text.strip()

# Function to extract text using OCR
def extract_text_with_ocr(pdf_file):
    images = pdf2image.convert_from_bytes(pdf_file.read())
    ocr_text = ""
    for image in images:
        ocr_text += pytesseract.image_to_string(image) + "\n"
    return ocr_text.strip()

# Function to get response from Gemini model
def get_gemini_response(prompt_text):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt_text)
    return response.text.strip()

# Updated function to parse integer scores and explanation text with fallback
def parse_score_and_explanation(response_text):
    # Try to match the "Score:" pattern
    match = re.search(r"Score:\s*(\d{1,3})", response_text)
    # Fallback: if the pattern isn't found, try to find any number in the response
    if not match:
        match = re.search(r"(\d{1,3})", response_text)
    explanation_match = re.search(r"Explanation:\s*(.*)", response_text, re.DOTALL)
    
    score = int(match.group(1)) if match else None
    explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."
    
    return (min(100, max(0, score)) if score is not None else None), explanation

# Function to evaluate resume scores with explanations and weighted total
def evaluate_resume(job_description, resume_text):
    scores = {}
    explanations = {}

    prompts = {
        "Semantic Score": f"""
            You are an AI expert in evaluating resumes based on job descriptions.

            Job Description:
            "{job_description}"

            Candidate’s Resume:
            "{resume_text}"

            Task:
            1. Compare keywords, skills, and responsibilities in the resume versus the job description.
            2. Identify the overlap between job requirements and the resume.
            3. Assign a Semantic Score (0-100) based on how well the resume aligns with the job.
            4. If the score is low, explain which key skills or responsibilities are missing.

            Format (return output in this structure only):
            - **Score:** [numeric value]
            - **Matched Keywords:** [List of relevant skills and responsibilities found]
            - **Missing Keywords:** [List of important skills that were missing]
            - **Explanation:** [Why this score was assigned based on keyword overlap]
        """,
        "Education Score": f"""
            You are an AI expert in resume evaluation.

            Job Description:
            "{job_description}"

            Candidate’s Resume:
            "{resume_text}"

            Task:
            1. Identify the candidate's highest relevant degree by focusing on the degree type and field (e.g., PhD, Master, BS, BSc).
            2. Ignore additional adjectives such as "Honours", "with distinction", etc.
            3. Evaluate whether the degree meets or exceeds the job's educational requirements.
            4. Assign an Education Score (0-100) based solely on the degree type and field match.
            5. If multiple degrees are present, pick the most relevant one.

            Format (return output in this structure only):
            - **Score:** [numeric value]
            - **Matched Degree:** [Degree type and field found in the resume]
            - **Explanation:** [Brief reason based solely on the degree type and field matching the job requirements]
        """,
        "Experience Score": f"""
            You are an AI trained to assess resumes for job positions.

            Job Description:
            "{job_description}"

            Candidate’s Resume:
            "{resume_text}"

            Task:
            1. Identify the most relevant past job experience from the resume.
            2. Check how closely the responsibilities match the job description.
            3. Consider the total years of relevant experience (more years = better score).
            4. Assign an Experience Score (0-100).
            5. If experience is missing or not closely related, explain why the score is low.

            Format (return output in this structure only):
            - **Score:** [numeric value]
            - **Matched Experience:** [Relevant job title and years]
            - **Explanation:** [Why this score was assigned, considering job responsibilities and relevance]
        """,
        "Certification Score": f"""
            You are an AI expert in evaluating resumes with respect to certifications and specialized training.

            Job Description:
            "{job_description}"

            Candidate’s Resume:
            "{resume_text}"

            Task:
            1. Identify any certifications or specialized training mentioned in the resume that are relevant to the job.
            2. Evaluate how these certifications meet or exceed the job's requirements.
            3. Assign a Certification Score (0-100) based solely on the relevance and value of the certifications.
            
            Format (return output in this structure only):
            - **Score:** [numeric value]
            - **Matched Certifications:** [List of certifications found]
            - **Explanation:** [Brief reason why this score was assigned based on the certifications]
        """
    }

    # Fetch scores and explanations from Gemini model for each category
    for category, prompt in prompts.items():
        raw_response = get_gemini_response(prompt)
        score, explanation = parse_score_and_explanation(raw_response)
        scores[category] = score if score is not None else 0  # Use 0 if no score is returned
        explanations[category] = explanation

    # Compute weighted total score
    # Weights: Semantic = 40%, Experience = 30%, Education = 20%, Certification = 10%
    weighted_total = round(
        scores["Semantic Score"] * 0.4 +
        scores["Experience Score"] * 0.3 +
        scores["Education Score"] * 0.2 +
        scores["Certification Score"] * 0.1
    )
    scores["Total Score"] = weighted_total
    explanations["Total Score"] = "Overall weighted score based on Semantic (40%), Experience (30%), Education (20%), and Certification (10%)."

    return scores, explanations

# Streamlit app UI
st.title("Resume Ranker Tool")

job_description = st.text_area("Enter Job Description", "")
uploaded_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)

if st.button("Analyze Resumes"):
    if not job_description:
        st.error("Please enter a job description!")
    elif not uploaded_files:
        st.error("Please upload at least one resume!")
    else:
        results = []

        # Create a placeholder for processing status
        processing_status = st.empty()

        # Process resumes with a counter indicator
        for idx, uploaded_file in enumerate(uploaded_files, start=1):
            processing_status.text(f"Processing Resume: {idx}")
            resume_text = extract_text_from_pdf(uploaded_file)

            if not resume_text:
                st.warning(f"Could not extract text from {uploaded_file.name}. Skipping.")
                continue

            scores, explanations = evaluate_resume(job_description, resume_text)
            results.append([
                uploaded_file.name,  # Preserve actual file name
                scores["Semantic Score"],
                explanations["Semantic Score"],
                scores["Education Score"],
                explanations["Education Score"],
                scores["Experience Score"],
                explanations["Experience Score"],
                scores["Certification Score"],
                explanations["Certification Score"],
                scores["Total Score"]
            ])

        # Once done, update the processing status
        processing_status.text("Processing Complete ✅")

        # Create DataFrame for display with appropriate column names
        df = pd.DataFrame(results, columns=[
            "File Name", 
            "Semantic Score", "Semantic Explanation",
            "Education Score", "Education Explanation",
            "Experience Score", "Experience Explanation",
            "Certification Score", "Certification Explanation",
            "Total Score"
        ])
        
        # Rank resumes based on Total Score using DataFrame ranking
        df["Rank"] = df["Total Score"].rank(method="dense", ascending=False).astype(int)
        df = df.sort_values(by="Rank")  # Sort by Rank for display

        # Show table in Streamlit
        st.subheader("Resume Analysis Results")
        st.dataframe(df, height=400)

        # Save results to CSV
        output_file = "resume_analysis_results.csv"
        df.to_csv(output_file, index=False)

        st.success("Analysis completed! Download results below:")
        st.download_button("Download CSV", data=open(output_file, "rb"), file_name=output_file)
