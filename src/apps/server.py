from flask import Flask, jsonify, request
from uuid import uuid4

from src.apps.blockchain import Blockchain

app = Flask(__name__)

node_identifier = str(uuid4()).replace("-", "")

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine(previous=None):
    # Запускаем алгоритм и получаем подтверждение работы
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Мы должны получить вознаграждение за найденное подтверждение
    # Отправитель "0" означает, что узел заработал крипто монету
    blockchain.create_transaction('0', node_identifier, 1)

    # Создаем новый блок и вносим его в цепь
    previous_hash = blockchain.hash(last_block)
    new_block = blockchain.create_block(proof, previous_block_hash=previous_hash)
    # Возвращаем результат
    return jsonify({
        'message': 'New Block has been created and added',
        'index': new_block['index'],
        'transactions': new_block['transactions'],
        'proof': new_block['proof'],
        'previous_hash': new_block['previous_hash']
    }), 200


@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    values = request.get_json()

    # Проверка присутствия всех необходимых значений
    for required in ('sender', 'recipient', 'amount'):
        if not required in values:
            return 'Неправильный формат Data', 400

    # Создание новой транзакции
    index = blockchain.create_transaction(values['sender'], values['recipient'], values['amount'])

    # Возвращаем результат
    return jsonify({'massage': f'Транзакция успешно выполнена, в блоке {index}'}), 201


@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }), 200


app.run(host='0.0.0.0', port=5000)


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    # Проверка корректности данных
    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400

    # Добавляем каждый узел в список
    for node in nodes:
        blockchain.register_node(node)

    # Возвращаем ответ
    return jsonify({
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replased = blockchain.resolve_conflicts()
    if replased:
        response = {
            'message': 'Our chain was replased',
            'new_chain': blockchain.chain
        }

        return jsonify(response), 200
