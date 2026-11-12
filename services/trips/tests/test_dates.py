from datetime import date
from trips.dates import dominant_month


def test_dominant_month_single_month():
    assert dominant_month(date(2026, 6, 15), date(2026, 6, 22)) == 6

def test_dominant_month_spanning_two_months():
    #July has more days
    assert dominant_month(date(2026, 6, 28), date(2026, 7, 5)) == 7

def test_dominant_month_tie():
    #tie, earlier month wins
    assert dominant_month(date(2026, 6, 28), date(2026, 7, 3)) == 6