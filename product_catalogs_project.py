# -*- coding: utf-8 -*-
"""product_catalogs_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WcKLMv24uYRGOTtJY-XSKtWEBlV6vt-i
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer, util
import time
import torch
import matplotlib.pyplot as plt

"""# **Exploratory Data Analysis**"""

df = pd.read_csv('amazon_co-ecommerce_sample.csv')
df

"""### Check Category Distribution"""

df['amazon_category_and_sub_category'].value_counts()

"""# **Data Preprocessing & Feature Engineering**

### Check Missing Value in Used Column & Drop it

#### Column Price
"""

df['price'].isna().sum()

df = df.dropna(subset=['price'])
df['price'].isna().sum()

# Replace £123,000.20 into float
df['price'] = df['price'].apply(lambda x: float(x.replace('£','').replace(',','').split('-')[0]))

"""#### Column Sub Category"""

df['amazon_category_and_sub_category'].isna().sum()

df = df.dropna(subset=['amazon_category_and_sub_category'])
df['amazon_category_and_sub_category'].isna().sum()

"""##### Create Category to New Column"""

# Example 'Hobbies > Model Trains & Railway Sets > Rail Vehicles > Trains' into 4 Column
df['amazon_category_and_sub_category'] = df['amazon_category_and_sub_category'].apply(lambda x: list(map(str.strip, x.split('>'))))

# Commented out IPython magic to ensure Python compatibility.
# %%time
# df = df.assign(**df.amazon_category_and_sub_category.apply(pd.Series).add_prefix('category_'))
# #df.assign(**pd.DataFrame(df.amazon_category_and_sub_category.values.tolist()).add_prefix('category_'))

# Showed Category 0 - Category 4
df.head()

"""#### Column Product Information / Description"""

df['product_information'].isna().sum()

df = df.dropna(subset=['product_information'])
df['product_information'].isna().sum()

"""### Final Shape"""

df.shape

df.info()

df.head()

"""### Select Only Used Columns"""

df = df[['product_name', 'price', 'product_information', 'category_1']]
df

"""### Concat All Used Columns"""

df['content'] = df.agg(lambda x: f"price: {x['price']} category: {x['category_1']} product name: {x['product_name']} desc: {x['product_information']}", axis=1)
df['content']

df.head()

"""### Train Test Split"""

df_train, df_test = train_test_split(df, test_size=0.1,random_state=28)

df_train

df_train.reset_index(drop=True, inplace=True)

"""# **Generate Product Embeddings**"""

#Encoding to embedding using pretrained model
model = SentenceTransformer('all-MiniLM-L6-v2')

list_content = df_train['content'].to_list()

corpus_embeddings = model.encode(list_content, show_progress_bar=True, convert_to_tensor=True)
corpus_embeddings = corpus_embeddings.to('cpu')

"""## **Fast Clustering**"""

print("Start clustering")
start_time = time.time()

clusters = util.community_detection(corpus_embeddings, min_community_size=3, threshold=0.8)

print("Clustering done after {:.2f} sec".format(time.time() - start_time))

"""### Show Cluster"""

for i, cluster in enumerate(clusters):
    print("\nCluster {}, #{} Elements ".format(i+1, len(cluster)))
    for sentence_id in cluster[0:3]:
        print("\t", list_content[sentence_id])
    print("\t", "...")
    for sentence_id in cluster[-3:]:
        print("\t", list_content[sentence_id])

"""### Total Data Clustered"""

sum_clustered =0
for i in range(len(list_content)):
    tf = any(i in x for x in clusters)
    if tf:
        sum_clustered += 1

sum_clustered

"""## **Remove Community Cluster Duplicate**"""

lists_elements_count = 0

for ele in clusters:
    lists_elements_count += len(ele)

print('length of list of lists is =',lists_elements_count)

"""### So there is no duplicate."""

def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)

idx_clustered = {}
new_cluster = []

