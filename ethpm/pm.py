from web3.module import Module
from ethpm import Package


class PM(Module):
    def get_package(self, path: str) -> Package:
        pkg = Package.from_file(path, self.web3)
        return pkg
