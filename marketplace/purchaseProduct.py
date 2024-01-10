import solcx
from web3 import Web3
from eth_utils import to_checksum_address
import os

# Escolha a versão do Solidity que você deseja usar
_solc_version = "0.8.0"
solcx.install_solc(_solc_version)

# Código do contrato
contract_source = '''
pragma solidity ^0.8.0;

contract Marketplace {
    string public name;
    uint public productCount = 0;
    mapping(uint => Product) public products;

    struct Product {
        uint id;
        string name;
        uint price;
        address payable owner;
        bool purchased;
    }

    event ProductCreated(
        uint id,
        string name,
        uint price,
        address payable owner,
        bool purchased
    );

    event ProductPurchased(
        uint id,
        string name,
        uint price,
        address payable owner,
        bool purchased
    );

    constructor() {
        name = "Dapp University Marketplace";
    }

    function createProduct(string memory _name, uint _price) public {
        // Require a valid name
        require(bytes(_name).length > 0);
        // Require a valid price
        require(_price > 0);
        // Increment product count
        productCount ++;
        // Create the product
        products[productCount] = Product(productCount, _name, _price, payable(msg.sender), false);
        // Trigger an event
        emit ProductCreated(productCount, _name, _price, payable(msg.sender), false);
    }

    function purchaseProduct(uint _id) public payable {
        // Fetch the product
        Product storage _product = products[_id];
        // Fetch the owner
        address payable _seller = _product.owner;
        // Make sure the product has a valid id
        require(_product.id > 0 && _product.id <= productCount);
        // Require that there is enough Ether in the transaction
        require(msg.value >= _product.price);
        // Require that the product has not been purchased already
        require(!_product.purchased);
        // Require that the buyer is not the seller
        require(_seller != payable(msg.sender));
        // Transfer ownership to the buyer
        _product.owner = payable(msg.sender);
        // Mark as purchased
        _product.purchased = true;
        // Update the product
        products[_id] = _product;
        // Pay the seller by sending them Ether
        _seller.transfer(msg.value);
        // Trigger an event
        emit ProductPurchased(_id, _product.name, _product.price, _seller, true);
    }
}
'''

# Conectar ao nó Besu
w3 = Web3(Web3.HTTPProvider('http://10.20.30.5:8585'))

# Endereço e chave privada do comprador
buyer_address = to_checksum_address('0x8da6423Fc50237d46E1B3882E1e335106408CeB9')
private_key_buyer = '0xe531b7de360c4acfde014298668f496ac82dc70dfb1a3c23f9c989e0aac1e0f8'

# Endereço do contrato implantado
contract_address = '0x6c6fdB66e7f9349fd24abD161ccd610F362bbc6C'

# Criar instância do contrato
checksum_address = to_checksum_address(contract_address)
contract_interface = solcx.compile_source(contract_source)['<stdin>:Marketplace']
contract = w3.eth.contract(address=checksum_address, abi=contract_interface['abi'])

# Nome do arquivo para armazenar o último product_id_to_buy
last_product_id_file = 'last_product_id.txt'

# Verificar se o arquivo existe
if os.path.exists(last_product_id_file):
    # Se o arquivo existe, ler o último product_id_to_buy salvo
    with open(last_product_id_file, 'r') as file:
        last_product_id = int(file.read())
else:
    # Se o arquivo não existe, iniciar com o product_id_to_buy inicial
    last_product_id = 9  # ou o valor inicial desejado

# Escolher um produto para comprar (por exemplo, o próximo produto disponível)
last_product_id_file = 'last_product_id.txt'

# Lê o último product_id_to_buy do arquivo
try:
    with open(last_product_id_file, 'r') as file:
        last_product_id = int(file.read().strip())
except FileNotFoundError:
    # Se o arquivo não existir, comece com o valor inicial
    last_product_id = 8

# Incrementa o product_id_to_buy para a próxima execução
product_id_to_buy = last_product_id + 1

# Obter o número total de produtos disponíveis (productCount)
total_products = contract.functions.productCount().call()

# Verificar se ainda há produtos disponíveis para compra
if product_id_to_buy <= total_products:
    # Obter o preço do produto desejado (pode ser ajustado conforme necessário)
    product_price_to_buy = 1  # Defina o preço correspondente ao produto que você deseja comprar

    # Obter o nonce do comprador usando a instância w3.eth.get_transaction_count
    nonce = w3.eth.get_transaction_count(buyer_address)

    # Chamar a função purchaseProduct do contrato
    transaction_data = contract.functions.purchaseProduct(product_id_to_buy).build_transaction({
        'from': buyer_address,
        'gas': 2000000,
        'gasPrice': Web3.to_wei('1', 'gwei'),
        'nonce': nonce,
        'value': product_price_to_buy,
    })

    # Assinar e enviar a transação
    signed_transaction = w3.eth.account.sign_transaction(transaction_data, private_key_buyer)
    transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    print(f'Transação enviada. Hash: {transaction_hash.hex()}')

    # Atualizar o arquivo com o último product_id_to_buy utilizado
    with open(last_product_id_file, 'w') as file:
        file.write(str(product_id_to_buy))
else:
    print('Não há mais produtos disponíveis para compra.')