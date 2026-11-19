
import os
import csv
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import analysiere_tickets, priorisiere_ticket


# 1. API-Schlüssel aus .env laden
load_dotenv(
    Path(__file__).parent / ".env",
    override=True
)

# 2. Verbindung zu Gemini herstellen
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


# 3. Werkzeug für unseren KI-Agenten
def hole_ticket_statistik() -> dict[str, int]:
    """
    Liest die CSV-Datei und zählt die offenen
    Tickets pro Kategorie.
    """

    dateipfad = (
        Path(__file__).parent / "data" / "tickets.csv"
    )

    with open(
        dateipfad,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as datei:
        reader = csv.DictReader(datei)
        tickets = list(reader)

    print("Tool wurde aufgerufen!")

    return analysiere_tickets(tickets)



def hole_offene_tickets() -> dict:
    """Liefert offene Tickets mit regelbasierter Priorität."""

    dateipfad = Path(__file__).parent / "data" / "tickets.csv"

    with open(dateipfad, "r", encoding="utf-8-sig", newline="") as datei:
        reader = csv.DictReader(datei)
        tickets = list(reader)

    offene_tickets = []

    for ticket in tickets:
        if ticket["status"] == "Offen":

            # Unsere bestehende Python-Funktion verwenden
            ticket["prioritaet"] = priorisiere_ticket(ticket)

            offene_tickets.append(ticket)

    print("Tool hole_offene_tickets wurde aufgerufen!")

    return {"offene_tickets": offene_tickets}



# Chat mit unseren Werkzeugen erstellen
chat = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        tools=[
            hole_ticket_statistik,
            hole_offene_tickets]
    )
)

# Benutzerfrage an den Agenten
response = chat.send_message(
     """
    Analysiere alle offenen Tickets mithilfe der Python-Tools.

    Verwende die bereits berechnete Priorität jedes Tickets.
    Ändere diese Priorität nicht.

    Erstelle für jedes Ticket:
    1. Beschreibung
    2. Priorität aus den Python-Daten
    3. Eine kurze Begründung
    4. Eine empfohlene Maßnahme

    Antworte auf Deutsch.
    """
)

print("\nAntwort des KI-Agenten:")
print(response.text)


# Ordner für Berichte erstellen
bericht_ordner = Path(__file__).parent / "reports"
bericht_ordner.mkdir(exist_ok=True)

# Bericht als Markdown-Datei speichern
bericht_datei = bericht_ordner / "ticket_bericht.md"

bericht_datei.write_text(
    "# AI Workflow Assistant – Ticketbericht\n\n"
    + (response.text or "Keine KI-Antwort verfügbar."),
    encoding="utf-8"
)

print(f"\nBericht gespeichert: {bericht_datei}")
