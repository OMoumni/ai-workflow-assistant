
import csv
from pathlib import Path

from tools import analysiere_tickets, priorisiere_ticket


# Path to our CSV file
dateipfad = Path(__file__).parent / "data" / "tickets.csv"

# Read all tickets
with open(dateipfad, "r", encoding="utf-8-sig", newline="") as datei:
    reader = csv.DictReader(datei)
    tickets = list(reader)


# Display number of tickets
print("Anzahl der Tickets:", len(tickets))


# Display all tickets
print("\nAlle Tickets:")

for ticket in tickets:
    print(ticket["beschreibung"])


# Display only open tickets
print("\nOffene Tickets:")

for ticket in tickets:
    if ticket["status"] == "Offen":
        print(ticket["beschreibung"])


# Analyze open tickets by category
ergebnis = analysiere_tickets(tickets)

print("\nOffene Tickets pro Kategorie:")

for kategorie, anzahl in ergebnis.items():
    print(kategorie, ":", anzahl)


# Prioritize open tickets
print("\nPriorisierung der offenen Tickets:")

for ticket in tickets:
    if ticket["status"] == "Offen":
        prioritaet = priorisiere_ticket(ticket)

        print(ticket["beschreibung"], "->", prioritaet)
