def get_id_attr(data: dict) -> str | None:
    """Get the first key with the ID-like in it

    For example: 'id', 'idProduct', or 'productId'.

    Args:
        data (dict): data structure to analyse

    Returns:
        str | None: The ID-like name or None if not found.
    """
    id_idx: list = list(
        filter(
            lambda x: x == "id"
            or (x[:2] == "id" and x[:3][-1:].isupper())
            or x[-2:] == "Id",
            data.keys(),
        )
    )
    if not id_idx:
        return None

    id_idx_zero: str = id_idx[0]
    return id_idx_zero
