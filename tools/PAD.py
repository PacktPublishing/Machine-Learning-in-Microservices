import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM

"""
Load Data

Here we want to look at only the response time and detect anomalies within the MSA
You can include more features to better determine anomalies
"""
payment_ms_stats_df = pd.read_csv('scrubbed_stats/payment_ms_stats.csv')

model_data = np.array(payment_ms_stats_df['response_time']).reshape(-1,1)


"""
Initialize anamoly model (Here we use a One Class SVM)
"""

# Documentation on OneClassSVM API https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html
model = OneClassSVM(gamma = 'scale', nu = 0.1).fit(model_data)

"""
Predict anomalies from the dataset 
1 indicates normal while -1 indicates an anomaly
"""
y_pred = model.predict(model_data)

"""
Here we can extract the indices of the anomalies within our model prediction and futher examine the data to see
how it compares with the other response times
"""
anomaly_ind = np.where(y_pred == -1) 
anomalies = payment_ms_stats_df.iloc[anomaly_ind]

df = payment_ms_stats_df.assign(Anomaly = y_pred == -1)
df.to_csv("predicted_payment_ms_rt_anomalies.csv", mode = 'w', index=False)