for index, i in enumerate(clusters):
    temp_list = clusters[index]
    temp_dup = []
    for j in clusters[index]:
        if j in idx_clustered:
            temp_dup.append(j[:])
        else:
            idx_clustered[j] = 1

    delete_multiple_element(temp_list, temp_dup)
    new_cluster.append(temp_list[:])

"""# **Retraining**

### Total data not clustered
"""

single_member = [i for i in range(len(list_content)) if i not in idx_clustered]
len(single_member)

"""### Get small member cluster (below 10 member) & large member (more than 10 member)"""

small_member = []
large_member = []
for index, i in enumerate(clusters):
    if len(i) < 11:
        for j in clusters[index]:
            small_member.append(j)
    else:
        large_member.append(i[:])

print(len(small_member))
print(len(large_member))

"""### Total Data Large Member"""

lists_elements_count = 0

for ele in large_member:
    lists_elements_count += len(ele)

print('length of list of lists is =',lists_elements_count)

"""### Concat Small and not clustered member into 1 list"""

concate_small_single = [*small_member, *single_member]
len(concate_small_single)

"""### Save count of member & member before recluster"""

before_recluster = [0, 0, 0, 0, 0, 0]
before_recluster[0] = len(single_member)
before_recluster[1] = len(small_member)

for cluster in clusters:
    if (len(cluster) > 10) and (len(cluster) <= 30):
        before_recluster[2] += len(cluster)
    elif (len(cluster) > 30) and (len(cluster) <= 50):
        before_recluster[3] += len(cluster)
    elif (len(cluster) > 50) and (len(cluster) <= 100):
        before_recluster[4] += len(cluster)
    elif len(cluster) > 100:
        before_recluster[5] += len(cluster)

before_recluster

import copy
cluster_before = copy.deepcopy(clusters)

#cluster_before = clusters[:]

"""### **Note: Due to list append python can change older list, so we need to run from fast clustering again**

## Retraining Using Nearest Member to Member
"""

def retrain(small_list, big_list, model_retrain, all_list_content, all_cluster):
    bigger_list = copy.deepcopy(big_list)
    all_index_cluster = copy.deepcopy(all_cluster)


    # Change from index to content
    content_group =[]
    for i in range(len(bigger_list)):
        temp_content_group = []
        for j in range(len(bigger_list[i])):
            temp_content_group.append(all_list_content[bigger_list[i][j]])

        content_group.append(temp_content_group[:])

    # Change Embedding big member group
    list_embedding_big = []
    for content_big in content_group:
        list_embedding_big.append(model_retrain.encode(content_big, convert_to_tensor=True).to('cpu'))



    content_small_list =[]
    for i in range(len(small_list)):
        content_small_list.append(all_list_content[small_list[i]])

    list_embedding_small = []
    for content_small in content_small_list:
        list_embedding_small.append(model_retrain.encode(content_small, convert_to_tensor=True).to('cpu'))


    print('Starting to Clustering')
    list_not_clustered = []

    for idx_small, small_embed in enumerate(list_embedding_small):
        temp_highest_sim = 0
        temp_cluster = -1

        real_index = small_list[idx_small]

        small_embed = small_embed.unsqueeze(0)


        for idx_big, embed_big in enumerate(list_embedding_big):
            max_sim_big = cosine_similarity(small_embed, embed_big).max()
            if max_sim_big > temp_highest_sim:
                temp_highest_sim = max_sim_big
                temp_cluster = idx_big



        # Threshold
        if temp_highest_sim > 0.8:
            founded = False
            for i in range(len(all_index_cluster)): # If had clustered before
                if real_index in all_index_cluster[i]:
                    all_index_cluster[i].remove(real_index)
                    all_index_cluster[temp_cluster].append(real_index)
                    founded = True
                    break;

            if founded == False:
                all_index_cluster[temp_cluster].append(real_index)

        else:
            founded = False
            for i in range(len(all_index_cluster)): # If had clustered before
                if real_index in all_index_cluster[i]:
                    founded = True
                    break;
            if founded == False:
                list_not_clustered.append(real_index)


    return all_index_cluster, list_not_clustered

