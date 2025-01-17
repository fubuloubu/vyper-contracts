import pytest

from brownie import (
    reverts,
    ZERO_ADDRESS,
)

from eip712.messages import EIP712Message, EIP712Type


ERC165_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000001ffc9a7"
ERC721_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000080ac58cd"
INVALID_INTERFACE_ID = "0x0000000000000000000000000000000000000000000000000000000012345678"
ERC721_METADATA_INTERFACE_ID = b'[^\x13\x9f'
ERC721_ENUMERABLE_INTERFACE_ID = b'x\x0e\x9dc'
ERC721_TOKEN_RECEIVER_INTERFACE_ID = b'\x15\x0bz\x02'
EIP4494_INTERFACE_ID = "0x000000000000000000000000000000000000000000000000000000005604e225"

# Tests adapted from official Vyper example

@pytest.fixture(scope="module", autouse="True")
def local_account(accounts):
    a = accounts.add()
    accounts[0].transfer(a, 50000)
    yield a


@pytest.fixture(scope="module", autouse="True")
def eip4494(accounts, EIP4494):
    c = accounts[0].deploy(
        EIP4494,
        "Test Token",
        "TST",
        "https://www.test.com/",
        100,
        accounts[0],
        accounts[0]
    )

    # Mint 1 token
    c.mint(
        accounts[0],
        '1.json',
        {'from': accounts[0]}
    )
    yield c


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_supportsInterface(eip4494):

    assert eip4494.supportsInterface(ERC165_INTERFACE_ID) == 1
    assert eip4494.supportsInterface(ERC721_INTERFACE_ID) == 1
    assert eip4494.supportsInterface(ERC721_METADATA_INTERFACE_ID) == 1
    assert eip4494.supportsInterface(ERC721_ENUMERABLE_INTERFACE_ID) == 1
    assert eip4494.supportsInterface(ERC721_TOKEN_RECEIVER_INTERFACE_ID) == 1
    assert eip4494.supportsInterface(EIP4494_INTERFACE_ID) == 1

    assert eip4494.supportsInterface(INVALID_INTERFACE_ID) == 0


def test_name(eip4494):

    assert eip4494.name() == "Test Token"


def test_symbol(eip4494):

    assert eip4494.symbol() == "TST"


def test_totalSupply(eip4494):

    assert eip4494.totalSupply() == 1


def test_baseURI(eip4494):

    assert eip4494.baseURI() == "https://www.test.com/"


def test_tokenURI(eip4494):

    assert eip4494.tokenURI(1) == "https://www.test.com/1.json"

    with reverts():
        eip4494.tokenURI(0)


def test_balanceOf(accounts, eip4494):

    assert eip4494.balanceOf(accounts[0]) == 1
    assert eip4494.balanceOf(accounts[1]) == 0


def test_ownerOf(accounts, eip4494):

    assert eip4494.ownerOf(1) == accounts[0]

    with reverts():
        eip4494.ownerOf(2)


def test_tokenByIndex(eip4494):

    assert eip4494.tokenByIndex(1) == 1


def test_tokenOfOwnerByIndex(eip4494, accounts):

    assert eip4494.tokenOfOwnerByIndex(accounts[0], 1) == 1


def test_getApproved(accounts, eip4494):

    assert eip4494.getApproved(1) == ZERO_ADDRESS

    eip4494.approve(accounts[1], 1, {'from': accounts[0]})
    assert eip4494.getApproved(1) == accounts[1]


def test_isApprovedForAll(eip4494, accounts):

    assert eip4494.isApprovedForAll(accounts[0], accounts[1]) == 0

    eip4494.setApprovalForAll(accounts[1], True, {'from': accounts[0]})
    assert eip4494.isApprovedForAll(accounts[0], accounts[1]) == 1


