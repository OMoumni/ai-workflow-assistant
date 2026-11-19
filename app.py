
import os
import csv
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import analysiere_tickets, priorisiere_ticket


# =====================================
# 1. KONFIGURATION
# =====================================

BASE_DIR = Path(__file__).parent
DATEIPFAD = BASE_DIR / "data" / "tickets.csv"

MODELL = "gemini-3.5-flash-lite"

st.set_page_config(
    page_title="AI Workflow Assistant",
    page_icon="🤖",
    layout="wide"
)


# =====================================
# 2. TICKET-FUNKTIONEN
# =====================================

def lade_tickets():
    with open(
        DATEIPFAD,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as datei:
        return list(csv.DictReader(datei))


def hole_ticket_statistik() -> dict[str, int]:
    """Zählt alle offenen Tickets pro Kategorie."""

    tickets = lade_tickets()

    return analysiere_tickets(tickets)


def hole_offene_tickets() -> dict:
    """
    Liefert offene Tickets mit ihren
    regelbasiert berechneten Prioritäten.
    """

    tickets = lade_tickets()
    offene_tickets = []

    for ticket in tickets:
        if ticket["status"] == "Offen":

            ticket["prioritaet"] = priorisiere_ticket(
                ticket
            )

            offene_tickets.append(ticket)

    return {"offene_tickets": offene_tickets}


# =====================================
# 3. DATEN LADEN
# =====================================

try:
    tickets = lade_tickets()

except (OSError, csv.Error) as fehler:
    st.error(f"Tickets konnten nicht geladen werden: {fehler}")
    st.stop()


offene_tickets = [
    ticket for ticket in tickets
    if ticket["status"] == "Offen"
]

hohe_prioritaet = sum(
    1 for ticket in offene_tickets
    if priorisiere_ticket(ticket) == "Hoch"
)


# =====================================
# 4. DASHBOARD
# =====================================

st.title("🤖 AI Workflow Assistant")

st.caption(
    "Intelligentes Ticketmanagement | "
    "Automatisierung | KI-gestützte Empfehlungen"
)

st.divider()

st.subheader("📊 Dashboard – Überblick")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Gesamte Tickets",
    value=len(tickets)
)

col2.metric(
    label="Offene Tickets",
    value=len(offene_tickets)
)

col3.metric(
    label="Hohe Priorität",
    value=hohe_prioritaet
)

st.divider()


# =====================================
# 5. TICKETÜBERSICHT
# =====================================


# =====================================
# 5. OFFENE TICKETS
# =====================================

st.subheader("📋 Offene Tickets")

st.write(
    "Übersicht aller aktuell offenen Vorgänge "
    "mit ihren automatisch berechneten Prioritäten."
)

anzeige = []

for ticket in offene_tickets:
    anzeige.append({
        "Ticket-ID": ticket["id"],
        "Kategorie": ticket["kategorie"],
        "Beschreibung": ticket["beschreibung"],
        "Priorität": priorisiere_ticket(ticket)
    })

st.dataframe(
    anzeige,
    hide_index=True,
    use_container_width=True
)

st.caption(
    f"Aktuell sind {len(offene_tickets)} Tickets offen. "
    "Die Prioritäten werden anhand definierter Python-Regeln berechnet."
)

st.divider()


# =====================================
# 6. KI-ASSISTENT
# =====================================

st.subheader("🧠 KI-Assistent")

st.write(
    "Stelle eine Frage zu den Tickets oder "
    "lasse dir Lösungsvorschläge erstellen."
)

frage = st.text_area(
    "Deine Frage an den KI-Assistenten",
    value=(
        "Analysiere alle offenen Tickets. "
        "Welche Probleme sollten zuerst "
        "bearbeitet werden? "
        "Erkläre die vorhandenen Prioritäten "
        "und schlage passende Maßnahmen vor."
    ),
    height=120
)


if "ki_antwort" not in st.session_state:
    st.session_state.ki_antwort = None


if st.button(
    "✨ KI-Empfehlungen anfordern",
    type="primary"
):

    st.session_state.ki_antwort = None

    if not frage.strip():
        st.warning("Bitte gib zuerst eine Frage ein.")

    else:

        # API-Schlüssel aus .env laden
        load_dotenv(
            BASE_DIR / ".env",
            override=True
        )

        api_key = os.getenv(
            "GEMINI_API_KEY", ""
        ).strip()

        if not api_key:
            st.error(
                "Gemini API Key fehlt. "
                "Bitte überprüfe deine .env-Datei."
            )

        else:

            with st.spinner(
                "Gemini analysiert deine Anfrage..."
            ):

                try:

                    # Gemini-Verbindung
                    client = genai.Client(
                        api_key=api_key
                    )

                    # Chat mit unseren Tools
                    chat = client.chats.create(
                        model=MODELL,

                        config=types.GenerateContentConfig(
                            tools=[
                                hole_ticket_statistik,
                                hole_offene_tickets
                            ],

                            system_instruction=(
                                "Du bist ein KI-Assistent "
                                "für betriebliches Ticketmanagement. "
                                "Nutze die Python-Tools, wenn "
                                "Ticketdaten benötigt werden. "
                                "Erfinde keine Ticketzahlen. "
                                "Übernimm vorhandene Prioritäten "
                                "aus den Tool-Daten unverändert. "
                                "Erkläre Ursachen als Möglichkeiten, "
                                "nicht als bestätigte Fakten. "
                                "Gib sichere, nachvollziehbare "
                                "Handlungsempfehlungen. "
                                "Antworte auf Deutsch."
                            )
                        )
                    )

                    # Benutzerfrage senden
                    response = chat.send_message(
                        frage.strip()
                    )

                    antwort = response.text

                    if not antwort:
                        st.warning(
                            "Gemini hat keine Textantwort geliefert."
                        )

                    else:

                        st.session_state.ki_antwort = antwort

                        # Bericht speichern
                        bericht_ordner = (
                            BASE_DIR / "reports"
                        )

                        bericht_ordner.mkdir(
                            exist_ok=True
                        )

                        bericht_datei = (
                            bericht_ordner /
                            "ticket_bericht.md"
                        )

                        bericht_datei.write_text(
                            "# AI Workflow Assistant – Bericht\n\n"
                            + antwort,
                            encoding="utf-8"
                        )

                except Exception as fehler:
                    st.error(
                        "Die KI-Anfrage ist fehlgeschlagen."
                    )
                    st.caption(str(fehler))


# =====================================
# 7. KI-ANTWORT UND DOWNLOAD
# =====================================

if st.session_state.ki_antwort:

    st.divider()

    st.subheader("✅ KI-Analyse und Empfehlungen")

    st.markdown(
        st.session_state.ki_antwort
    )

    bericht = (
        "# AI Workflow Assistant – Bericht\n\n"
        + st.session_state.ki_antwort
    )

    st.download_button(
        label="📥 KI-Bericht herunterladen",
        data=bericht,
        file_name="ticket_bericht.md",
        mime="text/markdown"
    )


# =====================================
# 8. FOOTER
# =====================================

st.divider()

st.caption(
    "AI Workflow Assistant | "
    "Python · Streamlit · Gemini · Function Calling"
)