# Commented out IPython magic to ensure Python compatibility.
# %%time
# recluster_list, not_clustered_list =  retrain(concate_small_single, large_member, model, list_content, clusters)

"""### Total data still not clustered after reclustering"""

len(not_clustered_list)

"""### Total data after reclustered"""

lists_elements_count = 0

for ele in recluster_list:
    lists_elements_count += len(ele)

print('length of list of lists is =',lists_elements_count)

"""### Total data before reclustered"""

lists_elements_count = 0

for ele in cluster_before:
    lists_elements_count += len(ele)

print('length of list of lists is =',lists_elements_count)

# Total Data
6547 + 617

2745 + 600 + 3819

"""### Save Count of Member & Member after reclustering member to member"""

after_recluster = [0, 0, 0, 0, 0, 0]
after_recluster[0] = len(not_clustered_list)

for cluster in recluster_list:
    if (len(cluster) > 1) and (len(cluster) <= 10):
        after_recluster[1] += len(cluster)
    elif (len(cluster) > 10) and (len(cluster) <= 30):
        after_recluster[2] += len(cluster)
    elif (len(cluster) > 30) and (len(cluster) <= 50):
        after_recluster[3] += len(cluster)
    elif (len(cluster) > 50) and (len(cluster) <= 100):
        after_recluster[4] += len(cluster)
    elif len(cluster) > 100:
        after_recluster[5] += len(cluster)

after_recluster

before_recluster

"""## Retraining Using Nearest Member to Centroid

### Total data not clustered
"""

single_member_centroid = [i for i in range(len(list_content)) if i not in idx_clustered]
len(single_member_centroid)

"""### Get small member cluster (below 10 member) & large member (more than 10 member)"""

small_member_cen = []
large_member_cen = []
for index, i in enumerate(cluster_before):
    if len(i) < 11:
        for j in cluster_before[index]:
            small_member_cen.append(j)
    else:
        large_member_cen.append(i[:])

print(len(small_member_cen))
print(len(large_member_cen))

"""### Total Data Large Member"""

lists_elements_count = 0

for ele in large_member_cen:
    lists_elements_count += len(ele)

print('length of list of lists is =',lists_elements_count)

"""### Concat Small and not clustered member into 1 list"""

concate_small_single_cen = [*small_member_cen, *single_member_centroid]
len(concate_small_single_cen)

import copy
cluster_before_cen = copy.deepcopy(cluster_before)

