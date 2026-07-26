from __future__ import annotations

RATES_IN_COPPER = {
    "pp": 1000,
    "gp": 100,
    "sp": 10,
    "cp": 1,
}

DENOMINATION_ATTRIBUTES = {
    "pp": "platinum",
    "gp": "gold",
    "sp": "silver",
    "cp": "copper",
}


def calculate_exchange(
    from_denomination: str,
    to_denomination: str,
    amount: int,
    current_wallet: dict[str, int],
) -> dict[str, int]:
    """Return denomination balance changes without mutating the wallet."""
    from_denomination = from_denomination.strip().lower()
    to_denomination = to_denomination.strip().lower()

    if amount <= 0:
        raise ValueError("Amount must be a positive integer.")
    if (
        from_denomination not in RATES_IN_COPPER
        or to_denomination not in RATES_IN_COPPER
    ):
        raise ValueError("Invalid denomination specified.")
    if from_denomination == to_denomination:
        raise ValueError(f"Cannot exchange {from_denomination.upper()} to itself.")

    from_attribute = DENOMINATION_ATTRIBUTES[from_denomination]
    current_amount = current_wallet.get(from_attribute, 0)
    if current_amount < amount:
        raise ValueError(
            f"Not enough {from_denomination.upper()} to exchange. "
            f"Needs {amount}, has {current_amount}."
        )

    total_copper = amount * RATES_IN_COPPER[from_denomination]
    destination_rate = RATES_IN_COPPER[to_denomination]
    destination_amount, remainder = divmod(total_copper, destination_rate)

    distributed = {denomination: 0 for denomination in RATES_IN_COPPER}
    distributed[to_denomination] = destination_amount

    order = ["pp", "gp", "sp", "cp"]
    destination_index = order.index(to_denomination)
    for denomination in order[destination_index + 1 :]:
        distributed[denomination], remainder = divmod(
            remainder,
            RATES_IN_COPPER[denomination],
        )

    changes = {attribute: 0 for attribute in DENOMINATION_ATTRIBUTES.values()}
    changes[from_attribute] -= amount
    for denomination, received in distributed.items():
        changes[DENOMINATION_ATTRIBUTES[denomination]] += received

    if all(change == 0 for change in changes.values()):
        raise ValueError(
            f"This exchange has no effect. The amount {amount} "
            f"{from_denomination.upper()} is too small to obtain any "
            f"{to_denomination.upper()} or intermediate coins."
        )

    return changes
