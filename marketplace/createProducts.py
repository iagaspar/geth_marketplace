import solcx
from web3 import Web3
from eth_utils import to_checksum_address

# Escolha a versão do Solidity que você deseja usar
_solc_version = "0.8.0"
solcx.install_solc(_solc_version)

# Conectar ao nó Besu
w3 = Web3(Web3.HTTPProvider('http://10.20.30.5:8585'))

# Endereço e chave privada do remetente
sender_address = '0x493e78581bBf7B9E750FA94d11b9aD058d743d17'
private_key = '0x1ff64cf779b111a1bbb78e813b0bc227ec39472b6fd189fe9925473ddea0898f'
buyer_address = to_checksum_address('0x493e78581bBf7B9E750FA94d11b9aD058d743d17')

# Caminho do arquivo do contrato
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

compiled_sol = solcx.compile_source(contract_source)
contract_interface = compiled_sol['<stdin>:Marketplace']

# Endereço do contrato implantado
contract_address = '0x6c6fdB66e7f9349fd24abD161ccd610F362bbc6C'

# Criar instância do contrato
checksum_address = to_checksum_address(contract_address)
contract = w3.eth.contract(address=checksum_address, abi=contract_interface['abi'])

# Dados do produto
product_name = "produto"
product_price = 1  # 1 gwei

# Obter o nonce do remetente usando a instância w3.eth.get_transaction_count
nonce = w3.eth.get_transaction_count(sender_address)

# Chamar a função createProduct do contrato
transaction_data = contract.functions.createProduct(product_name, product_price).build_transaction({
    'from': sender_address,
    'gas': 2000000,
    'gasPrice': Web3.to_wei('1', 'gwei'),
    'nonce': nonce,
})

# Assinar e enviar a transação
signed_transaction = w3.eth.account.sign_transaction(transaction_data, private_key)
transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

print(f'Transação enviada. Hash: {transaction_hash.hex()}')