def retrain_centroid(small_list, big_list, model_retrain, all_list_content, all_cluster):
    bigger_list = copy.deepcopy(big_list)
    all_index_cluster = copy.deepcopy(all_cluster)


    # Change from index to content
    content_group =[]
    for i in range(len(bigger_list)):
        temp_content_group = []
        for j in range(len(bigger_list[i])):
            temp_content_group.append(all_list_content[bigger_list[i][j]])

        content_group.append(temp_content_group[:])

    # Change Embedding big member group
    list_embedding_big = []
    for content_big in content_group:
        list_embedding_big.append(model_retrain.encode(content_big, convert_to_tensor=True).to('cpu'))

    # Get Centroid of every cluster
    list_embedding_centroid = []
    for index, embed in enumerate(list_embedding_big):
        list_embedding_centroid.append(torch.tensor([sum(i)/len(embed) for i in zip(*embed)]))


    content_small_list =[]
    for i in range(len(small_list)):
        content_small_list.append(all_list_content[small_list[i]])

    list_embedding_small = []
    for content_small in content_small_list:
        list_embedding_small.append(model_retrain.encode(content_small, convert_to_tensor=True).to('cpu'))


    print('Starting to Clustering')
    list_not_clustered = []

    for idx_small, small_embed in enumerate(list_embedding_small):
        temp_highest_sim = 0
        temp_cluster = -1

        real_index = small_list[idx_small]

        small_embed = small_embed.unsqueeze(0)


        for idx_big, embed_big in enumerate(list_embedding_centroid):
            max_sim_big = cosine_similarity(small_embed, embed_big.unsqueeze(0)).max()
            if max_sim_big > temp_highest_sim:
                temp_highest_sim = max_sim_big
                temp_cluster = idx_big


        # Threshold
        if temp_highest_sim > 0.8:
            founded = False
            for i in range(len(all_index_cluster)): # If had clustered before
                if real_index in all_index_cluster[i]:
                    all_index_cluster[i].remove(real_index)
                    all_index_cluster[temp_cluster].append(real_index)
                    founded = True
                    break;

            if founded == False:
                all_index_cluster[temp_cluster].append(real_index)

        else:
            founded = False
            for i in range(len(all_index_cluster)): # If had clustered before
                if real_index in all_index_cluster[i]:
                    founded = True
                    break;
            if founded == False:
                list_not_clustered.append(real_index)



    return all_index_cluster, list_not_clustered

# Commented out IPython magic to ensure Python compatibility.
# %%time
# recluster_list_cen, not_clustered_list_cen =  retrain_centroid(concate_small_single_cen, large_member_cen, model, list_content, cluster_before)

lists_elements_count = 0

for ele in recluster_list_cen:
    lists_elements_count += len(ele)

print('length of list of lists is =',lists_elements_count)

len(not_clustered_list_cen)

907 + 6257

"""### Save count of member & centroid after recluster"""

after_recluster_cen = [0, 0, 0, 0, 0, 0]
after_recluster_cen[0] = len(not_clustered_list_cen)

for cluster in recluster_list_cen:
    if (len(cluster) > 1) and (len(cluster) <= 10):
        after_recluster_cen[1] += len(cluster)
    elif (len(cluster) > 10) and (len(cluster) <= 30):
        after_recluster_cen[2] += len(cluster)
    elif (len(cluster) > 30) and (len(cluster) <= 50):
        after_recluster_cen[3] += len(cluster)
    elif (len(cluster) > 50) and (len(cluster) <= 100):
        after_recluster_cen[4] += len(cluster)
    elif len(cluster) > 100:
        after_recluster_cen[5] += len(cluster)
    elif len(cluster) == 1:
        after_recluster_cen[0] += 1

after_recluster_cen

before_recluster

"""### Visualization"""

fig = plt.figure(figsize = (10, 5))
#ax.plot(after_recluster_cen)
lab = ['Single Member',
'Very Small \n (2-10 Member)',
'Small Member \n (11-30 Member)',
'Medium Member \n (31-50 Member)',
'Large Member \n (50-100 Member)',
'Very Large Member \n ( > 100 Member)']

recluster_cen_viz = [x/sum(before_recluster)*100 for x in before_recluster]

plt.bar(lab, recluster_cen_viz, color ='maroon',
        width = 0.6)

plt.xlabel("Cluster Size")
plt.ylabel("(%) of All Products")
plt.title("Before Reclustering")

plt.show()

fig = plt.figure(figsize = (10, 5))
#ax.plot(after_recluster_cen)
lab = ['Single Member',
'Very Small \n (2-10 Member)',
'Small Member \n (11-30 Member)',
'Medium Member \n (31-50 Member)',
'Large Member \n (50-100 Member)',
'Very Large Member \n ( > 100 Member)']

recluster_cen_viz = [x/sum(after_recluster)*100 for x in after_recluster]

plt.bar(lab, recluster_cen_viz, color ='maroon',
        width = 0.6)

plt.xlabel("Cluster Size")
plt.ylabel("(%) of All Products")
plt.title("After Reclustering Member to Member")

