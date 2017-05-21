class BlockCode(object):
    """
    Code representation of a HDB Flat

    Attributes:
        block_num (str): Block number of the flat (e.g. 370C)
        neighbourhood (str): Neighbourhood code of the flat
        contract (str): HDB contract under which the flat was built
    """
    block_num: str
    neighbourhood: str
    contract: str

    def __init__(self, block_num: str, neighborhood: str, contract: str) -> None:
        self.block_num = block_num
        self.neighbourhood = neighborhood
        self.contract = contract

    def __str__(self) -> str:
        return 'Blk {}'.format(self.block_num)

    def __repr__(self) -> str:
        return self.__str__()
