from decimal import Decimal, ROUND_HALF_UP, getcontext

# Configure global decimal precision
getcontext().prec = 28  # 28 digits precision is plenty for finance

class Money(Decimal):
    """A safe Decimal subclass specialized for currency operations."""

    def __new__(cls, value = "0.00"):
        # Convert anything (int, float, str) to Decimal safely
        return super().__new__(cls, str(value))

    # Standard rounding to 2 decimal places (cents)
    def round2(self) -> "Money":
        return Money(self.quantize(Decimal("0.01"), rounding = ROUND_HALF_UP))

    # Quantize to arbitrary step (e.g., $1, $0.05, etc.)
    def quantize_to_step(self, step: "Money") -> "Money":
        step = Decimal(step)
        quantized = (self / step).quantize(Decimal("1"), rounding = ROUND_HALF_UP) * step
        return Money(quantized)

    # Override __str__ for nicer formatting
    def __str__(self):
        return f"{self.round2():.2f}"

    # Override addition/subtraction to ensure Money type consistency
    def __add__(self, other):
        return Money(super().__add__(Money(other)))

    def __sub__(self, other):
        return Money(super().__sub__(Money(other)))

    def __radd__(self, other):
        # support sum() where start is 0 (an int)
        return self.__add__(other)

    def __mul__(self, other):
        return Money(super().__mul__(Money(other)))

    def __rmul__(self, other):
        return Money(super().__rmul__(Money(other)))

    def __truediv__(self, other):
        return Money(super().__truediv__(Money(other)))

    def __rtruediv__(self, other):
        return Money(super().__rtruediv__(Money(other)))

    # Optional helpers
    def is_positive(self) -> bool:
        return self > 0

    def is_zero(self) -> bool:
        return self == 0

    # Convenience constructors
    @classmethod
    def from_decimal(cls, d) -> "Money":
        if isinstance(d, Money):
            return d
        # Accept Decimal or numeric types
        return cls(str(d))

    @classmethod
    def from_float(cls, f: float) -> "Money":
        return cls(str(f))
