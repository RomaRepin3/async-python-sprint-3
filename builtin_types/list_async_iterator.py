class ListAsyncIterator:
    """
    Асинхронный итератор для списков.
    """

    def __init__(self, items: list):
        self._items = items
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index < len(self._items):
            item = self._items[self._index]
            self._index += 1
            return item
        else:
            raise StopAsyncIteration
