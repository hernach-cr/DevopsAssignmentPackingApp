from datetime import timedelta

def dominant_month(start_date, end_date):
    counts = {}
    current = start_date
    while current <= end_date:
        counts[current.month] = counts.get(current.month, 0) + 1
        current += timedelta(days=1)

    best_month = None
    best_count = -1
    for month, count in counts.items():
        if count > best_count:
            best_month = month
            best_count = count

    return best_month