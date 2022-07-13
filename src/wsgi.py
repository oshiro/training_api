from flask import Flask
from flask_restful import Api
from iris_classifier import iris_classifier
from data_models.db import db

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/predictions.db'
db.init_app(app)

api.add_resource(iris_classifier.ModelTrainer, '/train_model/<string:model_id>')
api.add_resource(iris_classifier.Classifier, '/predict')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)