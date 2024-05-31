import streamlit as st
import PyPDF2
import tabula
import pandas as pd
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import re
import pdfplumber
import base64

def extract_content(pdf_file):
    # Open the PDF file
    with pdfplumber.open(pdf_file) as pdf:
        # Extract the text from the PDF
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Split the text into lines
    lines = text.split('\n')

    # Initialize variables to store the table data
    table_data = []
    current_table = []

    # Iterate through the lines and extract the table data
    for line in lines:
        if line.strip() == "":
            # Append the current table to the table_data list and reset the current_table
            if current_table:
                table_data.append(current_table)
                current_table = []
        else:
            # Add the line to the current_table
            current_table.append(line)

    # Append the last table, if any
    if current_table:
        table_data.append(current_table)

    # Extract the content outside the tables
    non_table_content = [line for line in lines if line.strip() not in [table for table_row in table_data for table in table_row]]

    return non_table_content, table_data

def process_text_with_llm(text):
    # Split the text into chunks of 4097 tokens or less
    text_chunks = [text[i:i+4097] for i in range(0, len(text), 4097)]
    
    # Process each chunk and collect the results
    processed_chunks = []
    for chunk in text_chunks:
        result = chain.run(chunk)
        processed_chunks.append(result)
    
    # Combine the processed chunks back into a single string
    processed_text = ''.join(processed_chunks)
    return processed_text

def redact_content(extracted_content):
    # Define the prompt template
    demo_template = 'In the following text, identify and REDACT (replace with [REDACTED]) any sensitive information such as names, addresses, phone numbers, email addresses, Social Security numbers, hospital IDs, UHID number, gender, age numbers etc you find in the {text}.'

    # Set up the prompt template
    prompt = PromptTemplate(
        input_variables=['text'],
        template=demo_template
    )

    # Set up the language model (LLM)
    llm = OpenAI(temperature=0.7, max_tokens = -1)  # Remove the openai_api_key parameter

    # Set up the LLM chain
    global chain
    chain = LLMChain(llm=llm, prompt=prompt)

    # Process the extracted content
    processed_text = process_text_with_llm(extracted_content)

    return processed_text

def save_redacted_pdf(processed_text, pdf_file_path):
    doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph('Processed Content', styles['Heading1']))
    elements.append(Spacer(1, 12))

    for line in processed_text.split('\n'):
        elements.append(Paragraph(line, styles['BodyText']))
        elements.append(Spacer(1, 12))

    doc.build(elements)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">Download {file_label}</a>'
    return href

def main():
    st.title("PDF Content Extraction and Redaction")

    # Get OpenAI API key from user
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")

    if openai_api_key:
        # Set the OpenAI API key
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key

        # File uploader
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

        if uploaded_file is not None:
            # Extract text and tables from the PDF
            non_table_content, table_data = extract_content(uploaded_file)

            # Redact sensitive information
            extracted_content = "\n".join(non_table_content) + "\n\n" + "\n\n".join(["\n".join(table) for table in table_data])
            processed_text = redact_content(extracted_content)

            # Display redacted content
            st.header("Redacted Content")
            st.write(processed_text)

            # Save redacted content as PDF
            pdf_file_path = "redacted.pdf"
            save_redacted_pdf(processed_text, pdf_file_path)

            # Display a downloadable link for the redacted PDF
            st.markdown(get_binary_file_downloader_html(pdf_file_path, 'Redacted PDF'), unsafe_allow_html=True)
    else:
        st.warning("Please enter your OpenAI API key to continue.")

if __name__ == "__main__":
    main()
