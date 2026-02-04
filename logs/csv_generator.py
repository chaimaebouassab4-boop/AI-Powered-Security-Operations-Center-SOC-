import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()

def generate_synthetic_logs(n=300, anomaly_ratio=0.1):
    data = []
    for _ in range(n):
        is_anomaly = np.random.rand() < anomaly_ratio
        event = {
            'timestamp': fake.date_time_this_year().isoformat(),
            'source': 'ssh' if is_anomaly else fake.random_element(['apache', 'syslog', 'auth']),
            'event_type': 'brute_force' if is_anomaly else 'login',
            'details': {'message': 'Failed password for invalid user' if is_anomaly else 'Accepted password'},
            'ip': fake.ipv4(),
            'label': 1 if is_anomaly else 0
        }
        data.append(event)
    df = pd.DataFrame(data)
    df.to_csv('labeled_dataset.csv', index=False)
    return df

# Run: generate_synthetic_logs(500)
if __name__ == "__main__":
    generate_synthetic_logs(500)
