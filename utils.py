import re


def filter_guest_accounts(term) -> bool:
    return re.fullmatch(r"Guest\d{4}", term)
