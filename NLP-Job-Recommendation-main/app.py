from flask import Flask , render_template , url_for , redirect , abort , request
from pymongo import MongoClient
import pymongo
import operator
# import spacy
import nltk
from trie import insertList,filtered_skills
import PyPDF2
import re
import math
from mlxtend.frequent_patterns import apriori
# from mlxtend.frequent_patterns import association_rules
import pandas as pd

insertList()
app = Flask(__name__)



#EXTRACT SKILLS FROM THE GIVEN TEXT
def extract_information_from_user(text):
    
    key=[]
    value=[]
    # nlp = spacy.load("./output/model-best/")
    tokens= nltk.word_tokenize(text)
    tokens = list(set(tokens))

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

    return retrieve_info_from_db(text)

#RETRIVE RELATED JOBS BASED ON JACCARD COEFFICIENT 

def expected_salary(salary):
    l=len(salary)
    sum=0
    value=0
    for i in range(0,l):
        if(salary[i]=='-'):
            sum+=value
            value=0
        elif(salary[i]>='0' and salary[i]<='9'):
            value=value*10+int(salary[i])-int('0') 
    if value!=0 and sum!=0:
        return (value+sum)/2
    else:
        return value 
 
# Function to retrieve information from the database and calculate expected salary
def retrieve_info_from_db(user_list):
    len_user_list = len(user_list)
    print("Length of user list:", len_user_list)

    jobsmatched = mydb.find({'skills': {'$in': user_list}}, {'_id': 0})
    # noOfjobs = jobsmatched.count_documents()
    # print("Number of Jobs Retrieved:", noOfjobs)
    temp=jobsmatched
    print(temp)
    print("hello")
    frequent_skills_sets = findfrequentskillset(user_list)
    print(temp)
    print("completed")
    jobs = []
    for i in jobsmatched:
        job_skills = i['skills']
        print("Skills for job:", job_skills)

        match = len([k for k, val in enumerate(job_skills) if val in user_list])
        total_len = len(job_skills) + len_user_list 
        i['rank'] = match / total_len  # RANKING COEFFICIENT

        # Calculate expected salary for the current job
        
        difficulty=estimate_difficulty(user_list, job_skills, frequent_skills_sets)
        print(difficulty)
        i['difficulty']=difficulty

        #print(i)
        temp_salary=(str)(i['salary'])
        #print(temp_salary)
        if(expected_salary(temp_salary)==0):
            i['expected_salary']="cann't predict"
        else:
            #print(expected_salary(temp_salary))
            salary = calculate_expected_salary(i['skills'], expected_salary(temp_salary), user_list, 1/2, i['rank'])
            i['expected_salary'] = salary
        
        jobs.append(i)

    print("loop")
    return show_info(jobs, user_list, len(jobs))

# Function to calculate expected salary for a job based on the algorithm discussed earlier
def calculate_expected_salary(job_skills, job_salary, user_skills, θs, w):
    match_count = len([skill for skill in job_skills if skill in user_skills])
    total_len = len(job_skills) + len(user_skills)
    probability = 1 / (1 + (1 / (1 + w * ((match_count / len(job_skills)) - 1/2))))
    
    if match_count / len(job_skills) >= θs:
        return probability * job_salary
    else:
        return 0  # Return 0 if the job does not meet the qualification threshold




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

def findfrequentskillset(user_list):
    print("hello vivek")
    job_listings = mydb.find({'skills': {'$in': user_list}}, {'_id': 0})
    #job_listings = mydb.find({}, {"_id": 0, "skills": 1})

# Extract skills
    all_skills = []
    for job in job_listings:
        all_skills.append(job["skills"])
    #print(all_skills)
    # Flatten the list of skills
    flattened_skills = [skill for sublist in all_skills for skill in sublist]

    # Convert the list of skills to a dataframe
    df = pd.DataFrame(flattened_skills, columns=["Skill"])

    # Convert the dataframe to a one-hot encoded format
    one_hot_encoded = pd.get_dummies(df)

    # Find frequent itemsets using Apriori algorithm
    frequent_itemsets = apriori(one_hot_encoded, min_support=0.001, use_colnames=True)
    print ("frequent")
    print(frequent_itemsets)
    frequent_itemsets_list = []

    for _ , itemset in frequent_itemsets.iterrows():
        item=str((set(itemset['itemsets'])))
        print(item[8:-2])
        frequent_itemsets_list.append(item[8:-2])


    
    
    print(frequent_itemsets_list)

    # Print frequent itemsets
    return frequent_itemsets_list

def estimate_difficulty(user_skills, job_skills, frequent_skill_sets):
    # Initialize empty sets
    edges = {i: set() for i in range(len(frequent_skill_sets))}
    
    # Map all skills to unique identifiers
    all_skills = set(user_skills + job_skills + frequent_skill_sets)
    skill_to_id = {skill: idx for idx, skill in enumerate(all_skills)}
    
    # Convert frequent_skill_sets to sets of single skills
    frequent_skill_sets = [set([skill]) for skill in frequent_skill_sets]
    
    active_skills = {skill_id: set() for skill_id in skill_to_id.values()}
    
    # Create edges between frequent skills
    for j, frequent_skill in enumerate(frequent_skill_sets):
        for skill in frequent_skill:
            i = frequent_skill_sets.index(set([skill]))
            edges[i].add((i, j, skill_to_id[skill]))  # Use skill_id instead of skill
    
    # Initialize active sets
    for edge in edges[0]:
        active_skills[edge[2]].add(edge)
    
    # Estimate overall difficulty
    overall_difficulty = 0
    max_difficulty = len(job_skills)  # Maximum possible difficulty
    
    for job_skill in job_skills:
        di = math.inf
        for edge in active_skills.get(skill_to_id.get(job_skill, None), set()):
            start, end, skill_id = edge
        
            di = min(di, 1.0)  # Assuming a fixed difficulty value of 1 for each skill
        if(di!= math.inf):
            overall_difficulty += di
    print(max_difficulty)
    # Normalize overall difficulty to range [0, 1]
    normalized_difficulty = overall_difficulty / max_difficulty
    
    return normalized_difficulty





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