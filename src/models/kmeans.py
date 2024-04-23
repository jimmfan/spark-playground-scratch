import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Sample data
data = {'store_id': [1, 2, 3, 4, 5],
        'employee_turnover_rate': [0.1, 0.3, 0.2, 0.4, 0.15],
        'incident_rate': [0.05, 0.1, 0.05, 0.15, 0.02],
        'compliance_score': [0.95, 0.80, 0.90, 0.70, 0.93]}

df = pd.DataFrame(data)

# Normalize data
df_normalized = (df[['employee_turnover_rate', 'incident_rate', 'compliance_score']] - df[['employee_turnover_rate', 'incident_rate', 'compliance_score']].mean()) / df[['employee_turnover_rate', 'incident_rate', 'compliance_score']].std()

# Clustering
kmeans = KMeans(n_clusters=3, random_state=0).fit(df_normalized)
df['cluster'] = kmeans.labels_

# Plotting
plt.scatter(df['employee_turnover_rate'], df['incident_rate'], c=df['cluster'])
plt.xlabel('Employee Turnover Rate')
plt.ylabel('Incident Rate')
plt.title('Store Risk Profiles')
plt.show()
