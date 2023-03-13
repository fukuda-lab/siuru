from dataloaders.IDataLoader import IDataLoader


class PacketSniffer(IDataLoader):

    @staticmethod
    def can_load(filepath: str) -> bool:
        pass