from gltest import get_contract_factory, get_default_account, create_account
from gltest.assertions import tx_execution_succeeded
import json

TOKEN_TOTAL_SUPPLY = 1000
TRANSFER_AMOUNT = 100


def test_llm_erc20(setup_validators):
    # Account Setup
    from_account_a = get_default_account()
    from_account_b = create_account()

    # Mock Response
    mock_response = {
        "response": {
            "The balance of the sender": json.dumps(
                {
                    "transaction_success": True,
                    "transaction_error": "",
                    "updated_balances": {
                        from_account_a.address: TOKEN_TOTAL_SUPPLY - TRANSFER_AMOUNT,
                        from_account_b.address: TRANSFER_AMOUNT,
                    },
                }
            )
        },
        "eq_principle_prompt_non_comparative": {"The balance of the sender": True},
    }
    setup_validators(mock_response=mock_response)

    # Deploy Contract
    factory = get_contract_factory("LlmErc20")
    contract = factory.deploy(args=[TOKEN_TOTAL_SUPPLY])

    # Get Initial State
    contract_state_1 = contract.get_balances(args=[]).call()
    assert contract_state_1[from_account_a.address] == TOKEN_TOTAL_SUPPLY

    # Transfer from User A to User B
    transaction_response_call_1 = contract.transfer(
        args=[TRANSFER_AMOUNT, from_account_b.address]
    ).transact()
    assert tx_execution_succeeded(transaction_response_call_1)

    # Get Updated State
    contract_state_2_1 = contract.get_balances(args=[]).call()
    assert (
        contract_state_2_1[from_account_a.address]
        == TOKEN_TOTAL_SUPPLY - TRANSFER_AMOUNT
    )
    assert contract_state_2_1[from_account_b.address] == TRANSFER_AMOUNT

    # Get Updated State
    contract_state_2_2 = contract.get_balance_of(args=[from_account_a.address]).call()
    assert contract_state_2_2 == TOKEN_TOTAL_SUPPLY - TRANSFER_AMOUNT

    # Get Updated State
    contract_state_2_3 = contract.get_balance_of(args=[from_account_b.address]).call()
    assert contract_state_2_3 == TRANSFER_AMOUNT
