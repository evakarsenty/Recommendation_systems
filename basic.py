# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16QMUUaSHzx4CTF8qAEqWd3jkhNfFAtqo

F1:
"""

import numpy as np
import pandas as pd
import scipy
import scipy.sparse
import sklearn
from sklearn.preprocessing import OneHotEncoder

np.random.seed(0)

users_doc = pd.read_csv("user_song.csv")
test_doc = pd.read_csv("test.csv")
users_doc2 = pd.read_csv("user_song.csv")
test_doc2 = pd.read_csv("test.csv")

nb_users = users_doc["user_id"].nunique()
nb_songs = users_doc["song_id"].nunique()
dimensions = nb_users*nb_songs

r_avg = users_doc['weight'].mean()
#print(r_avg)

users_id_dict ={}
songs_id_dict={}
count = 0
counter = 0
id_unique = users_doc['user_id'].unique()
id_unique_song = users_doc['song_id'].unique()

for id in id_unique:
  users_id_dict[id] =  count
  count+=1

for song in id_unique_song:
  songs_id_dict[song] = counter
  counter +=1

train_users_songs = users_doc.iloc[:, 0:2]

encoder = OneHotEncoder(sparse_output=False, dtype=int)
encoded_data = encoder.fit_transform(train_users_songs)
A = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(['user_id', 'song_id']))
sparse_A = scipy.sparse.csr_matrix(A.values)

c = users_doc['weight'] - r_avg
b_vector = scipy.sparse.linalg.lsqr(A=sparse_A, b=c)
b_vector = b_vector[0]

user_id_dict = {}
song_id_dict = {}

index = 0
for column in A.columns:
  user_song = column.split("_")[0]
  id = column.split("_")[2]
  if user_song == "user":
      user_id_dict[id] = b_vector[index]
  else:
      song_id_dict[id] = b_vector[index]
  index += 1

users_predictions = []

for index, row in users_doc2.iterrows():
    user_id = str(row['user_id'])
    song_id = str(row['song_id'])
    bu = user_id_dict[user_id]
    bi = song_id_dict[song_id]
    users_predictions.append(r_avg + bu + bi)

users_doc2['predictions_zero'] = users_predictions
weight_np = users_doc2['weight'].to_numpy()
pred_np = users_doc2['predictions_zero'].to_numpy()
diff_withZero = (weight_np - pred_np)
score_diff_withZero = diff_withZero ** 2
f1 = np.sum(score_diff_withZero)
#print("Value of f1 function:", f1)

test_predictions = []
for index, row in test_doc2.iterrows():
        user_id = str(row['user_id'])
        song_id = str(row['song_id'])
        bu = user_id_dict[user_id]
        bi = song_id_dict[song_id]
        test_predictions.append(r_avg + bu + bi)

test_doc2['weight'] = test_predictions
resultdf= test_doc2[['user_id', 'song_id', 'weight']]
resultdf.to_csv('task1.csv', index=False)

"""F2:"""

users_id_dict ={}
songs_id_dict={}
count = 0
counter = 0
for id in id_unique:
  users_id_dict[id] =  count
  count+=1

for song in id_unique_song:
  songs_id_dict[song] = counter
  counter +=1

cols = nb_users
rows= nb_songs
R = np.zeros((rows, cols))

for row in users_doc.index:
    R[songs_id_dict.get(users_doc.loc[row]["song_id"])][users_id_dict.get(users_doc.loc[row]["user_id"])] = users_doc.loc[row]["weight"]

cols = nb_users
rows= nb_songs
R2 = np.zeros((cols, rows))

for row in users_doc.index:
    R2[users_id_dict.get(users_doc.loc[row]["user_id"])][songs_id_dict.get(users_doc.loc[row]["song_id"])] = users_doc.loc[row]["weight"]

def ALS(matrix, num_factors, max_iterations):

    num_users, num_songs = matrix.shape
    P = np.random.rand(num_users, num_factors)
    Q = np.zeros((num_songs, num_factors))

    for _ in range(max_iterations):
        #print(_)
        for song_idx in range(num_songs):
            users = np.where(matrix[:, song_idx] > 0)[0]
            if len(users) > 0:
                U = P[users, :]
                R = matrix[users, song_idx]
                # Update Q using arg min of norm(U*Q.T - R)
                Q[song_idx, :] = np.linalg.lstsq(U, R, rcond=None)[0]

        for user_idx in range(num_users):
            songs = np.where(matrix[user_idx, :] > 0)[0]
            if len(songs) > 0:
                U = Q[songs, :]
                R = matrix[user_idx, songs]
                # Update P using arg min of norm(U*P.T - R)
                P[user_idx, :] = np.linalg.lstsq(U, R, rcond=None)[0]

    return P, Q

num_factors = 20
max_iterations = 1000

P, Q = ALS(R2, num_factors, max_iterations)

f2=0

for row in users_doc.index:
    r_u_i = users_doc.loc[row]["weight"]
    f2 += (r_u_i - np.dot((P[(users_id_dict.get(users_doc.loc[row]["user_id"])),:]).T , Q[songs_id_dict.get(users_doc.loc[row]["song_id"]),:]))**2
#print("Value of f2 function:", f2)

values = []

for row in test_doc.index:
  value = np.dot((P[(users_id_dict.get(test_doc.loc[row]["user_id"])),:]).T , Q[songs_id_dict.get(test_doc.loc[row]["song_id"]),:])
  values.append((test_doc.loc[row]["user_id"],test_doc.loc[row]["song_id"],value))

result_df = pd.DataFrame(values, columns=['user_id', 'song_id', 'weight'])

result_df.to_csv('task2.csv', index=False)

"""F3:"""

U, S, Vt = np.linalg.svd(R)

K=20
U_approx = U[:, :20]
S_approx = np.diag(S[:20])
Vt_approx = Vt[:20, :]

R_approx = U_approx @ S_approx @ Vt_approx

mask = R != 0
f3 = np.sum(np.square((R - R_approx) * mask))
#print("Value of f3 function:", f3)

pairs = [(row.user_id, row.song_id) for row in test_doc.itertuples()]

values = []

for row in test_doc.index:
    value=R_approx[(songs_id_dict.get(test_doc.loc[row]["song_id"]))][(users_id_dict.get(test_doc.loc[row]["user_id"]))]
    values.append((test_doc.loc[row]["user_id"],test_doc.loc[row]["song_id"],value))


result_df = pd.DataFrame(values, columns=['user_id', 'song_id', 'weight'])

result_df.to_csv('task3.csv', index=False)
