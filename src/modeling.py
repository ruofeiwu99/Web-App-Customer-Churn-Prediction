import logging.config

from typing import List, Tuple
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

# pylint: disable=locally-disabled, invalid-name

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('modeling')


def train_model(data: pd.DataFrame, used_features: List[str], test_size: float, random_state: int) -> Tuple:
    """
    Perform train test split, train the random forest model on training data, and save train data, test data as well
    as trained model object
    Args:
        data (obj: pd.DataFrame): processed dataframe
        used_features (List[str]): features used in the random forest model
        test_size (float): proportion of test data
        random_state (int): random seed for train test split and random forest model

    Returns:
        rf (obj: RandomForestClassifier): trained random forest model object
        X_train (obj: pd.DataFrame): train features
        X_test (obj: pd.DataFrame): test features
        y_train (obj: pd.DataFrame): train target
        y_test (obj: pd.DataFrame): test target
    """
    X = data[used_features]
    X = pd.get_dummies(data=X, drop_first=True)
    y = data['churn']

    # train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # use random forest classifier model
    rf = RandomForestClassifier(class_weight='balanced', random_state=random_state)

    # fit model to train data
    rf.fit(X_train, y_train)

    return rf, X_train, X_test, y_train, y_test


def save_model(model_obj: RandomForestClassifier, model_path: str) -> None:
    """
    Saves the model to the specified path
    Args:
        model_obj (obj: sklearn.ensemble.RandomForestClassifier): trained random forest model object
        model_path (str): path to save the trained model object

    Returns:
        None
    """
    # save model
    with open(model_path, 'wb') as f:
        pickle.dump(model_obj, f)
    logger.info("Random forest model saved.")


def save_train_test(X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.DataFrame, y_test: pd.DataFrame,
                    X_train_path: str, X_test_path: str, y_train_path: str, y_test_path: str) -> None:
    """
    Save train and test data to the specified path
    Args:
        X_train (obj: pd.DataFrame): train features
        X_test (obj: pd.DataFrame): test features
        y_train (obj: pd.DataFrame): train target
        y_test (obj: pd.DataFrame): test target
        X_train_path (str): specify the path to save train features
        X_test_path (str): specify the path to save test features
        y_train_path (str): specify the path to save train target
        y_test_path (str): specify the path to save test target

    Returns:
        None
    """
    X_train.to_csv(X_train_path, index=False)
    X_test.to_csv(X_test_path, index=False)
    y_train.to_csv(y_train_path, index=False)
    y_test.to_csv(y_test_path, index=False)


def pred_one_record(rf_model: RandomForestClassifier, columns: List[str], record_df: pd.DataFrame) -> int:
    record_df = record_df[columns]
    transformed_record = pd.get_dummies(record_df)
    pred_class = rf_model.predict(transformed_record)[0]
    return pred_class


def make_predictions(rf_model: RandomForestClassifier, X_test: pd.DataFrame) -> pd.DataFrame:
    # make predictions
    ypred_test = rf_model.predict(X_test)
    pred_df = pd.DataFrame({'pred_class': ypred_test})
    return pred_df


def eval_performance(pred_res: pd.DataFrame, y_test: pd.DataFrame) -> Tuple:
    # compute performance metrics and save
    ypred_test = pred_res['pred_class']

    confusion = confusion_matrix(y_test, ypred_test)
    accuracy = accuracy_score(y_test, ypred_test)
    class_report = classification_report(y_test, ypred_test)
    conf_mat = pd.DataFrame(confusion,
                            index=['Actual negative', 'Actual positive'],
                            columns=['Predicted negative', 'Predicted positive'])

    return accuracy, class_report, conf_mat


def save_model_eval(accuracy: float, class_report: str, conf_mat: pd.DataFrame, model_eval_path: str) -> None:
    """
    Save model performance metrics to specified path
    Args:
        accuracy  (float): accuracy score
        class_report (str): text summary of the precision, recall, F1 score for each class
        conf_mat (obj: pd.DataFrame): Confusion matrix
        model_eval_path (str): path to save model evaluation metrics

    Returns:
        None
    """
    with open(model_eval_path, 'w') as f:
        f.write('Accuracy on test: %0.3f \n' % accuracy)
        f.write('-------------------Classification Report--------------------\n')
        f.write(class_report)
        f.write('-------------------Confusion Matrix--------------------\n')
        f.write(conf_mat.to_string())
