# calculadora.py

class MiCalculadora:
    """
    Acepta 2 enteros en el constructor y expone métodos de suma, resta, multiplicación y división.
    """
    def __init__(self, a: int, b: int):
        if not (isinstance(a, int) and isinstance(b, int)):
            raise TypeError("MiCalculadora solo acepta enteros en el constructor")
        self.a = a
        self.b = b

    def sumar(self) -> int:
        return self.a + self.b

    def restar(self) -> int:
        return self.a - self.b

    def multiplicar(self) -> int:
        return self.a * self.b

    def dividir(self) -> float:
        if self.b == 0:
            raise ZeroDivisionError("No se puede dividir entre cero")
        return self.a / self.b

