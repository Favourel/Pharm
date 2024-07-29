# recommendations/utils.py
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from .models import Order, Product


def get_recommendations(user_id, n=4):
    # Load the purchase history data from the database
    purchase_data = []
    orders = Order.objects.filter(user_id=user_id).prefetch_related('order_item__product')
    for order in orders:
        for item in order.order_item.all():
            purchase_data.append({'user_id': order.user_id, 'product_id': item.product_id})

    df = pd.DataFrame(purchase_data)
    if df.empty:
        return []

    # Count the number of purchases for each user and product combination
    purchase_counts = df.groupby(['user_id', 'product_id']).size().unstack(fill_value=0)

    # Convert the purchase counts to a sparse matrix
    sparse_purchase_counts = sparse.csr_matrix(purchase_counts)

    # Compute the cosine similarity matrix between the products
    cosine_similarities = cosine_similarity(sparse_purchase_counts.T)

    # Define a function to recommend items for a user based on their purchase history
    user_idx = df['user_id'].drop_duplicates().tolist().index(user_id)
    user_history = sparse_purchase_counts[user_idx].toarray().flatten()
    similarities = cosine_similarities.dot(user_history)

    purchased_indices = np.where(user_history > 0)[0]
    similarities[purchased_indices] = 0

    recommended_indices = np.argsort(similarities)[::-1][:n]
    recommended_items = list(purchase_counts.columns[recommended_indices])

    purchased_items = list(purchase_counts.columns[purchase_counts.loc[user_id] > 0])
    recommended_items = [item for item in recommended_items if item not in purchased_items]

    return Product.objects.filter(id__in=recommended_items)
