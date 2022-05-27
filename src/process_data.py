import pandas as pd


def process_data(raw_data_path, final_data_path):
    data = pd.read_csv(raw_data_path)
    data['churn'] = data['churn'].map({0: 'No', 1: 'Yes'})
    data.to_csv(final_data_path, index=False)
