# training_api

API para executar o treinamento de um classificador iris e as classificações.

## Instalação e execução

Para executar a API neste repositório basta ter o docker instalado na máquina.

Depois de clonar o repositório e entrar em sua raiz, construa o container docker executando:

```bash
$ docker build -t training_api .
```

Para iniciar o container execute:

```bash
$ docker run -d --name iris_api -p 8080:8080 training_api
```

## Endpoints

A API possui 2 endpoints, um para treinar um novo modelo e outro para executar uma classificação, 
gravando em uma base de dados Sqlite.

### Treino
- endpoint: localhost:8080/train_model/\<string:model_id>
- método: GET

Exemplo:
```bash
$ curl localhost:8080/train_model/model_v2 -X GET
```

Os modelos são salvos no diretório de modelos "./models" no formato joblib.



### Classificação
- endpoint: localhost:8080/predict
- método: POST 
- payload: {"model_id": \<string>, "sepal_length": \<float>, "sepal_width": \<float>, "petal_length": \<float>, "petal_width": \<float>}
- resultado: {"model_id": \<string>, "sepal_length": \<float>, "sepal_width": \<float>, "petal_length": \<float>, "petal_width": \<float>, "predicted_class_id": \<integer>, "predicted_class": \<string>}

Exemplo:
```bash
$ curl localhost:8080/predict -X POST -d '{"model_id": "model_v1", "sepal_length": 4.0, "sepal_width": 4, "petal_length": 4, "petal_width": 4}' -H "Content-Type: application/json"
{"model_id": "model_v1", "sepal_length": 4.0, "sepal_width": 4.0, "petal_length": 4.0, "petal_width": 4.0, "predicted_class_id": 1, "predicted_class": "versicolor"}
```

Caso uma classificação com os mesmos parâmetros tenha sido feita anteriormente, o resultado é recuperado da base de dados e retornado. Caso contrário é feita a classificação
através do modelo.

## Considerações

- os modelos estão sendo persistidos dentro do container, o ideal seria em um local externo, como por exemplo na nuvem (AWS S3, GCP GCS, ...);
- a base de dados também está sendo persistida dentro do container, o ideal seria ter uma base externa;
- por simplicidade usei o Sqlite como banco de dados, mas para uma API em produção necessitando de baixa latência um banco NoSQL, como MongoDB talvez seja mais adequado;
- configuração da base de dados está incompleta, para segurança seria preciso definir usuários e senhas e implementar alguma proteção de segredos para não expor as senhas;
- por falta de tempo não criei teste unitários.
