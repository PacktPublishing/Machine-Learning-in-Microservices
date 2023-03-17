import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


"""
Read in data

Response time is our target label to predict. We will extract the column to use as our Y

With the remaining data we will use it as our features or X. From there we can split the data into training and
testing dataset with 80% for training and 20% for testing
"""
payment_ms_stats_df = pd.read_csv('scrubbed_stats/payment_ms_stats.csv')
payment_ms_rt = np.array(payment_ms_stats_df['response_time']).reshape(-1,1)

model_data = payment_ms_stats_df.drop('response_time', axis = 1)
model_data = np.array(model_data)

model_data_train, model_data_test, payment_ms_rt_train, payment_ms_rt_test = train_test_split(model_data, payment_ms_rt, test_size = 0.20, shuffle=True)


"""
We will initialize our Linear Regression Model, train the model with our data, predict our response time

Using the predicted results we can initialize thresolds for our program to detect any irregularities within our MSA 
"""
# Documentation on Linear Regression API https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
lr_model = LinearRegression()
lr_model.fit(model_data_train, payment_ms_rt_train)
trend_payment_ms_rt_predictions = lr_model.predict(model_data_test)

df = pd.DataFrame()
df["predicted_payment_ms_rt"] = trend_payment_ms_rt_predictions[:,-1]
df.to_csv("predicted_payment_ms_rt_trend.csv", mode = 'w', index=False)

