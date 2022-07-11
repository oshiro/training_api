from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import logging
import joblib
import os

logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s - %(message)s', datefmt='%Y-%m-%d|%H:%M:%S')
logger = logging.getLogger('iris_classifier')
logger.setLevel(logging.INFO)

def get_training_dataset() -> tuple[np.ndarray, np.ndarray]:
    '''
    Gets the training dataset for the iris classification problem.

    Currently retrieving the data from sklearn module.

    ### Returns
    - X: array where each element is a representation of the features of
    a training example.
    - y: array where each element is the target value for the corresponding
    element in X.
    '''
    logger.info('Getting iris dataset from sklearn datasets')
    X, y = datasets.load_iris(return_X_y=True)
    return X, y

def train_classifier(X: np.ndarray, y: np.ndarray, model_id: str):
    '''
    Train a Decision Tree Classifier for the iris classification problem.
    The trained model is serialized using joblib to the models directory
    with the model_id as part of the filename.

    ### Parameters
    - X: array where each element is a representation of the features of
    a training example.
    - y: array where each element is the target value for the corresponding
    element in X.
    - model_id: str with the model id.
    '''
    logger.info('Training a Decision Tree Classifier')
    model = DecisionTreeClassifier()
    model.fit(X,y)
    model_location = f'../models/{model_id}.joblib'
    joblib.dump(model, model_location)
    logger.info(f'Model saved as {model_location}')

def predict(x: np.ndarray, model_id: str) -> int:
    '''
    Prediction of the classification using model named `model_id`. The serialized model
    must exist in the models directory.

    ### Parameters
    - x: array representing the features of the element to be classified.
    - model_id: str with model id.

    ### Returns
    - result: int value indicating the class predicted for x
    '''
    model_location = f'../models/{model_id}.joblib'
    if not os.path.exists(model_location):
        raise Exception('Model file not found, call "train_classifier" with the corresponding model_id first.')

    model = joblib.load(model_location)
    logger.info(f'Model loaded from {model_location}')
    # features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    result = model.predict([x])[0]
    logger.info(f'Predicted {result} for x = {x}')
    return result
