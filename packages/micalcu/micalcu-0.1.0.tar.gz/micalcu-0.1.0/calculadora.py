# calculadora.py

class MiCalculadora:
    """
    Acepta 2 enteros en el constructor y expone un método sumar() que retorna la suma.
    """
    def __init__(self, a: int, b: int):
        if not (isinstance(a, int) and isinstance(b, int)):
            raise TypeError("MiCalculadora solo acepta enteros en el constructor")
        self.a = a
        self.b = b

    def sumar(self) -> int:
        return self.a + self.b

