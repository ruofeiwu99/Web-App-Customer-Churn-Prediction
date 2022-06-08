import logging

from typing import List, Tuple, Union
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

# pylint: disable=locally-disabled, invalid-name

logger = logging.getLogger('modeling')


def select_features(data: pd.DataFrame, features: List[str]) -> Union[None, pd.DataFrame]:
    """
    Select features from the dataframe
    Args:
        data (obj: pd.DataFrame): dataframe
        features (List[str]): features to be selected

    Returns:
        data (obj: pd.DataFrame): selected dataframe
    """
    if features is None or len(features) == 0:
        return pd.DataFrame()

    valid_features = []

    for feature in features:
        if feature in data.columns:
            valid_features.append(feature)

    if len(valid_features) == 0:
        return pd.DataFrame()

    logger.info('Features for model training are selected: %s', valid_features)
    return data[valid_features]


def select_target(data: pd.DataFrame, target: str) -> Union[None, pd.DataFrame]:
    """
    Select target column from the dataframe
    Args:
        data (obj: pd.DataFrame): dataframe
        target (str): target column name

    Returns:
        target (Union[None, pd.DataFrame]): target column; None if target column is not found in the dataframe
    """
    # select target
    if target is None:
        logger.error('Error: target column is None.')
        return None

    if target in data.columns:
        logger.info('Target column for model training selected.')
        return data[target]

    logger.error('Error: target column not found in the dataset.')
    raise KeyError(f'{target} is not in the input dataframe.')


def train_model(data: pd.DataFrame, used_features: List[str], target: str, test_size: float,
                random_state: int) -> Tuple:
    """
    Perform train test split, train the random forest model on training data, and save train data, test data as well
    as trained model object
    Args:
        data (obj: pd.DataFrame): processed dataframe
        used_features (List[str]): features used in the random forest model
        target (str): target column name
        test_size (float): proportion of test data
        random_state (int): random seed for train test split and random forest model

    Returns:
        rf (obj: RandomForestClassifier): trained random forest model object
        X_train (obj: pd.DataFrame): train features
        X_test (obj: pd.DataFrame): test features
        y_train (obj: pd.DataFrame): train target
        y_test (obj: pd.DataFrame): test target
    """
    X = select_features(data, used_features)
    X = pd.get_dummies(data=X, drop_first=True)
    y = select_target(data, target)

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
    logger.info('Random forest model saved.')


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
    """
    Make predictions on a single input record
    Args:
        rf_model (obj: RandomForestClassifier): random forest model object
        columns (List[str]): list of columns to be used in the prediction
        record_df (obj: pd.DataFrame): input record

    Returns:
        pred (int): prediction if a customer is likely to churn 1: Yes, 0: No
    """
    record_df = record_df[columns]
    transformed_record = pd.get_dummies(record_df)
    pred_class = rf_model.predict(transformed_record)[0]
    return pred_class


def make_predictions(rf_model: RandomForestClassifier, X_test: pd.DataFrame) -> pd.DataFrame:
    """
    Make predictions on test set
    Args:
        rf_model (obj: RandomForestClassifier): random forest model object
        X_test (obj: pd.DataFrame): test features

    Returns:
        pred (obj: pd.DataFrame): dataframe containing predicted churn labels
    """
    # make predictions
    ypred_test = rf_model.predict(X_test)
    pred_df = pd.DataFrame({'pred_class': ypred_test})
    return pred_df


def eval_performance(pred_res: pd.DataFrame, y_test: pd.DataFrame) -> Tuple:
    """
    Evaluate performance of the model by computing accuracy, confusion matrix, and classification report
    Args:
        pred_res (obj: pd.DataFrame): dataframe containing predicted churn labels
        y_test (obj: pd.DataFrame): dataframe containing test target

    Returns:
        accuracy (float): accuracy of the model
        confusion_matrix (obj: pd.DataFrame): confusion matrix
        classification_report (str): classification report
    """
    ypred_test = pred_res['pred_class']

    # compute model performance metrics
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
    with open(model_eval_path, 'w', encoding='utf8') as f:
        f.write(f'Accuracy on test: {accuracy}\n')
        f.write('-------------------Classification Report--------------------\n')
        f.write(class_report)
        f.write('-------------------Confusion Matrix--------------------\n')
        f.write(conf_mat.to_string())
