"""Prisregler för TechRetail AB.

Lektion 1: du skriver komponenttester (enhetstester) för funktionerna i den här
filen. Läs reglerna nedan noga – de är din kravspecifikation.

Regler
------
1. Rabatt anges i procent och måste vara mellan 0 och 100 (båda inräknade).
   Annars blir det ValueError.
2. Ett pris får inte vara negativt. Annars blir det ValueError.
3. Priset efter rabatt avrundas till hela ören (två decimaler).
   Exakt halvt öre avrundas uppåt: 0,075 kr blir 0,08 kr.
4. Frakten är 49 kr när ordervärdet är under 500 kr. Från och med 500 kr är
   frakten gratis.

Beloppen räknas internt med Decimal för att undvika avrundningsfel, men
funktionerna tar emot och returnerar vanliga tal (float). Därför kan du skriva
till exempel ``assert apply_discount(199, 15) == 169.15`` i dina tester.
"""

from decimal import ROUND_HALF_UP, Decimal

SHIPPING_COST = 49.0
FREE_SHIPPING_FROM = 500.0

_ORE = Decimal("0.01")


def _to_decimal(value) -> Decimal:
    return Decimal(str(value))


def apply_discount(price: float, percent: float) -> float:
    """Returnera priset efter rabatt, avrundat till hela ören.

    Exempel: apply_discount(199, 15) returnerar 169.15
    """
    price_d = _to_decimal(price)
    percent_d = _to_decimal(percent)
    if price_d < 0:
        raise ValueError("Priset får inte vara negativt.")
    if percent_d < 0 or percent_d > 100:
        raise ValueError("Rabatten måste vara mellan 0 och 100 procent.")
    discounted = price_d * (100 - percent_d) / 100
    return float(discounted.quantize(_ORE, rounding=ROUND_HALF_UP))


def shipping_cost(order_total: float) -> float:
    """Returnera fraktkostnaden för ett ordervärde (i kronor, efter rabatt).

    Exempel: shipping_cost(300) returnerar 49.0 och shipping_cost(800) returnerar 0.0
    """
    total = _to_decimal(order_total)
    if total < 0:
        raise ValueError("Ordervärdet får inte vara negativt.")
    return 0.0 if total >= _to_decimal(FREE_SHIPPING_FROM) else SHIPPING_COST
