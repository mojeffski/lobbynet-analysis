# Datennotizen

Was man beim Analysieren wissen muss. Ab Release v0.2 steht das meiste im
README des Releases („Known limitations“), weil das Wissen dann mit den
Daten reist. v0.1 ist schon geschrieben und unveränderlich, seine
Einschränkungen stehen deshalb hier.

## v0.1.1 (Schema 1.1, 08.11.2026)

Dieselben Daten wie v0.1: Die acht Tabellen sind bytegleich. Neu sind
`text` (der ganze Text, wie ihn das LLM gelesen hat) und `mention` (alles,
was das LLM in einem Text gelesen hat, auch vage und Sammelangaben, mit
Präzisionsklasse). Weg zurück zur Quelle: `observation.mention_id` →
`mention` → `text`. Das README des Releases enthält ab jetzt „Known
limitations“. **`text` enthält teils Namen und E-Mail-Adressen von Personen:
nicht veröffentlichen.**

Alles Folgende gilt unverändert auch für v0.1.1.

## v0.1 (Schema 1.0, 03.11.2026)

**Richtung und Zeit**
- Eine Kante ist **Mitglied → Organisation**. Bei „is member of“ ist die
  berichtende Organisation das Mitglied, bei „has members“ die Organisation
  (`observation.reported_by`).
- Die Zeit ist der Snapshot (18 Stück, 2015-06 bis 2026-10). Die Abstände
  sind ungleich, und **2018 fehlt**. Vergleiche über `snapshot_index` oder
  `reference_month`, nie über gleiche Abstände.
- **Fehlend ist nicht 0:** `edge_snapshot.observable` sagt, ob eine Kante
  hätte berichtet werden können. Ohne diese Unterscheidung sieht jede
  Registrierungslücke wie das Ende einer Mitgliedschaft aus.
- `first_observed` und `last_observed` sind zensiert. Vor 2015 und nach
  2026 ist nichts bekannt.

**Quellenfelder je Ära**
- **2015:** nur die Richtung „is member of“ (`NETWORKING`). „Has members“
  gibt es nicht, `MEMBERS` ist eine Zahl.
- **2016–2022:** `Membership` / `Member organisations`. Das eingehende Feld
  enthält oft nur eine URL (44,9 %). Solche Texte ergeben keine Kanten, bis
  Mitgliederlisten ausgelesen werden.
- **2023–2026:** klar getrennte Felder.
- Ein Sprung in den Kennzahlen an einer Ära-Grenze ist deshalb zuerst ein
  Verdacht auf ein Messartefakt.

**Knoten**
- **35 %** der Erwähnungen sind einer Register- oder Referenzquelle
  zugeordnet (Register, ROR, CORDIS, FTS, Kohesio). Der Rest sind **eigene
  Knoten**, die über ihre normalisierte Schreibweise identifiziert werden.
  Dieselbe Organisation kann darum als mehrere Knoten auftreten
  („SolarPower Europe“ / „Solar Power Europe“). Unscharfer Abgleich folgt in
  v0.2.
- Neuregistrierungen derselben Organisation sind zu einem Knoten
  zusammengeführt (`organisation.register_ids`).
- `organisation.abbreviation_only` und `match_status = single_weak_match`
  (eindeutiges Kürzel, Stichprobe ~90 % richtig) markieren die unsichereren
  Zuordnungen. Wenn ein Ergebnis nicht davon abhängen soll, herausfiltern.
- **Keine Kanten** aus Selbst-Erwähnungen, Schleifen (Mitglied =
  Organisation nach der Auflösung) und EU-Programmen. Sie stehen in
  `observation` mit `is_edge = false`.

**„Has members“ ist nicht immer Mitgliedschaft**
- Das Feld heißt im Register „members and/or affiliated“. Manche
  Organisationen listen Partner, Kunden oder Programmteilnehmer.
- Beispiel: Dopper B.V. (Trinkflaschen) mit 946 „Mitgliedern“ aus
  Partner-NGOs und Firmen seines Programms „Dopper Wave“.
- Bei Spitzenwerten eingehender Kanten deshalb immer die Kategorie der
  berichtenden Organisation prüfen (`organisation_snapshot.category`).

**Messfehler der Extraktion** (ADR-0009, Untergrenzen)
- 0,45 % der extrahierten Erwähnungen sind keine Organisation.
- 0,84 % der echten Organisationen fehlen.
- Die Prüfung hat ein Modell gemacht, nicht ein Mensch.

**Selbstauskunft**
- Alles stammt aus Selbstauskünften registrierter Organisationen. Nicht
  registrierte Organisationen kommen nur über die Angaben anderer vor. Ihre
  Netzwerkposition ist darum systematisch unterschätzt, vor allem bei
  ausgehenden Kanten.
