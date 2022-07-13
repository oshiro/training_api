from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from flask_restful import Resource, reqparse, fields, marshal_with
from data_models.classification_data_model import ClassificationData
from data_models.db import db
import numpy as np
import joblib
import os

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
        model_location = f'models/{model_id}.joblib'
        joblib.dump(model, model_location)

class Classifier(Resource):
    resource_fields = {
        'model_id': fields.String,
        'sepal_length': fields.Float,
        'sepal_width': fields.Float,
        'petal_length': fields.Float,
        'petal_width': fields.Float,
        'predicted_class_id': fields.Integer,
        'predicted_class': fields.String
    }

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

    @marshal_with(resource_fields)
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

        result = ClassificationData.query.filter_by(model_id=args['model_id'],
                                                         sepal_length=args['sepal_length'],
                                                         sepal_width=args['sepal_width'],
                                                         petal_length=args['petal_length'],
                                                         petal_width=args['petal_width']).first()
        if result:
            print('Retrieved result')
            return result

        print('New prediction')
        model_location = f'models/{args["model_id"]}.joblib'
        if not os.path.exists(model_location):
            raise Exception('Model file not found, call "train_classifier" with the corresponding model_id first.')
        
        model = joblib.load(model_location)
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
        return result
