import pymongo
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from skill_list import skills
# Connect to MongoDB
skills.sort()
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["jobs"]
collection = db["narkuri_tech_jobs"]

# Retrieve transaction data from MongoDB
transactions = collection.find({}, {"_id": 0, "skills": 1})

# Preprocess data if needed (e.g., remove duplicates)

# Convert data to a suitable format for Apriori (e.g., list of lists)
basket_data = []
for transaction in transactions:
    transaction["skills"].sort()
    basket_data.append(transaction["skills"])
# Create a set of all unique items
#print(basket_data)
transaction_list = list(basket_data)
all_items = set(item for sublist in transaction_list for item in sublist)
all_items=list(all_items)
all_items.sort()
# Initialize an empty list to store boolean values
boolean_list = []
print("all_items")
n=len(skills)
print(n)
# Populate the boolean list
"""for sublist in transaction_list:
    boolean_sublist = [item in sublist for item in all_items]
    boolean_list.append(boolean_sublist)"""

for sublist in skills:
    i=0
    j=0
    boolean_sublist=[]
    m=len(sublist)
    for j in range(0,n):
        
        if i<m and sublist[i]==all_items[j]:
            i=i+1
            boolean_sublist.append(True)
        elif i<m and all_items[j]<sublist[i]:
            boolean_sublist.append(False)
        else:
            i=i+1
        
    boolean_list.append(boolean_sublist)

print("booleanist")
print(boolean_list)
# Convert the list of lists to a DataFrame (optional)
import pandas as pd
df = pd.DataFrame(boolean_list, columns=skills)

# Display the DataFrame
print(df)

# Apply Apriori algorithm
frq_items = apriori(df, min_support=0.2, use_colnames=True)

# Store frequent itemsets in another MongoDB collection
frequent_itemsets_collection = db["frequent_itemsets"]
for index, row in frq_items.iterrows():
    frequent_itemsets_collection.insert_one({"itemset": list(row["itemsets"]), "support": row["support"]})

# Optionally, you can also generate association rules
#rules = association_rules(frq_items, metric="lift", min_threshold=1)

# Close the MongoDB connection
client.close()
