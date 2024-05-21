import os
import pandas as pd
from dotenv import load_dotenv
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.chat_models import ChatOpenAI
#from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel
from langchain_experimental.tabular_synthetic_data.base import SyntheticDataGenerator
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator, OPENAI_TEMPLATE
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_SUFFIX, SYNTHETIC_FEW_SHOT_PREFIX
import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import streamlit as st
import zipfile
openGPT_key = r'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'
# openGPT_key = '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'
# paLM_key = APIKey['PaLMKey']

def setAPIKey(x):
  os.environ["OPENAI_API_KEY"] = x

setAPIKey(openGPT_key)
def generate_pdf_for_row(row_data, pdf_file):
    # Create PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    Story = []
    #logo = "python_logo.png"
    
    full_name = row_data.get('Patient_Name', '')  # Assign patient_name to full_name
    
    # Extract patient data from the row_data dictionary
    Patient_ID = row_data.get('Patient_ID','')
    Patient_Name = row_data.get('Patient_Name','')
    Patient_Address = row_data.get('Patient_Address','')
    Patient_DOB = row_data.get('Patient_DOB','')
    Admitting_Diagnosis = row_data.get('Admitting_Diagnosis','')
    Hospital_Course = row_data.get('Hospital_Course','')
    Discharge_Diagnosis = row_data.get('Discharge_Diagnosis','')
    Discharge_Instructions = row_data.get('Discharge_Instructions','')
    Discharge_Disposition = row_data.get('Discharge_Disposition','')
    Discharge_Condition = row_data.get('Discharge_Condition','')
    Attending_Physician = row_data.get('Attending_Physician','')
    Additional_Information = row_data.get('Additional_Information','')
    Procedure_Code = row_data.get('Procedure_Code','')
    Total_Charge = row_data.get('Total_Charge','')
    Insurance_Claim_Amount = row_data.get('Insurance_Claim_Amount','')
    
    #im = Image(logo, 1*inch, 1*inch)
    #Story.append(im)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    formatted_time = time.ctime()

    ptext = 'Date: %s' % formatted_time
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 12))

    Story.append(Spacer(1, 12))
    ptext = 'Dear %s:' % full_name.split()[0].strip()
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 12))
    

    # Patient details
    ptext = 'Patient Name: %s' % Patient_Name
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Patient ID: %s' % Patient_ID
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Patient DOB: %s' % Patient_DOB
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Patient Address: %s' % Patient_Address
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Admitting Diagnosis Code: %s' % Admitting_Diagnosis
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Procedure Code: %s' % Procedure_Code
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Attending Physician: %s' % Attending_Physician
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Hospital Course: %s' % Hospital_Course
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Discharge Diagnosis Code: %s' % Discharge_Diagnosis
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Discharge Instructions: %s' % Discharge_Instructions
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Discharge Disposition: %s' % Discharge_Disposition
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Discharge Condition: %s' % Discharge_Condition
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Additional Information: %s' % Additional_Information
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Total Charge: $%s' % Total_Charge
    Story.append(Paragraph(ptext, styles["Normal"]))

    ptext = 'Insurance Claim Amount: $%s' % Insurance_Claim_Amount
    Story.append(Paragraph(ptext, styles["Normal"]))

    Story.append(Spacer(1, 12))

    # Additional details
    #limitedDate = "03/05/2010"
    #freeGift = "tin foil hat"
    
    #ptext = 'Limited Date: %s' % limitedDate
    #Story.append(Paragraph(ptext, styles["Normal"]))
    
    #ptext = 'Free Gift: %s' % freeGift
    #Story.append(Paragraph(ptext, styles["Normal"]))

    #Story.append(Spacer(1, 12))

    # paragraph
    ptext = 'We would like to thank you %s for taking our service for %s treatment! \
                You will receive a billing details along with %s. The Total Charge of the treatement is %s. \
                Please respond by following up with %s.' % ( Patient_Name,
                                                            Admitting_Diagnosis, 
                                                            Discharge_Instructions,
                                                            Total_Charge,
                                                            Attending_Physician)
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))

    # Closing message
    ptext = 'Thank you very much and we look forward to serving you.'
    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Spacer(1, 12))
    ptext = 'Sincerely,'
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 48))
    ptext = 'Your Name Here'  # Replace with appropriate name
    Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 12))
    doc.build(Story)
