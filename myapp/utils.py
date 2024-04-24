import spacy
from faker import Faker
import pandas as pd
import os
from tqdm import tqdm
import json
import fitz  # PyMuPDF
from spacy.tokens import DocBin
import subprocess

def extract_text_from_pdf(doc_type):
    # Define paths for Tax Invoice and Payslip PDF files
    tax_invoice_path = "myapp/test_files/Tax Invoice.pdf"
    pay_slip_path = "myapp/test_files/PaySlip.pdf"

    if doc_type == "TAX_INVOICE":
        pdf_file_path = tax_invoice_path
    elif doc_type == "PAYSLIP":
        pdf_file_path = pay_slip_path

    # Extract text from the selected PDF file
    page_text = ""
    with fitz.open(pdf_file_path) as doc:
        if doc:
            for page in doc:
                page_text += page.get_text()
                page_text += "\n\n"  # Add two new lines after each page
        else:
            print("File Not Found")   
    # return the extracted text
    return page_text
    
def get_entities(page_text):
    nlp1 = spacy.load(r"myapp/output/model-best") 
    doc = nlp1(page_text)

    entities = []
    # Iterate over the entities and append text and label to the list
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))

    # return the list of entities
    return entities


def train_spacy_with_entities(TRAIN_DATA):
    # Read data from the JSON file as text, specifying the encoding
    with open('myapp/TrainingDataSet.json', 'r', encoding='utf-8') as file:
        json_text = file.read()

    # Parse the JSON text
    data = json.loads(json_text)

    # Extract the 'annotations' from the JSON data
    annotations = data['annotation']

    # Define TRAIN_DATA as an empty list
    TRAIN_DATA = []

    # Iterate over each annotation and append it to TRAIN_DATA
    for annotation in annotations:
        TRAIN_DATA.append(annotation)

    nlp = spacy.blank("en") # load a new spacy model
    #nlp = spacy.load("en_core_web_sm") # load other spacy model

    db = DocBin() # create a DocBin object
    skipped_entities = []
    for text, annot in tqdm(TRAIN_DATA): # data in previous format
        doc = nlp.make_doc(text) # create doc object from text
        ents = []
        for start, end, label in annot["entities"]: # add character indexes
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                skipped_entities.append((text, start, end, label))
                print("Skipping entity:", text, start, end, label)
            else:
                ents.append(span)
        doc.ents = ents # label the text with the ents
        db.add(doc)

    # Print skipped entities
    print("Skipped entities:")
    for entity in skipped_entities:
        print(entity)

    current_folder = os.getcwd()
    print("Current folder path:", current_folder)
    os.chdir(current_folder)
    db.to_disk("./train.spacy") # save the docbin object
    
    command = "python3 -m spacy train myapp/output/model-best/config.cfg --output myapp/output --paths.train ./train.spacy --paths.dev ./train.spacy"
    try:
        subprocess.run(command, shell=True, check=True)
        print("SpaCy training completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running SpaCy training: {e}")

def generate_fake_value(label):
    faker = Faker()
    if label == "FULL_NAME":
        return faker.name()
    elif label == "ADDRESS":
        return faker.address()
    elif label == "VAT":
        return "{} {} {} {}".format(faker.random_number(digits=3), faker.random_number(digits=4), faker.random_number(digits=2), faker.random_number(digits=2))
    elif label == "Salary":
        return "£" + str(faker.random_number(digits=4)) + "." + str(faker.random_number(digits=2))
    elif label == "TaxCode":
        return str(faker.random_number(digits=4)) + "L"
    elif label == "BAN":
        return str(faker.random_number(digits=8))
    elif label == "NI":
        return faker.random_letter() + str(faker.random_number(digits=6)) + faker.random_letter()
    elif label == "Sort_Code":
        return "{}-{}-{}".format(faker.random_number(digits=2), faker.random_number(digits=2), faker.random_number(digits=2))
    elif label == "Date":
        return str(faker.date())
    elif label == "Invoice_Number":
        return str(faker.random_number(digits=2)) + "/" + str(faker.random_number(digits=4))
    elif label == "Money":
        return "£" + str(faker.random_number(digits=3)) + "." + str(faker.random_number(digits=2))
    elif label == "Phone_Number":
        return faker.phone_number()
    else:
        return None  # Return None for unrecognized labels
    

def MaskedData(entities, invoice_text):
    # Initialize an empty string to store modified text
    modified_text = invoice_text
    
    # Iterate over the identified entities
    for ent_text, ent_label in entities:
        # Generate fake value based on the entity label
        fake_value = generate_fake_value(ent_label)
        
        # Check if fake value is not None
        if fake_value is not None:
            # Replace the entity text with the fake value in the text
            modified_text = modified_text.replace(ent_text, fake_value)
    
    # Replace '\n' with actual newline character '\n'
    modified_text = modified_text.replace('\\n', '\n')
    
    # Return the modified text
    return modified_text

# Function to return original data
def OriginalData(invoice_text):
    invoice_text = invoice_text.replace('\\n', '\n')
    # Return the original text
    return invoice_text

