import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import csv

# Inicialização da aplicação Flask
app = Flask(_name_)
CORS(app, resources={r"/api/": {"origins": ""}})

# Variável para armazenar feedbacks do CSV
linhas = []
feedback_classificacoes = []  # Armazena as respostas da API de classificação

# Leitura do arquivo CSV ao iniciar a aplicação
with open('C:/Users/Henrique Vieira/Desktop/hackthon/feedbacks_hospitais_curto.csv', mode='r', newline='') as file:
    reader = csv.reader(file)
    next(reader)  # Pula o cabeçalho
    for row in reader:
        linhas.append(row)

# Armazena URLs para requisições GET
search = []
#print("Todas as linhas (exceto o título):")
#for linha in linhas:
#    print(linha)


# Endpoint POST para receber URLs
@app.route('/api/', methods=['POST'])
def post_request():
    data = request.get_json()
    search.append(data.get("site"))
    return jsonify({"Request": "Success!!!"}), 201


# Endpoint GET para realizar requisição com a primeira URL recebida
@app.route('/api/', methods=['GET'])
def get_request():
    if not search:
        return jsonify({"Request": "Bad Request!!!"}), 400
    data = requests.get(search[0])
    cep_data = data.json()
    return jsonify(cep_data), 200


# Endpoint para fornecer feedbacks do CSV
@app.route('/feedback', methods=['GET'])
def get_feedback():
    return jsonify({"feedbacks": linhas}), 200


# Endpoint para fazer a chamada curl à API externa com um feedback de exemplo
@app.route('/classify-feedback', methods=['POST'])
def classify_feedback():
    # Escolhe o primeiro feedback da lista para enviar
    if not linhas:
        return jsonify({"error": "No feedbacks available"}), 400

    # Extrai o texto do feedback (supondo que o texto está na primeira coluna)
    example_feedback = linhas[0][0]

    # Configura o payload da requisição
    prediction_payload = {
        "question": example_feedback,
        "overrideConfig": {
            "analytics": {
                "langFuse": {
                    "userId": "nome_to_time"
                }
            }
        }
    }

    # Requisição à API externa
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer uF6TJLlcl8e5_pQ-bHZQ8f1XBEjsTO5UJops_cHtWBc"
    }
    response = requests.post(
        "https://agent.lmuss.io/api/v1/prediction/5703ed2a-3057-46ec-9619-76c71ea8b2e7",
        json=prediction_payload,
        headers=headers
    )

    # Armazena e retorna a resposta da API externa
    if response.status_code == 200:
        classification = response.json()

        # Extraindo apenas a classificação "3 2 0"
        classification_value = classification.get("agentReasoning", [{}])[1].get("messages", [""])[0]

        feedback_classificacoes.append(classification_value)  # Armazena a resposta
        return jsonify({"classification": classification_value}), 200
    else:
        return jsonify({"error": "Failed to get response from external API"}), response.status_code


# Endpoint para ver todas as classificações armazenadas
@app.route('/classifications', methods=['GET'])
def get_classifications():
    return jsonify({"classifications": feedback_classificacoes}), 200


# Inicializa o servidor Flask
if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000)