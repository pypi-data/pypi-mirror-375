from typing import Any, Dict, List

from alpaca.common.models import ValidateBaseModel as BaseModel


class TimeSeriesMixin:
    pass


class BaseDataSet(BaseModel):
    """
    Base class to process data models for trades, bars quotes, and news.
    """

    data: Dict[str, List[BaseModel]] = {}

    def __getitem__(self, symbol: str) -> Any:
        """Gives dictionary-like access to multi-symbol data

        Args:
            symbol (str): The ticker identifier for the desired data

        Raises:
            KeyError: Symbol does not exist for data

        Returns:
            List[Bar]: The data for the given symbol
        """
        if symbol not in self.data:
            raise KeyError(f"No key {symbol} was found.")

        return self.data[symbol]

    def dict(self, **kwargs) -> dict:
        """
        Gives dictionary representation of data.

        Returns:
            dict: The data in dictionary form.
        """
        # converts each data (Bar, Quote, etc) in the symbol specific lists to its dictionary format
        return {
            symbol: list(map(lambda d: d.model_dump(), data_list))
            for symbol, data_list in self.data.items()
        }
