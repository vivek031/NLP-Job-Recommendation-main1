from flask import Flask , render_template , url_for , redirect , abort , request
from pymongo import MongoClient
import pymongo
import operator
import spacy
import nltk
from trie import insertList,filtered_skills
import PyPDF2
import re
insertList()
app = Flask(__name__)

#EXTRACT SKILLS FROM THE GIVEN TEXT
def extract_information_from_user(text):
    
    key=[]
    value=[]
    # nlp = spacy.load("./output/model-best/")
    tokens= nltk.word_tokenize(text)
    stopwords = nltk.corpus.stopwords.words('english')
    SKILLS = [word for word in tokens if word not in stopwords]
    SKILLS=filtered_skills(SKILLS)
    #print("hi")
    #nlp = spacy.load("C:/Users/vivek/OneDrive/Desktop/All folder/8th sem/project/NLP-Job-Recommendation-main/NLP-Job-Recommendation-main/output/model-best")
    #print("nlp is ",nlp)
    # doc = model(text)
   # print(doc)
    """for ent in doc.ents:
        key.append(ent.label_)
        value.append(ent.text)
"""
    #print(key)
    #print(value)
    Dict = {key[i]: value[i] for i in range(len(key))}

    #SKILLS= doc.split(",")
    print(SKILLS)
    Dict.update(SKILLS=SKILLS)

    text = Dict["SKILLS"]
    print(text)

    return retirve_info_from_db(text)

#RETRIVE RELATED JOBS BASED ON JACCARD COEFFICIENT 
def retirve_info_from_db(user_list):

    len_user_list = len(user_list)
    print("len user list",len_user_list)
    print(mydb)
    n = mydb.find( { 'skills': { '$in': user_list}} ,{'_id':0}) #COLLECTING JOBS BASED ON MATCHING SKILLS
    print("jbos are",n)
    jobs = []
    for i in n:

        job_skills = i['skills']
        print("skills ",job_skills)

        match = len([k for k , val in enumerate(job_skills) if val in user_list])
        
        total_len = len(job_skills) + len_user_list 
        i['rank'] = match/total_len #RANKING COEFFICIENT
        jobs.append(i)

    return show_info(jobs , user_list , len(jobs))

#SORT THE JOBS RANK WISE AND DISPLAY
def show_info(jobs , job_skills , job_len):

    jobs.sort(key=operator.itemgetter('rank') , reverse=True) #SORTING JOBS BASED ON THE RANK SCORE
    return render_template('show_job.html' , jobs=jobs , job_skills=job_skills , job_len=job_len)
 

def extract_text_from_pdf(file):
    # Create a PDF file reader object
    pdf_reader = PyPDF2.PdfReader(file)
    
    # Initialize an empty string to store extracted text
    text = ""
    
    # Iterate through each page of the PDF
    for page in pdf_reader.pages:
        # Extract text from the current page
        # page = pdf_reader.getPage(page_num)
        page_text = page.extract_text()
        page_text = re.sub(r'[^a-zA-Z\s]', '', page_text)
        text+=page_text

    
    # Close the PDF file
    file.close()
    
    return text


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/', methods=['POST'])
# def my_form_post():
#     text = request.form['text']
#     print("fahfakshfaskhfask   ",text)

#     return extract_information_from_user(text)    
def my_form_post():
    print("response is ",request)
    if 'resume' in request.files:  # Check if a file is uploaded
        uploaded_file = request.files['resume']
        if uploaded_file.filename != '':
            file_text = extract_text_from_pdf(uploaded_file)
            print(file_text)
            return extract_information_from_user(file_text)
    elif 'text' in request.form:  # Check if text is entered manually
        text = request.form['text']
        return extract_information_from_user(text)


if __name__ == "__main__":
    
    #CONNECTING WITH MONGO DB
    connection_string = "mongodb://localhost:27017"
    client = MongoClient(connection_string)

    db = client['jobs']
    mydb = db['narkuri_tech_jobs']

    
    #STARTING THE APPLICATION
    app.run(host="0.0.0.0" ,port=5000, debug = True)