examples2 = [
{"example": """Patient_ID: 123456, Patient_Name: Ram Singh, Patient_Address: D-403 Downtown Langston Pune-411014, 
	Patient_DOB: 01/05/1980, Admitting_Diagnosis: Acute bronchitis (J20.9), 
	Hospital_Course: The patient was admitted with symptoms of cough, fever, and shortness of breath. Chest X-ray showed mild infiltrates. Treatment with antibiotics, bronchodilators, and supportive care was initiated. The patient's condition improved gradually, and symptoms resolved by day 5, 
	Discharge_Diagnosis: Acute bronchitis, resolved (J20.9), 
	Discharge_Instructions: Continue oral antibiotics for 5 more days. Follow up with primary care physician in 1 week. Resume normal activities as tolerated. Seek medical attention if symptoms worsen or fever returns., 
	Discharge_Disposition: Discharged to home with home health services for medication management., 
	Discharge_Condition: The patient was afebrile, with improved respiratory status and ambulating independently., 
	Attending_Physician: Dr. Jane Doe, Pulmonologist, 
	Additional_Information: The patient has a history of chronic obstructive pulmonary disease (COPD) and is a former smoker., 
	Procedure_Code: 99203 (Initial hospital care, level 3), Total_Charge: INR 5000, Insurance_Claim_Amount: INR 3500"""},
{"example": """Patient_ID: 789012, Patient_Name: Amit Sharma, Patient_Address: B-201 Sunrise Apartments Mumbai-400066, 
	Patient_DOB: 15/11/1975, Admitting_Diagnosis: Type 2 diabetes mellitus with diabetic ketoacidosis (E11.1), 
	Hospital_Course: The patient presented with severe dehydration, hyperglycemia, and ketoacidosis. Intravenous fluids, insulin therapy, and electrolyte replacement were initiated. Blood glucose levels were gradually stabilized, and the patient's condition improved over 3 days., 
	Discharge_Diagnosis: Type 2 diabetes mellitus with diabetic ketoacidosis, resolved (E11.1), 
	Discharge_Instructions: Continue long-acting insulin and oral hypoglycemic medications as prescribed. Follow a diabetic diet and monitor blood glucose levels regularly. Follow up with endocrinologist in 2 weeks. Seek medical attention if symptoms of hyperglycemia or ketoacidosis recur., 
	Discharge_Disposition: Discharged to home with home health services for diabetes management., 
	Discharge_Condition: The patient was stable, with normal vital signs and improved mentation., 
	Attending_Physician: Dr. Robert Lee, Endocrinologist, 
	Additional_Information: The patient has a family history of diabetes and is overweight (BMI 29.5)., 
	Procedure_Code: 99223 (Initial hospital care, level 3), Total_Charge: INR 12000, Insurance_Claim_Amount: INR 9600"""},
{"example": """Patient_ID: 345678, Patient_Name: Sarita Kulkarni, Patient_Address: 17 Shivaji Nagar Pune-411005, 
	Patient_DOB: 28/03/1990, Admitting_Diagnosis: Community-acquired pneumonia (J15.9), 
	Hospital_Course: The patient presented with fever, productive cough, and shortness of breath. Chest X-ray confirmed the presence of a right lower lobe infiltrate. Treatment with intravenous antibiotics, bronchodilators, and supportive care was initiated. The patient's condition gradually improved over 5 days., 
	Discharge_Diagnosis: Community-acquired pneumonia, resolved (J15.9), 
	Discharge_Instructions: Complete the course of oral antibiotics. Use incentive spirometer for deep breathing exercises. Follow up with primary care physician in 1 week. Seek medical attention if symptoms worsen or fever returns., 
	Discharge_Disposition: Discharged to home., 
	Discharge_Condition: The patient was afebrile, with improved respiratory status and ambulating independently., 
	Attending_Physician: Dr. Sanjay Deshmukh, Pulmonologist, 
	Additional_Information: The patient is a non-smoker and has no significant past medical history., 
	Procedure_Code: 99222 (Initial hospital care, level 2), Total_Charge: INR 8000, Insurance_Claim_Amount: INR 6400"""},
{"example": """Patient_ID: 102938, Patient_Name: Anjali Reddy, Patient_Address: Flat 304, Sunshine Residency Hyderabad-500072, 
	Patient_DOB: 12/09/1965, Admitting_Diagnosis: Acute myocardial infarction (I21.9), 
	Hospital_Course: The patient presented with severe chest pain, shortness of breath, and diaphoresis. Electrocardiogram confirmed ST-elevation myocardial infarction. Emergent cardiac catheterization and percutaneous coronary intervention were performed. The patient remained stable and was monitored in the cardiac intensive care unit for 3 days., 
	Discharge_Diagnosis: Acute myocardial infarction, status post percutaneous coronary intervention (I21.9), 
	Discharge_Instructions: Strict adherence to cardiac medications, including antiplatelet therapy, beta-blockers, and statins. Enroll in cardiac rehabilitation program. Avoid strenuous activities for 4-6 weeks. Follow a low-fat, low-cholesterol diet. Follow up with cardiologist in 2 weeks., 
	Discharge_Disposition: Discharged to home with home health services for medication management and cardiac monitoring., 
	Discharge_Condition: The patient was hemodynamically stable, with improved cardiac function., 
	Attending_Physician: Dr. Rajesh Gupta, Cardiologist, 
	Additional_Information: The patient has a history of hypertension and hyperlipidemia., 
	Procedure_Code: 92928 (Percutaneous coronary intervention), Total_Charge: INR 250000, Insurance_Claim_Amount: INR 200000"""},
]
with st.expander("Example Inputs:"):
	st.write(examples2)

