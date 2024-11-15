import logging
import os
import csv
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, reqparse, Namespace, fields
from elegoo_module import ElegooSaturn3Ultra

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app, version='1.0', title='3D Printers API', description='3D Printers API (Just Elegoo resin implementation yet) - Gabriel Bolzani')

CSV_FILE_PATH = 'printers.csv'

# Definindo namespaces
general_operations = Namespace('General Operations', description='Operações em Geral')
elegoo_printer_operations = Namespace('Elegoo printer operations', description='Operações com maquinas Elegoo')
creality_printer_operations = Namespace('creality_printer_operations', description='Operações com maquinas Creality')


# Parser para o IP no endpoint get_info_from_ip
info_parser = reqparse.RequestParser()
info_parser.add_argument('IP', type=str, required=True, help='Endereço IP da máquina')


device_registration_parser = reqparse.RequestParser()
device_registration_parser.add_argument('Machine_Name', type=str, required=True, help='Nome da máquina')
device_registration_parser.add_argument('ip_address', type=str, required=True, help='Endereço IP do dispositivo')
device_registration_parser.add_argument('Apelido', type=str, required=False, help='Apelido da máquina de impressão')
device_registration_parser.add_argument('Tipo', type=str, required=True, help='Tipo da máquina (resina ou FDM)')
device_registration_parser.add_argument('Marca', type=str, required=True, help='Marca da máquina de impressão')
device_registration_parser.add_argument('API', type=str, required=True, help='Rota da api')


def save_printer_to_csv(printer_name, nickname, ip, printer_type, brand,api):
    file_exists = os.path.isfile(CSV_FILE_PATH)
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        fieldnames = ['Machine_Name', 'Apelido', 'IP', 'Tipo', 'Marca', 'api']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Se o arquivo não existir, escreve o cabeçalho
        if not file_exists:
            writer.writeheader()

        # Adiciona a nova impressora
        writer.writerow({
            'Machine_Name': printer_name,
            'Apelido': nickname,
            'IP': ip,
            'Tipo': printer_type,
            'Marca': brand,
            'api': api
        })

@general_operations.route('/add_printer')
class Add_printer(Resource):
    @elegoo_printer_operations.doc(responses={200: 'Impressora adicionada com sucesso', 400: 'Falhou'})
    @general_operations.expect(device_registration_parser)
    def post(self):
        # Recebe os dados via formulário
        args = device_registration_parser.parse_args()

        try:
            # Extrai os dados
            printer_name = args['Machine_Name']
            nickname = args['Apelido']
            ip = args['ip_address']  # Corrigido para pegar 'ip_address' e não 'IP'
            printer_type = args['Tipo']
            brand = args['Marca']
            api = args['API']

            if not all([printer_name, nickname, ip, printer_type, brand,api]):
                return jsonify({"status": "error", "message": "Todos os campos são obrigatórios."}), 400

            # Salva a impressora no arquivo CSV
            save_printer_to_csv(printer_name, nickname, ip, printer_type, brand, api)

            return {"status": "success", "message": "Impressora adicionada com sucesso."}, 200

        except Exception as e:
            logger.error(f"Erro ao adicionar impressora: {e}")
            return jsonify({"status": "error", "message": "Erro ao adicionar impressora."}), 400

@elegoo_printer_operations.route('/get_printer_info')
class Get_printer_info(Resource):
    @elegoo_printer_operations.doc(responses={200: 'Sucesso', 400: 'Falhou'})
    @elegoo_printer_operations.expect(info_parser)
    def get(self):
        ip = request.args.get('IP')
        if not ip:
            return jsonify({"status": "error", "message": "IP não fornecido."}), 400
        printer = ElegooSaturn3Ultra(ip)
        return printer.get_printer_info(), 200

@elegoo_printer_operations.route('/get_printer_status')
class Get_printer_status(Resource):
    @elegoo_printer_operations.doc(responses={200: 'Sucesso', 400: 'Falhou'})
    @elegoo_printer_operations.expect(info_parser)
    def get(self):
        ip = request.args.get('IP')
        if not ip:
            return jsonify({"status": "error", "message": "IP não fornecido."}), 400
        printer = ElegooSaturn3Ultra(ip)
        return printer.get_status_info(), 200







def read_printers_from_csv(filename='printers.csv'):
    printers = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)  # Lê o CSV como dicionário
            for row in csv_reader:
                printers.append(row)
    except FileNotFoundError:
        print(f"Erro: O arquivo {filename} não foi encontrado.")
    return printers

# Recurso para obter as máquinas
@general_operations.route('/get_printers')
class GetPrinters(Resource):
    def get(self):
        printers = read_printers_from_csv()  # Lê as máquinas do CSV
        if not printers:
            return jsonify({"message": "Nenhuma máquina encontrada."}), 404  # Retorna mensagem caso não haja dados
        return jsonify(printers)  # Retorna as máquinas como JSON


@general_operations.route('/remove_printer_by_nickname')
class RemovePrinterByNickname(Resource):
    @general_operations.doc(responses={200: 'Máquina removida com sucesso', 400: 'Falhou'})
    @elegoo_printer_operations.expect()
    def post(self):
        nickname = request.args.get('Apelido')  # Obtém o apelido via query string
        if not nickname:
            return jsonify({"status": "error", "message": "Apelido não fornecido."}), 400

        # Chama a função para remover a impressora
        return remove_printer_by_nickname(nickname)


def remove_printer_by_nickname(nickname):
    """
    Remove uma máquina do arquivo CSV com base no apelido.

    :param nickname: Apelido da máquina a ser removida.
    :return: Mensagem de sucesso ou erro.
    """
    printers = read_printers_from_csv(CSV_FILE_PATH)  # Lê as máquinas atuais do CSV

    # Filtra as impressoras removendo a máquina com o apelido fornecido
    printers_to_save = [printer for printer in printers if printer['Apelido'] != nickname]

    if len(printers_to_save) == len(printers):
        return {"status": "error", "message": f"Máquina com apelido {nickname} não encontrada."}, 404

    # Reescreve o arquivo CSV com as impressoras restantes
    try:
        with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['Machine_Name', 'Apelido', 'IP', 'Tipo', 'Marca', 'api']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for printer in printers_to_save:
                writer.writerow(printer)

        return {"status": "success", "message": f"Máquina com apelido {nickname} removida com sucesso."}, 200
    except Exception as e:
        logger.error(f"Erro ao remover máquina: {e}")
        return {"status": "error", "message": "Erro ao remover a máquina."}, 500




# Adicionando namespaces à API
api.add_namespace(elegoo_printer_operations, path='/elegoo_operations')
api.add_namespace(creality_printer_operations, path='/creality_operations')
api.add_namespace(general_operations, path='/general_operations')




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
