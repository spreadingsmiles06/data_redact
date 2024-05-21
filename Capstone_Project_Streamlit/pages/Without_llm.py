import streamlit as st
import os
from presidio_analyzer import AnalyzerEngine
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from pikepdf import Pdf, Name, Dictionary

def download_file(file_path):
    with open(file_path, "rb") as f:
        contents = f.read()
    st.download_button(label="Download", data=contents, file_name=os.path.basename(file_path))

analyzer = AnalyzerEngine()

analyze_bounding_boxes = []

# Function to combine two rectangles into one
def combine_rect(rectA, rectB):
    a, b = rectA, rectB
    startX = min(a[0], b[0])
    startY = min(a[1], b[1])
    endX = max(a[2], b[2])
    endY = max(a[3], b[3])
    return (startX, startY, endX, endY)
uploaded_file = st.file_uploader("Your PDF files", type=['PDF', 'pdf'])
if st.button("Submit"):
    name = uploaded_file.name
    st.write(name)
    # Iterate over all pages of the PDF
    for page_layout in extract_pages(uploaded_file):
        analyze_char_sets = []

        for text_container in page_layout:
            if isinstance(text_container, LTTextContainer):
                # Extract text from the container
                text_to_anonymize = text_container.get_text()

                # Analyze the text using the analyzer engine
                analyzer_results = analyzer.analyze(text=text_to_anonymize, language='en')

                characters = list([])

                # Grab the characters from the PDF
                for text_line in filter(lambda t: isinstance(t, LTTextContainer), text_container):
                    for character in filter(lambda t: isinstance(t, LTChar), text_line):
                        characters.append(character)

                # Slice out the result that match the analyzer results
                for result in analyzer_results:
                    start = result.start
                    end = result.end
                    analyze_char_sets.append({"characters": characters[start:end], "result": result})

        # Combine the bounding boxes into a single bounding box
        for analyze_char_set in analyze_char_sets:
            if analyze_char_set["characters"]:
                completeBoundingBox = analyze_char_set["characters"][0].bbox
                
                for character in analyze_char_set["characters"]:
                    completeBoundingBox = combine_rect(completeBoundingBox, character.bbox)
                    
                analyze_bounding_boxes.append({"boundingBox": completeBoundingBox, "result": analyze_char_set["result"]})

    # Create annotations for each bounding box
    annotations = []
    for analyze_bounding_box in analyze_bounding_boxes:
        boundingBox = analyze_bounding_box["boundingBox"]

        highlight = Dictionary(
            Type=Name.Annot,
            Subtype=Name.Highlight,
            QuadPoints=[boundingBox[0], boundingBox[3],
                        boundingBox[2], boundingBox[3],
                        boundingBox[0], boundingBox[1],
                        boundingBox[2], boundingBox[1]],
            Rect=[boundingBox[0], boundingBox[1], boundingBox[2], boundingBox[3]],
            C=[0, 0, 0],
            CA=1,
            T=analyze_bounding_box["result"].entity_type,
        )

        annotations.append(highlight)

    # uploaded_file = st.file_uploader("Your PDF files", type=['PDF', 'pdf'])
    # name = uploaded_file.name

    # Open the PDF file
    pdf = Pdf.open(uploaded_file)

    # Add the annotations to all pages of the PDF
    for page in pdf.pages:
        page.Annots = pdf.make_indirect(annotations)

    # Save the modified PDF
    pdf.save(name)
    st.success(name)
    # downl_path = os.join(os.getcwd(), name)
    # st.download_button(downl_path)
    download_file(name)