def main():
   # Get OpenAI API key from user
	openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")
	if openai_api_key:
        # Set the OpenAI API key
		import os
		os.environ["OPENAI_API_KEY"] = openai_api_key
		load_dotenv()

	
		class MedicalBilling(BaseModel):
			Patient_ID: int
			Patient_Name: str
			Patient_Address: str
			Patient_DOB: str
			Admitting_Diagnosis: str
			Hospital_Course: str
			Discharge_Diagnosis: str
			Discharge_Instructions: str
			Discharge_Disposition: str
			Discharge_Condition: str
			Attending_Physician: str
			Additional_Information: str
			Procedure_Code: str
			Total_Charge: float
			Insurance_Claim_Amount: float
		examples = []
		run = st.number_input("Run:", step=1, value=2)
		patient_id = st.number_input("Patient ID", step=1, value=0)
		patient_name = st.text_input("Patient Name")
		patient_address = st.text_area("Patient Address")
		patient_dob = st.text_input("Date of Birth")
		# patient_dob = str(patient_dob)
		admitting_diagnosis = st.text_input("Admitting Diagnosis")
		hospital_course = st.text_area("Hospital Course")
		discharge_diagnosis = st.text_input("Discharge Diagnosis")
		discharge_instructions = st.text_area("Discharge Instructions")
		discharge_disposition = st.text_input("Discharge Disposition")
		discharge_condition = st.text_input("Discharge Condition")
		attending_physician = st.text_input("Attending Physician")
		additional_information = st.text_area("Additional Information")
		procedure_code = st.text_input("Procedure Code")
		total_charge = st.number_input("Total Charge", value=0.0, format="%.2f")
		insurance_claim_amount = st.number_input("Insurance Claim Amount", value=0.0, format="%.2f")
		if st.button("Submit", use_container_width=True, type='primary'):
			# examples = [
			# 	{"example": """Patient_ID: 123456, Patient_Name: Ram Singh, Patient_Address: D-403 Downtown Langston Pune-411014, 
			# 		Patient_DOB: 01/05/1980, Admitting_Diagnosis: Acute bronchitis (J20.9), 
			# 		Hospital_Course: The patient was admitted with symptoms of cough, fever, and shortness of breath. Chest X-ray showed mild infiltrates. Treatment with antibiotics, bronchodilators, and supportive care was initiated. The patient's condition improved gradually, and symptoms resolved by day 5, 
			# 		Discharge_Diagnosis: Acute bronchitis, resolved (J20.9), 
			# 		Discharge_Instructions: Continue oral antibiotics for 5 more days. Follow up with primary care physician in 1 week. Resume normal activities as tolerated. Seek medical attention if symptoms worsen or fever returns., 
			# 		Discharge_Disposition: Discharged to home with home health services for medication management., 
			# 		Discharge_Condition: The patient was afebrile, with improved respiratory status and ambulating independently., 
			# 		Attending_Physician: Dr. Jane Doe, Pulmonologist, 
			# 		Additional_Information: The patient has a history of chronic obstructive pulmonary disease (COPD) and is a former smoker., 
			# 		Procedure_Code: 99203 (Initial hospital care, level 3), Total_Charge: INR 5000, Insurance_Claim_Amount: INR 3500"""},
			# 	{"example": """Patient_ID: 789012, Patient_Name: Amit Sharma, Patient_Address: B-201 Sunrise Apartments Mumbai-400066, 
			# 		Patient_DOB: 15/11/1975, Admitting_Diagnosis: Type 2 diabetes mellitus with diabetic ketoacidosis (E11.1), 
			# 		Hospital_Course: The patient presented with severe dehydration, hyperglycemia, and ketoacidosis. Intravenous fluids, insulin therapy, and electrolyte replacement were initiated. Blood glucose levels were gradually stabilized, and the patient's condition improved over 3 days., 
			# 		Discharge_Diagnosis: Type 2 diabetes mellitus with diabetic ketoacidosis, resolved (E11.1), 
			# 		Discharge_Instructions: Continue long-acting insulin and oral hypoglycemic medications as prescribed. Follow a diabetic diet and monitor blood glucose levels regularly. Follow up with endocrinologist in 2 weeks. Seek medical attention if symptoms of hyperglycemia or ketoacidosis recur., 
			# 		Discharge_Disposition: Discharged to home with home health services for diabetes management., 
			# 		Discharge_Condition: The patient was stable, with normal vital signs and improved mentation., 
			# 		Attending_Physician: Dr. Robert Lee, Endocrinologist, 
			# 		Additional_Information: The patient has a family history of diabetes and is overweight (BMI 29.5)., 
			# 		Procedure_Code: 99223 (Initial hospital care, level 3), Total_Charge: INR 12000, Insurance_Claim_Amount: INR 9600"""},
			# 	{"example": """Patient_ID: 345678, Patient_Name: Sarita Kulkarni, Patient_Address: 17 Shivaji Nagar Pune-411005, 
			# 		Patient_DOB: 28/03/1990, Admitting_Diagnosis: Community-acquired pneumonia (J15.9), 
			# 		Hospital_Course: The patient presented with fever, productive cough, and shortness of breath. Chest X-ray confirmed the presence of a right lower lobe infiltrate. Treatment with intravenous antibiotics, bronchodilators, and supportive care was initiated. The patient's condition gradually improved over 5 days., 
			# 		Discharge_Diagnosis: Community-acquired pneumonia, resolved (J15.9), 
			# 		Discharge_Instructions: Complete the course of oral antibiotics. Use incentive spirometer for deep breathing exercises. Follow up with primary care physician in 1 week. Seek medical attention if symptoms worsen or fever returns., 
			# 		Discharge_Disposition: Discharged to home., 
			# 		Discharge_Condition: The patient was afebrile, with improved respiratory status and ambulating independently., 
			# 		Attending_Physician: Dr. Sanjay Deshmukh, Pulmonologist, 
			# 		Additional_Information: The patient is a non-smoker and has no significant past medical history., 
			# 		Procedure_Code: 99222 (Initial hospital care, level 2), Total_Charge: INR 8000, Insurance_Claim_Amount: INR 6400"""},
			# 	{"example": """Patient_ID: 102938, Patient_Name: Anjali Reddy, Patient_Address: Flat 304, Sunshine Residency Hyderabad-500072, 
			# 		Patient_DOB: 12/09/1965, Admitting_Diagnosis: Acute myocardial infarction (I21.9), 
			# 		Hospital_Course: The patient presented with severe chest pain, shortness of breath, and diaphoresis. Electrocardiogram confirmed ST-elevation myocardial infarction. Emergent cardiac catheterization and percutaneous coronary intervention were performed. The patient remained stable and was monitored in the cardiac intensive care unit for 3 days., 
			# 		Discharge_Diagnosis: Acute myocardial infarction, status post percutaneous coronary intervention (I21.9), 
			# 		Discharge_Instructions: Strict adherence to cardiac medications, including antiplatelet therapy, beta-blockers, and statins. Enroll in cardiac rehabilitation program. Avoid strenuous activities for 4-6 weeks. Follow a low-fat, low-cholesterol diet. Follow up with cardiologist in 2 weeks., 
			# 		Discharge_Disposition: Discharged to home with home health services for medication management and cardiac monitoring., 
			# 		Discharge_Condition: The patient was hemodynamically stable, with improved cardiac function., 
			# 		Attending_Physician: Dr. Rajesh Gupta, Cardiologist, 
			# 		Additional_Information: The patient has a history of hypertension and hyperlipidemia., 
			# 		Procedure_Code: 92928 (Percutaneous coronary intervention), Total_Charge: INR 250000, Insurance_Claim_Amount: INR 200000"""},
			# 	]

			example = {
				"example": f"""Patient_ID: {patient_id}, Patient_Name: {patient_name}, Patient_Address: {patient_address},
				Patient_DOB: {patient_dob}, Admitting_Diagnosis: {admitting_diagnosis}, Hospital_Course: {hospital_course},
				Discharge_Diagnosis: {discharge_diagnosis}, Discharge_Instructions: {discharge_instructions},
				Discharge_Disposition: {discharge_disposition}, Discharge_Condition: {discharge_condition},
				Attending_Physician: {attending_physician}, Additional_Information: {additional_information},
				Procedure_Code: {procedure_code}, Total_Charge: INR {total_charge}, Insurance_Claim_Amount: INR {insurance_claim_amount}"""
			}
			examples.append(example)
			# st.write(MedicalBilling)
			OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")

			prompt_template = FewShotPromptTemplate(
				prefix=SYNTHETIC_FEW_SHOT_PREFIX,
				examples=examples,
				suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
				input_variables=["subject", "extra"],
				example_prompt=OPENAI_TEMPLATE,
			)

			synthetic_data_generator = create_openai_data_generator(
				output_schema=MedicalBilling,
				llm=ChatOpenAI(temperature=1),
				prompt=prompt_template,
			)

			synthetic_results = synthetic_data_generator.generate(
				subject="discharge_summary",
				extra="the name must be Indian name chosen at random. Make it something you wouldn't normally choose.",
				runs=run,
			)

			type(synthetic_results)

			print(synthetic_results)

			# Create a list of dictionaries from the objects
			synthetic_data = []
			for item in synthetic_results:
				synthetic_data.append({
					'Patient_ID': item.Patient_ID,
					'Patient_Name': item.Patient_Name,
					'Patient_Address': item.Patient_Address,
					'Patient_DOB': item.Patient_DOB,
					'Admitting_Diagnosis': item.Admitting_Diagnosis,
					'Hospital_Course': item.Hospital_Course,
					'Discharge_Diagnosis': item.Discharge_Diagnosis,
					'Discharge_Instructions': item.Discharge_Instructions,
					'Discharge_Disposition': item.Discharge_Disposition,
					'Discharge_Condition': item.Discharge_Condition,
					'Attending_Physician': item.Attending_Physician,
					'Additional_Information': item.Additional_Information,
					'Procedure_Code': item.Procedure_Code,
					'Total_Charge': item.Total_Charge,
					'Insurance_Claim_Amount': item.Insurance_Claim_Amount
				})

			# Create a Pandas DataFrame from the list of dictionaries
			synthetic_df = pd.DataFrame(synthetic_data)

			# Display the DataFrame
			print(synthetic_df.head)

			pdf_output_folder = "Capstone_Project/pdf"
			zip_file_path = "Capstone_Project/pdf/output.zip"

			# Generate PDFs and collect their paths
			pdf_paths = []
			# Iterate over the rows and generate PDFs
			for index, row in synthetic_df.iterrows():
				row_data = row.to_dict()  # Convert each row to a dictionary
				pdf_file = os.path.join(pdf_output_folder, f'output_{index}.pdf')
				# pdf_file = f'{pdf_output_folder}output_{index}.pdf'   # Define PDF file name for the current row
				# generate_pdf_for_row(row_data, pdf_file)
				generate_pdf_for_row(row_data, pdf_file)
				pdf_paths.append(pdf_file)

			with zipfile.ZipFile(zip_file_path, 'w') as zipf:
				for pdf_path in pdf_paths:
					zipf.write(pdf_path, os.path.basename(pdf_path))

			with open(zip_file_path, 'rb') as f:
				zip_data = f.read()
			st.download_button(label='Download PDFs as ZIP', data=zip_data, file_name='output.zip', mime='application/zip')
	else:
		st.warning("Please enter your OpenAI API  tokey continue.")
if __name__=='__main__':
    main()
