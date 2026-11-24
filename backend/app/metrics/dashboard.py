"""Unit 7: Shelter Metrics.

Computes the dashboard numbers from the cat and application records:
capacity in use, average length of stay, adoption rate, and the cats
waiting longest.
"""
from dataclasses import dataclass, field


@dataclass
class MetricsResult:
    cats_in_shelter: int
    average_stay_days: float
    adoption_rate: float
    longest_waiting: list = field(default_factory=list)


def metrics(shelter):
    """Compute dashboard metrics for one shelter.

    Capacity counts resident cats only (status "available"). Average stay
    is the mean stay of adopted applications. Adoption rate is adopted
    over closed applications, so open applications never count. Longest
    waiting lists resident cats earliest arrival first. An empty shelter
    returns zeros instead of raising a division error.
    """
    cats = shelter.cats
    applications = shelter.applications
    resident = [c for c in cats if c.status == "available"]
    adopted = [a for a in applications if a.outcome == "adopted"]
    stays = [a.stay_days for a in adopted if a.stay_days is not None]
    average = sum(stays) / len(stays) if stays else 0
    closed = [a for a in applications if a.outcome is not None]
    rate = len(adopted) / len(closed) if closed else 0
    longest = sorted(resident, key=lambda c: c.arrival_date)
    return MetricsResult(
        cats_in_shelter=len(resident),
        average_stay_days=average,
        adoption_rate=rate,
        longest_waiting=longest,
    )
