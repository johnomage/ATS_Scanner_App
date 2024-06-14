from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
import streamlit as st
import time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_genai_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel(model_name='gemini-pro')
    combined_input = f"{input_text}\n\n{pdf_content}\n\n{prompt}"
    response = model.generate_content(combined_input)
    return response.text

def get_pdf_content(file_path):
    reader = PdfReader(file_path)
    pdf_content = ""
    for _, page in enumerate(reader.pages):
        content = page.extract_text()
        if content:
            pdf_content += content
            return pdf_content
        else:
            raise FileNotFoundError('No PDF file uploaded. 😒')

# create prompts
tech_analysis_prompt = """
            You are an expert Technical Recruiter with expertise in the following areas:
            - Frontend, Backend, and FullStack development
            - Data Science and Machine Learning
            - Data and Big Data Engineering
            - DevOps
            - Data Analysis

            Task: Provide a fit analysis of the provided resume against the job description (JD). The fit analysis should include the following sections:
            1. Summary of the candidate's qualifications
            2. Matching skills and experience with the JD
            3. Areas where the candidate's profile lacks alignment with the JD

            Additionally, provide a SWOT summary for the candidate based on the fit analysis.
            """

hr_analysis_prompt = f"""
                **Your Role:** You are an HR Manager with expertise in team dynamics, collaboration, personal development, behavioral interviewing, and data analysis.
                **Task:** You are tasked with evaluating a candidate's suitability for the [Job Title] position based on their resume and the provided Job Description (JD). 

                    **Analysis Framework:**
                            1. **Candidate Qualifications:** Briefly summarize the candidate's relevant skills and experience as highlighted in their resume. 
                            2. **Strengths:** Identify the key areas where the candidate's qualifications directly align with the requirements and desired skills outlined in the JD. Provide specific examples from the resume to support your evaluation.
                            3. **Areas for Improvement:**  Identify any gaps or areas where the candidate's experience or skills might not fully meet the expectations set in the JD.  Are there specific technical skills, certifications, or areas of experience missing? 
                            4. **Overall Suitability:**  Based on your analysis, assess the candidate's overall fit for the [Job Title] role. Consider both their strengths and any identified areas for improvement. 
                            5. **Recommendation:**  Would you recommend this candidate for an interview? If so, why? If not, what additional information might be helpful to determine their suitability? 
                            6. **Candidate Development:**  If there are any areas for improvement, suggest potential resources or steps the candidate could take to strengthen their profile for this or similar roles.
                            7. **Percentaget Match:** Calculate the percentage match of the candidate.

                **Additional Information:**

                - You may be provided with additional information about the candidate, such as a cover letter or references, which you can consider in your analysis (if applicable).
                - Use your judgment and expertise to assess the candidate's potential and fit for the company culture.

                **Remember:** Your objective evaluation will be crucial in the hiring process. 

                **Good Luck!**
                """

general_prompt = """
            You are an ATS scanner with full functionality and tuned for software development and Data Science and Analytics.

            Task: Evaluate the resume against the JD. Also estimate the matching percentage.
            """

prompt_dict = {"Engineering Manager Analysis": tech_analysis_prompt,
               "HR Analysis": hr_analysis_prompt,
               "General Overview": general_prompt}

def run_analysis(prompt, pdf_upload, jd):
    pdf_content = get_pdf_content(pdf_upload)
    response = get_genai_response(jd, pdf_content, prompt_dict[prompt])
    st.write(f'Analysis\n{response}')


# Streamlit app
st.set_page_config(page_title='ATS Resume Xpat')
st.header('ATS for your resume')

global job_title
job_title = st.text_input("Enter Job Title")
job_description = st.text_area(label='Paste the Job Description here.', key='input', help='Paste JD here.')
pdf_upload = st.file_uploader(label='Upload your resume in pdf', type=['pdf'])

if pdf_upload is not None:
    file_name = str(pdf_upload.name).split('.')[0]
    success = st.success(f'{file_name} uploaded successfully', icon='✅')
    time.sleep(1)
    success.empty()

# create buttons
# query_col, submit_col = st.columns(2)
prompt_selector = st.selectbox(label='Choose Query', options=["",
                                                              'Engineering Manager Analysis'.strip(),
                                                              'HR Analysis'.strip(),
                                                              'General Overview'.strip()])

submitted = st.button('Analyse Resume')
if submitted:
    if len(job_title) < 2 or len(job_description) < 70:
        st.error("One of Job Title or Job Description (JD) or both missing!", icon='❌')
    elif prompt_selector not in prompt_dict:
        st.error(f"Select a valid query to analyse {file_name}'s resume", icon='❌')
    else:
        info = st.info(f"Executing {prompt_selector} of {file_name}'s resume for {job_title} role.", icon='ℹ️')
        run_analysis(prompt_selector, pdf_upload, job_description)
