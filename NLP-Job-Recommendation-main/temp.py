# Example transaction list (list of lists)
transaction_list = [
    ["apple", "banana", "grape"],
    ["banana", "orange"],
    ["apple", "grape", "pear"],
]

# Create a set of all unique items
all_items = set(item for sublist in transaction_list for item in sublist)
all_items=list(all_items)
all_items.sort()
# Initialize an empty list to store boolean values
boolean_list = []

# Populate the boolean list
for sublist in transaction_list:
    boolean_sublist = [item in sublist for item in all_items]
    boolean_list.append(boolean_sublist)
print(boolean_list)
# Convert the list of lists to a DataFrame (optional)
import pandas as pd
df = pd.DataFrame(boolean_list, columns=all_items)

# Display the DataFrame
print(df)
