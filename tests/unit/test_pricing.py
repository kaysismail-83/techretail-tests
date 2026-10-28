"""Komponenttester (enhetstester) för src/techretail/pricing.py – lektion 1.

De tre testerna som börjar med test_exempel_ är givna. Läs dem först.
Varje test följer AAA: Arrange (förbered) – Act (gör en sak) – Assert (kontrollera).
"""

import pytest

from techretail.pricing import apply_discount, shipping_cost


def test_exempel_10_procent_rabatt_drar_av_en_tiondel():
    # Arrange
    pris = 200
    # Act
    resultat = apply_discount(pris, 10)
    # Assert
    assert resultat == 180.0


def test_exempel_0_procent_rabatt_ger_samma_pris():
    # Arrange
    pris = 199.90
    # Act
    resultat = apply_discount(pris, 0)
    # Assert
    assert resultat == 199.90


def test_exempel_negativ_rabatt_ger_valueerror():
    # Arrange
    pris = 100
    # Act och Assert: pytest.raises kontrollerar att rätt fel uppstår
    with pytest.raises(ValueError):
        apply_discount(pris, -1)


# TODO (lektion 1): Skriv minst 5 egna tester här under.
#
# Regler för dina tester:
#   - Namnet ska börja med test_ men INTE med test_exempel_ (då räknas de inte).
#   - Ett test kontrollerar en sak. Använd AAA-kommentarerna som i exemplen.
#
# Använd gränsvärden och ekvivalensklasser. Förslag:
#   1. Gränsvärdet 100 procent: vad ska priset bli?
#   2. Strax över gränsen: 101 procent.
#   3. Avrundning till hela ören: 15 procent på 99,99 kr.
#   4. Frakt strax under gränsen: ordervärde 499,99 kr.
#   5. Frakt precis på gränsen: ordervärde 500 kr.
#
# Kör dina tester med:  uv run pytest tests/unit -v
# Kontrollera milstolpen med:  make milstolpe L=1
