import resource
from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from flask_restful import Resource, reqparse, fields, marshal
from data_models.classification_data_model import ClassificationData
from data_models.db import db
import logging
import numpy as np
import joblib
import os

logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s - %(message)s', datefmt='%Y-%m-%d|%H:%M:%S')
logger = logging.getLogger('iris_classifier')
logger.setLevel(logging.INFO)

class ModelTrainer(Resource):
    def get_training_dataset(self) -> tuple[np.ndarray, np.ndarray]:
        '''
        Gets the training dataset for the iris classification problem.

        Currently retrieving the data from sklearn module.

        ### Returns
        - X: array where each element is a representation of the features of
        a training example.
        - y: array where each element is the target value for the corresponding
        element in X.
        '''
        X, y = datasets.load_iris(return_X_y=True)
        logger.info('Iris dataset retrieved from sklearn')
        return X, y

    def get(self, model_id: str):
        '''
        Train a Decision Tree Classifier for the iris classification problem.
        The trained model is serialized using joblib to the models directory
        with the model_id as part of the filename.

        ### Parameters
        - model_id: str with the model id.
        '''
        model = DecisionTreeClassifier()
        X, y = self.get_training_dataset()
        model.fit(X,y)
        logger.info('Decicions Tree Classifier trained')
        model_location = f'models/{model_id}.joblib'
        logger.info(f'Model saved in {model_location}')
        joblib.dump(model, model_location)

class Classifier(Resource):
    def get_class_name(self, class_id: int) -> str:
        '''
        Gets the class name given the class id.

        ### Parameters
        - class_id: int representing the class id.

        ### Returns:
        - str corresponding to the class name.
        '''

        classes = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}
        return classes[class_id]

    def post(self) -> dict:
        '''
        Prediction of the classification using model named `model_id`. The serialized model
        must exist in the models directory.

        ### Parameters
        - features: dict containing the features values of the element to be classified.
        - model_id: str with model id.

        ### Returns
        - result: int value indicating the class predicted for x
        '''
        args_parser = reqparse.RequestParser()
        args_parser.add_argument('model_id', type=str, help='Classification model id (required)', required=True)
        args_parser.add_argument('sepal_length', type=float, help='Sepal length (required)', required=True)
        args_parser.add_argument('sepal_width', type=float, help='Sepal width (required)', required=True)
        args_parser.add_argument('petal_length', type=float, help='Petal length (required)', required=True)
        args_parser.add_argument('petal_width', type=float, help='Petal width (required)', required=True)
        args = args_parser.parse_args()

        resource_fields = {
            'model_id': fields.String,
            'sepal_length': fields.Float,
            'sepal_width': fields.Float,
            'petal_length': fields.Float,
            'petal_width': fields.Float,
            'predicted_class_id': fields.Integer,
            'predicted_class': fields.String
        }

        result = ClassificationData.query.filter_by(model_id=args['model_id'],
                                                         sepal_length=args['sepal_length'],
                                                         sepal_width=args['sepal_width'],
                                                         petal_length=args['petal_length'],
                                                         petal_width=args['petal_width']).first()
        if result:
            logger.info('Result retrieved from database')
            return marshal(result, resource_fields)

        model_location = f'models/{args["model_id"]}.joblib'
        if not os.path.exists(model_location):
            logger.error('Model file not found')
            return 'Model file not found, call train_classifier with the corresponding model_id first.', 404
        
        model = joblib.load(model_location)
        logger.info(f'Model {args["model_id"]} loaded')
        logger.info(f'Executing new prediction')
        x = [ args[feature] for feature in ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'] ]
        class_id = int(model.predict([x])[0])
        result = ClassificationData(model_id=args['model_id'],
                                         sepal_length=args['sepal_length'],
                                         sepal_width=args['sepal_width'],
                                         petal_length=args['petal_length'],
                                         petal_width=args['petal_width'],
                                         predicted_class_id=class_id,
                                         predicted_class=self.get_class_name(class_id))
        db.session.add(result)
        db.session.commit()
        logger.info('Prediction saved to database')
        return marshal(result, resource_fields)