plt.tight_layout()

plt.show()

fig = plt.figure(figsize = (10, 5))
#ax.plot(after_recluster_cen)
lab = ['Single Member',
'Very Small \n (2-10 Member)',
'Small Member \n (11-30 Member)',
'Medium Member \n (31-50 Member)',
'Large Member \n (50-100 Member)',
'Very Large Member \n ( > 100 Member)']

recluster_cen_viz = [x/sum(after_recluster_cen)*100 for x in after_recluster_cen]

plt.bar(lab, recluster_cen_viz, color ='maroon',
        width = 0.6)

plt.xlabel("Cluster Size")
plt.ylabel("(%) of All Products")
plt.title("After Reclustering Member to Centroid")

plt.tight_layout()

plt.show()

"""# **Evaluation**

### Score before recluster
"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# # Change from index to content
# content_group_before =[]
# for i in range(len(cluster_before)):
#     temp_content_group = []
#     for j in range(len(cluster_before[i])):
#         temp_content_group.append(list_content[cluster_before[i][j]])
# 
#     content_group_before.append(temp_content_group[:])
# 
# # Change Embedding big member group
# list_embedding_before = []
# for content_big in content_group_before:
#     list_embedding_before.append(model.encode(content_big, convert_to_tensor=True).to('cpu'))

# Commented out IPython magic to ensure Python compatibility.
# %%time
# x_before = []
# label_before = []
# for index, per_cluster in enumerate(list_embedding_before):
#     for embed in per_cluster:
#         x_before.append(embed.cpu().detach().numpy())
#         label_before.append(index)
# 
# print(len(x_before))
# print(len(label_before))

silhouette_score(x_before, label_before)

"""### Score after recluster"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# # Change from index to content
# content_group_after =[]
# for i in range(len(recluster_list)):
#     temp_content_group = []
#     for j in range(len(recluster_list[i])):
#         temp_content_group.append(list_content[recluster_list[i][j]])
# 
#     content_group_after.append(temp_content_group[:])
# 
# # Change Embedding big member group
# list_embedding_after = []
# for content_big in content_group_after:
#     list_embedding_after.append(model.encode(content_big, convert_to_tensor=True).to('cpu'))

# Commented out IPython magic to ensure Python compatibility.
# %%time
# x_after = []
# label_after = []
# for index, per_cluster in enumerate(list_embedding_after):
#     for embed in per_cluster:
#         x_after.append(embed.cpu().detach().numpy())
#         label_after.append(index)
# 
# print(len(x_after))
# print(len(label_after))

silhouette_score(x_after, label_after)

"""### Score after recluster centroid"""

print(len(recluster_list_cen))
recluster_list_cen = [s for s in recluster_list_cen if s != []]
print(len(recluster_list_cen))

# Commented out IPython magic to ensure Python compatibility.
# %%time
# # Change from index to content
# content_group_after =[]
# for i in range(len(recluster_list_cen)):
#     temp_content_group = []
#     for j in range(len(recluster_list_cen[i])):
#         temp_content_group.append(list_content[recluster_list_cen[i][j]])
# 
#     content_group_after.append(temp_content_group[:])
# 
# # Change Embedding big member group
# list_embedding_after_cen = []
# for content_big in content_group_after:
#     list_embedding_after_cen.append(model.encode(content_big, convert_to_tensor=True).to('cpu'))

# Commented out IPython magic to ensure Python compatibility.
# %%time
# x_after_cen = []
# label_after_cen = []
# for index, per_cluster in enumerate(list_embedding_after_cen):
#     for embed in per_cluster:
#         x_after_cen.append(embed.cpu().detach().numpy())
#         label_after_cen.append(index)
# 
# print(len(x_after_cen))
# print(len(label_after_cen))

silhouette_score(x_after_cen, label_after_cen)

"""--------------------------------------------------------------------------------------------------------------------------------"""

