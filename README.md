
# 📄 Resume Ranker Tool

The **Resume Ranker Tool** is an AI-powered Streamlit application designed to **analyze, evaluate, and rank resumes** based on a given job description. It uses **Google Gemini AI** to assess each resume on four key criteria: **Semantic Match, Education, Experience, and Certifications**. The final output includes detailed explanations, scores, and a ranked list of candidates.

---

## 🚀 Features

- 🔍 **Semantic Analysis**: Evaluates how well a resume matches the job description using keyword and role alignment.
- 🎓 **Education Score**: Analyzes the degree type and field of study (e.g., PhD, Master, BS, BSc).
- 🏢 **Experience Score**: Checks relevant past roles, responsibilities, and years of experience.
- 📜 **Certification Score**: Evaluates industry-relevant certifications and training.
- 📊 **Total Score & Ranking**: Weighted scoring system and ranking based on total score.
- 📁 **Multiple Resume Upload**: Analyze a folder of PDFs at once.
- 📥 **Downloadable CSV Report**: Export analysis results.

---

## 🧠 Score Weightage

- **Semantic Score**: 40%
- **Experience Score**: 30%
- **Education Score**: 20%
- **Certification Score**: 10%

---

## 🛠 Installation

### Prerequisites

- **Python 3.7+**
- **pip** (Python package installer)
- **Tesseract OCR** installed and added to your system PATH  
  - [Tesseract OCR Installation Instructions](https://github.com/tesseract-ocr/tesseract)

1. **Clone the repository**  
```bash
git clone https://github.com/zazanali/resume-ranker-tool.git
cd resume-ranker-tool
```

2. **Create a virtual environment (recommended)**  
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**  
```bash
pip install -r requirements.txt
```

4. **Set up your API key**  
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## ✅ Usage

1. **Run the app**  
```bash
streamlit run streamlit_app.py
```

2. **Use the UI**:
   - Enter a **Job Description**
   - Upload one or more **PDF Resumes**
   - Click **Analyze Resumes**
   - View ranked results and **download the CSV report**

---

## 📂 Output Example

| File Name       | Total Score | Rank | Semantic Score | Education Score | Experience Score | Certification Score |
|----------------|-------------|------|----------------|------------------|------------------|----------------------|
| resume_john.pdf | 90          | 1    | 85             | 80               | 95               | 70                   |
| resume_jane.pdf | 75          | 2    | 70             | 65               | 80               | 60                   |

---

## 📎 Requirements

See [`requirements.txt`](./requirements.txt) for all dependencies. Key packages:

- `streamlit`
- `PyPDF2`
- `pdf2image`
- `pytesseract`
- `pandas`
- `google-generativeai`
- `python-dotenv`

Make sure [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) is installed and available in your system path.

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## 🙋‍♂️ Author

Developed by Zazan Ali – feel free to reach out for collaboration or questions!
