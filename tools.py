
def analysiere_tickets(tickets):
    statistik = {}

    for ticket in tickets:
        if ticket["status"] == "Offen":
            kategorie = ticket["kategorie"]

            if kategorie not in statistik:
                statistik[kategorie] = 0

            statistik[kategorie] += 1

    return statistik


def priorisiere_ticket(ticket):
    beschreibung = ticket["beschreibung"].lower()

    if "server antwortet nicht" in beschreibung:
        return "Hoch"

    elif "temperaturfehler" in beschreibung:
        return "Hoch"

    elif "lieferung" in beschreibung:
        return "Mittel"

    elif "anmelden" in beschreibung:
        return "Mittel"

    else:
        return "Niedrig"
