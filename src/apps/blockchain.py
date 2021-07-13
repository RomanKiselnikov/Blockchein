from time import time
import hashlib
import json
from urllib.parse import urlparse


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        # Создание блока генезиса
        self.create_block(proof=100, previous_block_hash=1)

    def create_block(self, proof, previous_block_hash=None):
        # Создание нового блока
        new_block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_block_hash or self.hash(self.chain[-1])
        }

        # Перезагрузка текущего списка транзакций
        self.current_transactions = []

        # Добавление блока
        self.chain.append(new_block)
        return new_block

    def create_transaction(self, sender, recipent, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipent': recipent,
            'amount': amount
        })

        return self.last_block['index']

    @staticmethod
    def hash(block):
        # Создание хэша SHA-256 блока
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    def register_node(self, address):
        # Вносим новый узел в список узлов
        pasred_url = urlparse(address)
        self.nodes.add(pasred_url.netloc)

    def valid_chain(self, chain, proof=None):
        # Проверяем, является ли внесенный в блок хеш корректным
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Проверка правильности хэша
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Проверка подтверждения работы
            if not self.valid_proof(last_block[proof], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self, requests=None):
        # Это алгоритм консенсуса, он разрешает конфликты, саменяя нашу цепь на самую длинную в цепи
        neighbours = self.nodes
        new_chain = None

        # Ищем только цепи, длиннее нашей
        max_lenght = len(self.chain)

        # Захватываем и проверяем все цепи из всех узлов цепи
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                lenght = response.json()['lenght']
                chain = response.json()['chain']

                # Проверяем, является ли эта длина самой длинной, а цепь валидной
                if lenght > max_lenght and self.valid_chain(chain):
                    max_lenght = lenght
                    new_chain = chain

        # Заменяем нашу цепь, если найдем более валидную или более длинную
        if new_chain:
            self.chain = new_chain
            return True

        return False
