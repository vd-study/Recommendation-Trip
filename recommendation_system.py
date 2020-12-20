import pandas as pd
import random
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def recommend(item_id, num,results,ds,user_budget):
    recs = results[item_id][:num]
    trip_price = 0
    recommend_activites = []
    for rec in recs:
        trip_id = rec[1]
        activiti_price = int(ds.query('data__data__id == @trip_id')['price'].tolist()[0])
        if (trip_price + activiti_price < user_budget):
            trip_price += activiti_price
            recommend_activites.append(trip_id)

    return trip_price, recommend_activites


def get_user_trip(user_id, user_budget):
    res = requests.get('https://hack-maldives.herokuapp.com/api/v1/activitites/all')
    data = res.json()
    df = pd.json_normalize(data["data"]["data"])

    df = df.drop(['id'], axis=1)

    activiti_id = df['_id'].tolist()
    visitors = df['visitors'].tolist()
    my_activiti = []
    notmy_activiti = []
    for i, visitor in enumerate(visitors):
        if (visitor[0] == user_id):
            my_activiti.append(i)
        elif (visitor[1] == user_id):
            my_activiti.append(i)
        else:
            notmy_activiti.append(i)

    my_activiti_id = []
    for index in my_activiti:
        my_activiti_id.append(df.iloc[index]['_id'])

    df = df.rename({'_id': 'data__data__id'}, axis=1)
    df = df.rename({'description': 'data__data__description'}, axis=1)
    df = df.rename({'title': 'data__data__title'}, axis=1)

    if (len(my_activiti_id) == 0):
        # In case of unforeseen circumstances
        my_activiti_id.append(random.choice(activiti_id))

    ds = df

    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
    tfidf_matrix = tf.fit_transform(ds['data__data__description'])

    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

    results = {}

    for idx, row in ds.iterrows():
        similar_indices = cosine_similarities[idx].argsort()[:-100:-1]
        similar_items = [(cosine_similarities[idx][i], ds['data__data__id'][i]) for i in similar_indices]
        results[row['data__data__id']] = similar_items[1:]

    cash_tour = []
    recommendation_tour = []
    for id in my_activiti_id:
        cash, recommendation = recommend(item_id=id, num=10,results=results,ds=ds,user_budget=user_budget)
        cash_tour.append(cash)
        recommendation_tour.append(recommendation)

    response = {'cash_tour': cash_tour, 'recommendation_tour': recommendation_tour}
    return response
