import logging

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix, accuracy_score, classification_report
import pickle

logger = logging.getLogger(__name__)


def train_model(data_path, model_path, X_test_path, y_test_path, used_features, test_size, random_state):
    data = pd.read_csv(data_path)
    X = data[used_features]
    X = pd.get_dummies(data=X, drop_first=True)
    y = data['churn']

    # train test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state)
    rf = RandomForestClassifier(class_weight='balanced', random_state=random_state)
    rf.fit(X_train, y_train)

    # save test set
    X_test.to_csv(X_test_path, index=False)
    y_test.to_csv(y_test_path, index=False)

    # save model
    with open(model_path, 'wb') as f:
        pickle.dump(rf, f)


def pred_one_record(model_path, columns, record_df):
    with open(model_path, 'rb') as f:
        rf_model = pickle.load(f)
    record_df = record_df[columns]
    transformed_record = pd.get_dummies(record_df)
    pred_class = rf_model.predict(transformed_record)[0]
    return pred_class


def make_predictions(model_path, X_test_path, y_test_path, pred_res_path):
    # produce predictions for evaluating the model and save them to the appropriate directory
    # load random forest model
    with open(model_path, 'rb') as f:
        rf_model = pickle.load(f)

    X_test = pd.read_csv(X_test_path)
    y_test = pd.read_csv(y_test_path)['churn']
    # make predictions

    ypred_test = rf_model.predict(X_test)
    pred_res = pd.DataFrame({'pred_class': ypred_test, 'true_class': y_test})
    # save prediction results
    pred_res.to_csv(pred_res_path, index=False)


def eval_performance(pred_res_path, performance_path):
    # compute performance metrics and save
    pred_res = pd.read_csv(pred_res_path)
    y_test = pred_res['true_class']

    ypred_test = pred_res['pred_class']

    confusion = confusion_matrix(y_test, ypred_test)
    accuracy = accuracy_score(y_test, ypred_test)
    pred_report = classification_report(y_test, ypred_test)
    conf_mat = pd.DataFrame(confusion,
                            index=['Actual negative', 'Actual positive'],
                            columns=['Predicted negative', 'Predicted positive'])

    with open(performance_path, 'w') as f:
        f.write('Accuracy on test: %0.3f \n' % accuracy)
        f.write('-------------------Classification Report--------------------\n')
        f.write(pred_report)
        f.write('-------------------Confusion Matrix--------------------\n')
        f.write(conf_mat.to_string())
