
import unittest

from tools import analysiere_tickets, priorisiere_ticket


class TestTools(unittest.TestCase):

    def test_analyse(self):
        tickets = [
            {"status": "Offen", "kategorie": "IT"},
            {"status": "Offen", "kategorie": "IT"},
            {"status": "Erledigt", "kategorie": "IT"}
        ]

        ergebnis = analysiere_tickets(tickets)

        self.assertEqual(ergebnis["IT"], 2)

    def test_hohe_prioritaet(self):
        ticket = {
            "beschreibung": "Server antwortet nicht"
        }

        self.assertEqual(priorisiere_ticket(ticket), "Hoch")

    def test_mittlere_prioritaet(self):
        ticket = {
            "beschreibung": "Lieferung ist verspaetet"
        }

        self.assertEqual(priorisiere_ticket(ticket), "Mittel")


if __name__ == "__main__":
    unittest.main()
