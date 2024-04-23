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
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(principal_df['principal_component_1'],
                     principal_df['principal_component_2'],
                     principal_df['principal_component_3'],
                     c=principal_df['cluster'], cmap='viridis')

# Labeling
ax.set_xlabel('Principal Component 1')
ax.set_ylabel('Principal Component 2')
ax.set_zlabel('Principal Component 3')
ax.set_title('3D PCA Plot')

# Legend
legend1 = ax.legend(*scatter.legend_elements(),
                    loc="upper right", title="Clusters")
ax.add_artist(legend1)

plt.show()
