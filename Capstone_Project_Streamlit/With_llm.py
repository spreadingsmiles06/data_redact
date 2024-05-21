import os
from io import BytesIO
from pathlib import Path
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
# from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from pdfminer.high_level import extract_text
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import streamlit as st
# genai.configure(api_key="AIzaSyDONU1LmKi9fVNEG9tsopZvRB0EcdKcfs8")

   # Get OpenAI API key from user
gemini_api_key = st.text_input("Enter your Gemini API key:", type="password")
if gemini_api_key:
# Set the OpenAI API key
    import os
    os.environ["GEMINI_API_KEY"] = gemini_api_key
#os.environ['GOOGLE_API_KEY'] = 'AIzaSyCNgcmnCCA81fPQWX_WL7Z786w-fOiankE'
else:
    st.warning("Please enter your Gemini API  tokey continue.")

try:
	llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
except:
	llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
# Initialize Presidio Analyzer and Anonymizer
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Provide your OpenAI API key
#openai_api_key = "sk-XXXXX"

# Initialize OpenAI language model
# llm = OpenAI(temperature=0.7, openai_api_key=openGPT_key)

# Define the prompt template
demo_template = 'In the following text, identify and REDACT (replace with [REDACTED]) any sensitive information such as names, addresses, phone numbers, email addresses, Social Security numbers, and credit card , gender , age numbers you find in the {text}.'

# Set up the prompt template
prompt = PromptTemplate(
    input_variables=['text'],
    template=demo_template
)

# Set up the LLM chain
chain1 = LLMChain(llm=llm, prompt=prompt)

# Function to redact PII from text
def redact_pii(text):
    analyzed_results = analyzer.analyze(text=text, language='en')
    redacted_text = anonymizer.anonymize(text=text, analyzer_results=analyzed_results)
    return redacted_text.text

# Function to process text with OpenAI and redact PII
def process_and_redact_text(text):
    processed_text = chain1.run(text)
    redacted_text = redact_pii(processed_text)
    return redacted_text

# Function to redact PII from PDF files
def redact_pdf(input_pdf_path, output_pdf_path):
    try:
        # Extract text from PDF
        input_text = extract_text(input_pdf_path)

        # Redact PII
        redacted_text = process_and_redact_text(input_text)

        # Write redacted text to a new file
        with open(output_pdf_path, 'w', encoding='utf-8') as output_file:
            output_file.write(redacted_text)
        
        print(f"Redacted file saved as: {output_pdf_path}")
    except Exception as e:
        print(f"Error processing {input_pdf_path}: {e}")

def download_file(file_path):
    with open(file_path, "rb") as f:
        contents = f.read()
    st.download_button(label="Download", data=contents, file_name=os.path.basename(file_path))

# Set the directory path for PDF files
directory_path = "/home/ubuntu/ISB_Project/pdf"

def save_uploaded_files(uploaded_files, directory_path):
    # for uploaded_file in uploaded_files:
    file_path = os.path.join(directory_path, uploaded_files.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_files.getbuffer())
    st.success(f"Saved file: {file_path}")

uploaded_files = st.file_uploader("Your PDF files", accept_multiple_files=False, type=['PDF', 'pdf'])
if uploaded_files is not None:
    filename = uploaded_files.name
# if uploaded_files:
if st.button("Submit"):
    save_uploaded_files(uploaded_files, directory_path)

    os.chdir(directory_path)

    # Process each PDF file in the directory
    # for filename in os.listdir(directory_path):
    if filename.endswith(".pdf") or filename.endswith(".PDF"):
        input_pdf_path = os.path.join(directory_path, filename)
        output_pdf_path = os.path.join(directory_path, "redacted_" + filename.replace('.PDF', '.txt').replace('.pdf', '.txt'))
        redact_pdf(input_pdf_path, output_pdf_path)
        st.success(f"Redacted file saved as: {output_pdf_path}")
        # st.download_button("Download Output file",output_pdf_path)
        download_file(output_pdf_path)
