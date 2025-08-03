import argparse
from dataclasses import dataclass


@dataclass
class Arguments:
    config: str
    model: str


class ArgumentParser:

    def __init__(self, description: str):
        self.parser = argparse.ArgumentParser(description=description)
        self.parser.add_argument(
            "-c", "--config", type=str, help="Path to config file", required=True
        )
        self.parser.add_argument(
            "-m", "--model", type=str, help="Specify model", required=True
        )

    def parse(self) -> Arguments:
        args = self.parser.parse_args()
        return Arguments(config=args.config, model=args.model)