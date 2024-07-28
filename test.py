class Identities:
    def __init__(self, _l):
        self.l = _l

    def __eq__(self, value: object) -> bool:
        return value in self.l


i = Identities([1, 2])
print(i)
print(1 == i)