def test_transferFrom_by_owner(accounts,eip4494):

    with reverts():
        eip4494.transferFrom(
            ZERO_ADDRESS,
            accounts[0],
            1,
            {'from': accounts[1]}
        )

        eip4494.transferFrom(
            accounts[0],
            accounts[1],
            1,
            {'from': accounts[1]}
        )

        eip4494.transferFrom(
            accounts[0],
            accounts[1],
            2,
            {'from': accounts[0]}
        )

    nonce = eip4494.nonces(1)

    tx = eip4494.transferFrom(
        accounts[0],
        accounts[1],
        1,
        {'from': accounts[0]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 1

    assert eip4494.balanceOf(accounts[0]) == 0
    assert eip4494.balanceOf(accounts[1]) == 1

    assert eip4494.ownerOf(1) == accounts[1]
    assert eip4494.nonces(1) == nonce + 1

def test_transferFrom_by_approved(accounts, eip4494):

    eip4494.approve(accounts[1], 1, {'from': accounts[0]})
    nonce = eip4494.nonces(1)

    tx = eip4494.transferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert eip4494.balanceOf(accounts[0]) == 0
    assert eip4494.balanceOf(accounts[2]) == 1

    assert eip4494.ownerOf(1) == accounts[2]
    assert eip4494.nonces(1) == nonce + 1

def test_transferFrom_by_operator(accounts, eip4494):

    eip4494.setApprovalForAll(accounts[1], True, {'from': accounts[0]})
    nonce = eip4494.nonces(1)

    tx = eip4494.transferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert eip4494.balanceOf(accounts[0]) == 0
    assert eip4494.balanceOf(accounts[2]) == 1

    assert eip4494.ownerOf(1) == accounts[2]
    assert eip4494.nonces(1) == nonce + 1

def test_safeTransferFrom_by_owner(accounts,eip4494):

    with reverts():
        eip4494.safeTransferFrom(
            ZERO_ADDRESS,
            accounts[0],
            1,
            {'from': accounts[1]}
        )

        eip4494.safeTransferFrom(
            accounts[0],
            accounts[1],
            1,
            {'from': accounts[1]}
        )

        eip4494.safeTransferFrom(
            accounts[0],
            accounts[1],
            2,
            {'from': accounts[0]}
        )

    nonce = eip4494.nonces(1)

    tx = eip4494.safeTransferFrom(
        accounts[0],
        accounts[1],
        1,
        {'from': accounts[0]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 1

    assert eip4494.balanceOf(accounts[0]) == 0
    assert eip4494.balanceOf(accounts[1]) == 1

    assert eip4494.ownerOf(1) == accounts[1]
    assert eip4494.nonces(1) == nonce + 1

def test_safeTransferFrom_by_approved(accounts, eip4494):

    eip4494.approve(accounts[1], 1, {'from': accounts[0]})
    nonce = eip4494.nonces(1)
    tx = eip4494.safeTransferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert eip4494.balanceOf(accounts[0]) == 0
    assert eip4494.balanceOf(accounts[2]) == 1

    assert eip4494.ownerOf(1) == accounts[2]
    assert eip4494.nonces(1) == nonce + 1

def test_safeTransferFrom_by_operator(accounts, eip4494):

    eip4494.setApprovalForAll(accounts[1], True, {'from': accounts[0]})
    tx = eip4494.safeTransferFrom(
        accounts[0],
        accounts[2],
        1,
        {'from': accounts[1]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == accounts[0]
    assert tx.events[0]["receiver"] == accounts[2]
    assert tx.events[0]["tokenId"] == 1

    assert eip4494.balanceOf(accounts[0]) == 0
    assert eip4494.balanceOf(accounts[2]) == 1

    assert eip4494.ownerOf(1) == accounts[2]


def test_burn(accounts, eip4494):

    with reverts():
        # No ownership
        eip4494.burn(1, {'from': accounts[1]})

    eip4494.burn(1, {'from': accounts[0]})

    assert eip4494.totalSupply() == 0
    assert eip4494.balanceOf(accounts[0]) == 0

    with reverts():
        assert eip4494.ownerOf(1) == ZERO_ADDRESS


@pytest.fixture
def test_permit(accounts, chain, local_account, eip4494):

    eip4494.mint(
        local_account,
        '2.json',
        {'from': accounts[0]}
    )

    assert eip4494.ownerOf(2) == local_account.address
    assert chain.id == 1337

    class Permit(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Vyper EIP4494"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = 1337
        _verifyingContract_: "address" = eip4494.address

        # EIP-4494 fields
        spender: "address"
        tokenId: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    nonce = int(eip4494.nonces(2))
    deadline = chain.time() + 10000

    assert nonce == 0
    assert deadline > chain.time()

    permit = Permit(
        spender=accounts[2].address,
        tokenId=2,
        nonce=nonce,
        deadline=deadline
    )

    signed = local_account.sign_message(permit)

    tx = eip4494.permit(
        permit.spender,
        permit.tokenId,
        permit.deadline,
        signed.signature,
        {'from': local_account}
    )

    assert len(tx.events) == 1
    assert tx.events[0]['owner'] == local_account.address
    assert tx.events[0]['approved'] == accounts[2].address
    assert tx.events[0]['tokenId'] == 2

    assert eip4494.getApproved(2) == accounts[2].address


@pytest.fixture
def test_permit_two(accounts, chain, local_account, eip4494):

    eip4494.mint(
        local_account,
        '2.json',
        {'from': accounts[0]}
    )

    assert eip4494.ownerOf(2) == local_account.address
    assert chain.id == 1337

    class Permit(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Vyper EIP4494"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = 1337
        _verifyingContract_: "address" = eip4494.address

        # EIP-4494 fields
        spender: "address"
        tokenId: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    nonce = int(eip4494.nonces(2))
    deadline = chain.time() + 10000

    assert nonce == 0
    assert deadline > chain.time()

    permit = Permit(
        spender=accounts[2].address,
        tokenId=2,
        nonce=nonce,
        deadline=deadline
    )

    signed = local_account.sign_message(permit)

    tx = eip4494.permit(
        permit.spender,
        permit.tokenId,
        permit.deadline,
        signed.signature,
        {'from': accounts[2]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]['owner'] == local_account.address
    assert tx.events[0]['approved'] == accounts[2].address
    assert tx.events[0]['tokenId'] == 2

    assert eip4494.getApproved(2) == accounts[2].address


def test_permit_expired(accounts, chain, local_account, eip4494):

    accounts[0].transfer(local_account, 50000)

    eip4494.mint(
        local_account,
        '2.json',
        {'from': accounts[0]}
    )

    assert eip4494.ownerOf(2) == local_account.address
    assert chain.id == 1337

    class Permit(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Vyper EIP4494"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = 1337
        _verifyingContract_: "address" = eip4494.address

        # EIP-4494 fields
        spender: "address"
        tokenId: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    nonce = int(eip4494.nonces(2))
    deadline = chain.time() - 1

    permit = Permit(
        spender=accounts[2].address,
        tokenId=2,
        nonce=nonce,
        deadline=deadline
    )

    signed = local_account.sign_message(permit)

    with reverts():
        tx = eip4494.permit(
            permit.spender,
            permit.tokenId,
            permit.deadline,
            signed.signature,
            {'from': accounts[2]}
        )

    assert eip4494.getApproved(2) == ZERO_ADDRESS


def test_permit_fail_non_owner(accounts, chain, local_account, eip4494):

    accounts[0].transfer(local_account, 50000)

    eip4494.mint(
        local_account,
        '2.json',
        {'from': accounts[0]}
    )

    assert eip4494.ownerOf(2) == local_account.address
    assert chain.id == 1337

    class Permit(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Vyper EIP4494"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = 1337
        _verifyingContract_: "address" = eip4494.address

        # EIP-4494 fields
        spender: "address"
        tokenId: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    nonce = int(eip4494.nonces(2))
    deadline = chain.time() - 1

    permit = Permit(
        spender=accounts[2].address,
        tokenId=1,
        nonce=nonce,
        deadline=deadline
    )

    signed = local_account.sign_message(permit)

    with reverts():
        tx = eip4494.permit(
            permit.spender,
            permit.tokenId,
            permit.deadline,
            signed.signature,
            {'from': accounts[2]}
        )

    assert eip4494.getApproved(1) == ZERO_ADDRESS


def test_transferFrom_by_permit_approved(accounts, local_account, eip4494, test_permit):

    nonce = eip4494.nonces(2)
    tx = eip4494.transferFrom(
        local_account,
        accounts[1],
        2,
        {'from': accounts[2]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == local_account
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 2

    assert eip4494.balanceOf(accounts[1]) == 1
    assert eip4494.balanceOf(local_account) == 0

    assert eip4494.ownerOf(2) == accounts[1]
    assert eip4494.nonces(2) == nonce + 1


def test_transferFrom_by_permit_approved_two(accounts, local_account, eip4494, test_permit_two):

    nonce = eip4494.nonces(2)
    tx = eip4494.transferFrom(
        local_account,
        accounts[1],
        2,
        {'from': accounts[2]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == local_account
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 2

    assert eip4494.balanceOf(accounts[1]) == 1
    assert eip4494.balanceOf(local_account) == 0

    assert eip4494.ownerOf(2) == accounts[1]
    assert eip4494.nonces(2) == nonce + 1


def test_safeTransferFrom_by_permit_approved(accounts, local_account, eip4494, test_permit):

    nonce = eip4494.nonces(2)
    tx = eip4494.safeTransferFrom(
        local_account,
        accounts[1],
        2,
        {'from': accounts[2]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == local_account
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 2

    assert eip4494.balanceOf(accounts[1]) == 1
    assert eip4494.balanceOf(local_account) == 0

    assert eip4494.ownerOf(2) == accounts[1]
    assert eip4494.nonces(2) == nonce + 1


def test_safeTransferFrom_by_permit_approved_two(accounts, local_account, eip4494, test_permit_two):

    nonce = eip4494.nonces(2)
    tx = eip4494.safeTransferFrom(
        local_account,
        accounts[1],
        2,
        {'from': accounts[2]}
    )

    assert len(tx.events) == 1
    assert tx.events[0]["sender"] == local_account
    assert tx.events[0]["receiver"] == accounts[1]
    assert tx.events[0]["tokenId"] == 2

    assert eip4494.balanceOf(accounts[1]) == 1
    assert eip4494.balanceOf(local_account) == 0

    assert eip4494.ownerOf(2) == accounts[1]
    assert eip4494.nonces(2) == nonce + 1


def test_multiple_permits_invalid_on_first_transfer(
    accounts,
    chain,
    local_account,
    eip4494,
    test_permit
):

    class Permit(EIP712Message):

        # EIP-712 fields
        _name_: "string" = "Vyper EIP4494"
        _version_: "string" = "1.0.0"
        _chainId_: "uint256" = 1337
        _verifyingContract_: "address" = eip4494.address

        # EIP-4494 fields
        spender: "address"
        tokenId: "uint256"
        nonce: "uint256"
        deadline: "uint256"

    nonce = int(eip4494.nonces(2))
    deadline = chain.time() + 10000

    permit_1 = Permit(
        spender=accounts[1].address,
        tokenId=2,
        nonce=nonce,
        deadline=deadline
    )

    permit_2 = Permit(
        spender=accounts[2].address,
        tokenId=2,
        nonce=nonce,
        deadline=deadline
    )

    signed_1 = local_account.sign_message(permit_1)
    signed_2 = local_account.sign_message(permit_2)

    permit_tx_1 = eip4494.permit(
        permit_1.spender,
        permit_1.tokenId,
        permit_1.deadline,
        signed_1.signature,
        {'from': accounts[1]}
    )

    assert eip4494.getApproved(2) == accounts[1]

    permit_tx_2 = eip4494.permit(
        permit_2.spender,
        permit_2.tokenId,
        permit_2.deadline,
        signed_2.signature,
        {'from': accounts[2]}
    )

    assert eip4494.getApproved(2) == accounts[2]

    tx_1 = eip4494.transferFrom(
        local_account,
        accounts[2],
        2,
        {'from': accounts[2]}
    )

    assert len(tx_1.events) == 1
    assert tx_1.events[0]["sender"] == local_account
    assert tx_1.events[0]["receiver"] == accounts[2]
    assert tx_1.events[0]["tokenId"] == 2

    assert eip4494.balanceOf(accounts[2]) == 1
    assert eip4494.balanceOf(local_account) == 0

    assert eip4494.ownerOf(2) == accounts[2]
    assert eip4494.nonces(2) == nonce + 1

    with reverts():
        eip4494.transferFrom(
            local_account,
            accounts[1],
            2,
            {'from': accounts[1]}
        )

    with reverts():
        eip4494.permit(
            permit_1.spender,
            permit_1.tokenId,
            permit_1.deadline,
            signed_1.signature,
            {'from': accounts[1]}
        )
