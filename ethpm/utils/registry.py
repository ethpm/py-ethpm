def is_ens_domain(authority: str) -> bool:
    """
    Return false if authority is not a valid ENS domain.
    """
    # check that authority ends with the tld '.eth'
    # check that there are either 2 or 3 subdomains in the authority
    # i.e. zeppelinos.eth or packages.zeppelinos.eth
    if authority[-4:] != '.eth' or len(authority.split('.')) not in [2, 3]:
        return False
    return True
