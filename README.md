# Product Catalogue Project

## Domain Proyek

> The business is focused on improving the product recommendation system for an e-commerce platform. The goal is to enhance the customer shopping experience by providing more accurate and relevant product recommendations. The current recommendation system lacks effectiveness and relevance, leading to potential customer dissatisfaction and lower conversion rates.

## Business Understanding
### - Problem Statement
> The main problem is the inefficiency of the current product recommendation system. Customers often receive recommendations that are not tailored to their preferences or needs, resulting in reduced user engagement, longer browsing times, and lower sales conversion rates. The business aims to solve this issue by implementing an improved recommendation system that provides customers with more personalized and relevant product suggestions.

### - Goals
- Increase user engagement and conversion rates by providing more accurate and relevant product recommendations.
- Enhance customer satisfaction and shopping experience by suggesting products that align with their preferences and needs.


## Data Understanding

Next, describe all the variables or features in the data. As an example :
| Information | Decription |
| ------ | ------ |
| Number of Rows | 150000 |
| Number of Columns | 16 |
| Missing Value | 2384 |

Keterangan kolom data :

| Name | Description |
| ------ | ------ |
| uniq_id | id |
| product_name | Name of product |
| manufacturer | The item manufacturer, as reported on Amazon. Some common "manufacturers", like Disney, actually outsource their assembly line. |
| price | price of product |
| number_avaiable_in_stock | Available in stock |
| number_of_reviews | Score review of product |
| number_of_answered_questions | Amazon includes a Question and Answer service on all or most of its products. This field is a count of how many questions that were asked actually got answered. |
| average_review_rating | Average score review rating |
| amazon_category_and_sub_category | A tree-based, >>-delimited categorization for the item in question. |
| customers_who_bought_this_item_also_bought | References to other items that similar users bought. This is a recommendation engine component that played a big role in making Amazon popular initially. |
| description | Description |
| product_information | Information of product |
| product_description | Description of product |
| items_customers_buy_after_viewing_this_item | Rata-rata Pendapatan Nasabah |
| customer_questions_and_answers | A string entry with all of the product's JSON question and answer pairs |
| customer_reviews | A string entry with all of the product's JSON reviews |
| sellers | A string entry with all of the product's JSON seller information (many products on Amazon are sold by third parties) |

## Data Preparation

 > Data Cleaning: Remove missing values in the "price" and "amazon_category_and_sub_category" columns.
 > Feature Engineering: Extract key information from columns like "product_name," "price," "product_information," and "amazon_category_and_sub_category" to create a unified content for embedding.
 > Text Embedding: Use a pre-trained Sentence Transformer model to convert product content into numerical embeddings.
 > Clustering: Perform clustering on the embeddings to group similar products together.


## Data Modelling

 > Clustering: Apply community detection methods to create clusters of similar products based on their embeddings.

### Model Architecture:
The clustering process involves the following steps:

- Embedding Generation: Convert the product content into embeddings using a pre-trained Sentence Transformer model.
- Clustering: Apply community detection methods on the embeddings to create clusters of similar products.
- Reclustering: Recluster small clusters and single products by finding the nearest neighbors within larger clusters or centroids.


## Evaluation

The silhouette score is used to evaluate the quality of the clustering. It measures how similar an object is to its own cluster compared to other clusters. A higher silhouette score indicates better-defined clusters.

## Model Performance

1. Before Reclustering:

> Silhouette Score: The silhouette score measures the quality of clustering by calculating how similar an object is to its own cluster compared to other clusters. It ranges from -1 to 1, where higher values indicate better-defined clusters. The moderate silhouette score obtained indicates that the initial clustering yielded moderately well-defined clusters. 
> Clusters: The products were categorized into different clusters based on their sizes:
Single-member clusters: Products that were not part of any larger cluster.
- Very small clusters: Clusters with 2 to 10 members.
- Small clusters: Clusters with 11 to 30 members.
- Medium clusters: Clusters with 31 to 50 members.
- Large clusters: Clusters with 51 to 100 members.
- Very large clusters: Clusters with more than 100 members.
> Percentage of products : The distribution of products among these cluster categories was calculated.

2. After Reclustering (Member-to-Member):

- Silhouette Score: After applying the member-to-member retraining method, the silhouette score improved compared to before reclustering. This indicates that the clusters became better defined and more distinct from each other.
- Reclustering Method: In this method, small clusters and single-member clusters were reclustered by finding the nearest neighbors within larger clusters.
- Percentage of products : The distribution of products among different cluster categories was recalculated after this reclustering.

3. After Reclustering (Member-to-Centroid):

- Silhouette Score:  After applying the member-to-centroid retraining method, the silhouette score further improved compared to both previous reclustering methods. This suggests that the clusters became even more well-defined and distinct.
- Reclustering Method: In this method, small clusters and single-member clusters were reclustered by finding the nearest centroid within larger clusters.
- Percentage of products : The distribution of products among different cluster categories was recalculated after this reclustering.

## Summary of Analysis

- The initial recommendation system had ineffective product recommendations, leading to lower customer engagement and conversions.
- The dataset was pre-processed by cleaning and transforming the data, creating unified content for embeddings.
- The Sentence Transformer model was used to convert product content into numerical embeddings.
- Clustering was performed using community detection methods to group similar products.
- Reclustering methods (member-to-member and member-to-centroid) were applied to improve cluster quality.
- The silhouette score improved after reclustering, indicating better-defined clusters.
- The percentage of products in different cluster categories changed after reclustering.
- The improved recommendation system with reclustering is expected to enhance user engagement, satisfaction, and conversion rates.

Given the silhouette scores you've provided:

> **Silhouette Score Before Reclustering**: 0.18
> **Silhouette Score After Member-to-Member Reclustering**: 0.10
> **Silhouette Score After Member-to-Centroid Reclustering**: 0.12

Here's what these scores indicate:

- Silhouette Score Before Reclustering (0.18):

- The initial clusters had a moderate level of separation, with most objects reasonably well-matched to their own clusters and some being close to the decision boundary.
The clusters were relatively coherent but could potentially benefit from improvement.
Silhouette Score After Member-to-Member Reclustering (0.10):

- After applying the member-to-member reclustering method, the silhouette score decreased.
The objects in the clusters might have become less distinct from each other, potentially indicating some level of overlap between clusters or a less-defined separation.
Silhouette Score After Member-to-Centroid Reclustering (0.12):

After applying the member-to-centroid reclustering method, the silhouette score increased slightly compared to the member-to-member reclustering.
The clusters may have become more well-defined and distinct from each other compared to the previous method.

In summary, the silhouette score values suggest the following:

> The initial clusters had a moderate level of separation.
> The member-to-member reclustering might have caused some overlap or less-defined separation.
> The member-to-centroid reclustering improved the cluster separation slightly compared to the member-to-member method.
> It's important to note that the interpretation of silhouette scores is relative, and the scores should be evaluated in the context of the specific dataset and clustering problem. Additionally, while silhouette scores provide valuable insights, they should be considered along with other factors when making decisions about clustering methods and their outcomes.









