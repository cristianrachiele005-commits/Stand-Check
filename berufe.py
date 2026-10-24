# -*- coding: utf-8 -*-
"""
Berufsliste für StandCheck, nach Branchen sortiert.
Die Zahl ist ein grober Einstiegslohn pro Jahr bei 100% (CHF). Sie wird NUR für die
erfundenen Testdaten benutzt, damit die App vor den ersten echten Einträgen etwas zeigen kann.
Neue Berufe einfach in der passenden Branche ergänzen.
"""

BERUFE = {
    "Industrie": [
        ("Einkäufer/in", 72000), ("Strategische/r Einkäufer/in", 90000), ("Projektleiter/in", 92000),
        ("Polymechaniker/in", 62000), ("Konstrukteur/in", 68000), ("Automatiker/in", 64000),
        ("Elektroniker/in", 64000), ("Anlagen und Apparatebauer/in", 60000), ("Produktionsmechaniker/in", 56000),
        ("Produktionsmitarbeiter/in", 50000), ("Maschinenführer/in", 54000), ("Kunststofftechnologe/in", 56000),
        ("Maschinenbauingenieur/in", 85000), ("Elektroingenieur/in", 87000), ("Prozessingenieur/in", 88000),
        ("Produktionsleiter/in", 95000), ("Qualitätsmanager/in", 85000), ("Qualitätsprüfer/in", 58000),
        ("Servicetechniker/in", 65000), ("Instandhalter/in", 62000), ("Supply Chain Manager/in", 95000),
        ("Disponent/in", 64000), ("Arbeitsvorbereiter/in", 66000), ("Verfahrenstechniker/in", 64000),
        ("Lebensmitteltechnologe/in", 56000), ("Chemie und Pharmatechnologe/in", 62000), ("Laborant/in", 60000),
        ("Chemiker/in", 100000), ("Biologe/in", 85000), ("Regulatory Affairs Spezialist/in", 105000),
        ("Pharmaberater/in", 100000), ("Uhrmacher/in", 58000), ("Feinwerkoptiker/in", 58000),
        ("Teamleiter/in Produktion", 85000), ("Teamleiter/in Einkauf", 95000), ("Teamleiter/in Technik", 90000),
        ("Teamleiter/in Qualität", 92000), ("Abteilungsleiter/in Einkauf", 115000),
    ],
    "Bau und Handwerk": [
        ("Maurer/in", 60000), ("Zimmermann/Zimmerin", 58000), ("Schreiner/in", 56000),
        ("Elektroinstallateur/in", 58000), ("Sanitärinstallateur/in", 58000), ("Heizungsinstallateur/in", 58000),
        ("Lüftungsanlagenbauer/in", 58000), ("Maler/in", 54000), ("Gipser/in", 55000), ("Dachdecker/in", 57000),
        ("Spengler/in", 58000), ("Metallbauer/in", 58000), ("Plattenleger/in", 56000), ("Bodenleger/in", 55000),
        ("Strassenbauer/in", 58000), ("Gleisbauer/in", 60000), ("Kaminfeger/in", 55000),
        ("Landschaftsgärtner/in", 52000), ("Bauzeichner/in", 58000), ("Gebäudetechnikplaner/in", 68000),
        ("Polier/in", 78000), ("Bauführer/in", 85000), ("Bauleiter/in", 90000), ("Architekt/in", 80000),
        ("Bauingenieur/in", 85000), ("Projektleiter/in Bau", 95000), ("Baumaschinenführer/in", 62000),
        ("Bauarbeiter/in", 54000), ("Glaser/in", 56000), ("Steinmetz/in", 56000),
        ("Teamleiter/in Gebäudetechnik", 85000),
    ],
    "Automobil": [
        ("Automobil Mechatroniker/in", 58000), ("Automobil Fachmann/Fachfrau", 54000),
        ("Nutzfahrzeug Mechatroniker/in", 60000), ("Carrosseriespengler/in", 56000),
        ("Carrosserielackierer/in", 55000), ("Werkstattleiter/in", 82000), ("Automobilverkäufer/in", 70000),
        ("Kundendienstberater/in Garage", 64000), ("Zweiradmechaniker/in", 52000), ("Reifenmonteur/in", 48000),
    ],
    "Informatik": [
        ("Software Entwickler/in", 90000), ("Informatiker/in Applikationsentwicklung", 78000),
        ("Systemtechniker/in", 76000), ("ICT Supporter/in", 62000), ("Netzwerkspezialist/in", 82000),
        ("Data Scientist", 98000), ("Data Analyst", 85000), ("IT Projektleiter/in", 105000),
        ("Business Analyst", 92000), ("Cyber Security Spezialist/in", 100000), ("DevOps Engineer", 98000),
        ("UX/UI Designer/in", 82000), ("IT Architekt/in", 115000), ("Product Owner", 100000),
        ("Scrum Master", 98000), ("IT Leiter/in", 120000), ("Mediamatiker/in", 58000),
        ("SAP Berater/in", 105000), ("Cloud Engineer", 100000), ("Webentwickler/in", 80000),
        ("Datenbankadministrator/in", 90000), ("Software Tester/in", 80000),
        ("Teamleiter/in IT", 115000), ("Teamleiter/in Software Entwicklung", 120000),
    ],
    "Dienstleistung": [
        ("Sachbearbeiter/in kaufmännisch", 62000), ("Kaufmann/Kauffrau EFZ", 56000), ("Buchhalter/in", 70000),
        ("Lohnbuchhalter/in", 70000), ("Treuhänder/in", 80000), ("Controller/in", 88000),
        ("Finanzchef/in (CFO)", 140000), ("Geschäftsführer/in", 130000), ("HR Fachperson", 75000),
        ("HR Business Partner", 100000), ("Personalleiter/in", 115000), ("Recruiter/in", 78000),
        ("Assistent/in der Geschäftsleitung", 78000), ("Office Manager/in", 68000),
        ("Empfangsmitarbeiter/in", 54000), ("Teamleiter/in Backoffice", 85000), ("Steuerexperte/in", 100000),
        ("Wirtschaftsprüfer/in", 85000), ("Jurist/in", 95000), ("Rechtsanwalt/Rechtsanwältin", 100000),
        ("Anwaltsassistent/in", 66000), ("Übersetzer/in", 72000), ("Marketing Fachperson", 72000),
        ("Marketing Manager/in", 95000), ("Social Media Manager/in", 72000), ("Kommunikationsfachperson", 78000),
        ("Eventmanager/in", 70000), ("Immobilienbewirtschafter/in", 78000), ("Immobilienvermarkter/in", 80000),
        ("Unternehmensberater/in", 110000), ("Callcenter Agent/in", 52000), ("Kundendienst Mitarbeiter/in", 56000),
        ("Teamleiter/in", 90000), ("Teamleiter/in Kundendienst", 78000), ("Teamleiter/in Finanzen", 105000),
        ("Teamleiter/in HR", 100000), ("Teamleiter/in Marketing", 100000), ("Teamleiter/in Verkaufsinnendienst", 88000),
        ("Abteilungsleiter/in", 115000), ("Bereichsleiter/in", 135000),
    ],
    "Handel": [
        ("Detailhandelsfachperson", 50000), ("Detailhandelsassistent/in", 46000), ("Verkäufer/in", 48000),
        ("Kassierer/in", 45000), ("Filialleiter/in", 72000), ("Stv. Filialleiter/in", 62000),
        ("Category Manager/in", 95000), ("Key Account Manager/in", 100000), ("Aussendienstmitarbeiter/in", 80000),
        ("Verkaufsinnendienst", 62000), ("Verkaufsleiter/in", 115000), ("Kundenberater/in", 60000),
        ("Onlineshop Manager/in", 78000), ("Einkäufer/in Detailhandel", 80000), ("Visual Merchandiser", 58000),
        ("Teamleiter/in Verkauf", 80000), ("Teamleiter/in Aussendienst", 105000),
    ],
    "Logistik": [
        ("Logistiker/in", 56000), ("Lagermitarbeiter/in", 50000), ("Lagerleiter/in", 78000),
        ("Logistikleiter/in", 105000), ("Lastwagenchauffeur/in", 60000), ("Lieferwagenfahrer/in", 52000),
        ("Speditionskaufmann/Speditionskauffrau", 64000), ("Zollfachmann/Zollfachfrau", 72000),
        ("Disponent/in Transport", 66000), ("Lokführer/in", 80000), ("Buschauffeur/in", 64000),
        ("Tramchauffeur/in", 64000), ("Pilot/in", 120000), ("Flugbegleiter/in", 52000),
        ("Pöstler/in", 52000), ("Kurier/in", 46000), ("Staplerfahrer/in", 52000), ("Taxifahrer/in", 46000),
        ("Teamleiter/in Logistik", 75000), ("Teamleiter/in Lager", 70000), ("Teamleiter/in Disposition", 82000),
    ],
    "Gesundheit": [
        ("Pflegefachperson", 72000), ("Fachperson Gesundheit (FaGe)", 56000), ("Pflegehelfer/in", 46000),
        ("Stationsleiter/in", 105000), ("Assistenzarzt/Assistenzärztin", 95000),
        ("Oberarzt/Oberärztin", 140000), ("Hausarzt/Hausärztin", 160000), ("Zahnarzt/Zahnärztin", 150000),
        ("Dentalassistent/in", 50000), ("Dentalhygieniker/in", 78000),
        ("Medizinische Praxisassistent/in (MPA)", 54000), ("Physiotherapeut/in", 70000),
        ("Ergotherapeut/in", 70000), ("Apotheker/in", 105000), ("Fachperson Apotheke", 50000),
        ("Hebamme", 78000), ("Rettungssanitäter/in", 80000), ("Psychologe/in", 95000),
        ("Biomedizinische Analytiker/in", 70000), ("Fachperson Operationstechnik", 72000),
        ("Radiologiefachperson", 75000), ("Optiker/in", 60000), ("Ernährungsberater/in", 72000),
        ("Logopäde/Logopädin", 85000), ("Fachperson Langzeitpflege", 54000),
        ("Teamleiter/in Pflege", 90000), ("Teamleiter/in Therapie", 90000),
    ],
    "Bildung und Soziales": [
        ("Kindergartenlehrperson", 82000), ("Primarlehrer/in", 88000), ("Lehrperson Sekundarstufe", 98000),
        ("Gymnasiallehrer/in", 115000), ("Berufsschullehrer/in", 110000), ("Dozent/in Fachhochschule", 120000),
        ("Schulleiter/in", 140000), ("Heilpädagoge/Heilpädagogin", 100000),
        ("Fachperson Betreuung Kinder (FaBe)", 52000), ("Fachperson Betreuung Betagte", 54000),
        ("Kita Leiter/in", 75000), ("Sozialarbeiter/in", 85000), ("Sozialpädagoge/Sozialpädagogin", 82000),
        ("Berufsberater/in", 95000), ("Klassenassistent/in", 48000), ("Jugendarbeiter/in", 72000),
        ("Teamleiter/in Sozialdienst", 100000), ("Teamleiter/in Betreuung", 78000),
    ],
    "Gastronomie und Tourismus": [
        ("Koch/Köchin", 52000), ("Küchenchef/in", 72000), ("Servicefachangestellte/r", 48000),
        ("Barkeeper/in", 48000), ("Restaurantleiter/in", 68000), ("Hotelfachmann/Hotelfachfrau", 50000),
        ("Rezeptionist/in", 52000), ("Hotelmanager/in", 100000), ("Reiseberater/in", 56000),
        ("Bäcker/in Konditor/in", 52000), ("Metzger/in", 55000), ("Fachmann/Fachfrau Systemgastronomie", 50000),
        ("Küchenhilfe", 44000), ("Confiseur/in", 52000),
        ("Teamleiter/in Service", 60000), ("Chef de Partie", 56000),
    ],
    "Banken und Versicherungen": [
        ("Kundenberater/in Bank", 80000), ("Private Banker", 130000), ("Kreditspezialist/in", 95000),
        ("Compliance Officer", 115000), ("Risk Manager/in", 120000), ("Finanzanalyst/in", 110000),
        ("Portfolio Manager/in", 140000), ("Versicherungsberater/in", 75000), ("Schadeninspektor/in", 85000),
        ("Underwriter/in", 100000), ("Aktuar/in", 120000), ("Sachbearbeiter/in Versicherung", 68000),
        ("Sachbearbeiter/in Bank", 70000), ("Hypothekarberater/in", 95000), ("Finanzplaner/in", 100000),
        ("Teamleiter/in Bank", 115000), ("Teamleiter/in Versicherung", 105000),
    ],
    "Öffentliche Verwaltung": [
        ("Verwaltungsangestellte/r", 66000), ("Gemeindeschreiber/in", 105000), ("Polizist/in", 82000),
        ("Fachspezialist/in Zoll und Grenzsicherheit", 80000), ("Berufsfeuerwehrmann/frau", 80000),
        ("Steuerkommissär/in", 85000), ("Sachbearbeiter/in Sozialversicherung", 68000),
        ("Berufsmilitär", 80000), ("Sachbearbeiter/in Einwohnerdienste", 64000), ("Richter/in", 160000),
        ("Teamleiter/in Verwaltung", 100000), ("Abteilungsleiter/in Verwaltung", 125000),
    ],
    "Kunst, Medien und Design": [
        ("Grafiker/in", 62000), ("Polygraf/in", 56000), ("Fotograf/in", 56000), ("Journalist/in", 80000),
        ("Redaktor/in", 82000), ("Videoproduzent/in", 68000), ("Texter/in", 75000), ("Innenarchitekt/in", 70000),
        ("Art Director", 100000), ("Musiklehrer/in", 85000),
    ],
    "Beauty und Fitness": [
        ("Coiffeur/Coiffeuse", 46000), ("Kosmetiker/in", 46000), ("Podologe/Podologin", 54000),
        ("Fitnesstrainer/in", 52000), ("Masseur/in", 54000), ("Nageldesigner/in", 44000),
    ],
    "Landwirtschaft und Umwelt": [
        ("Landwirt/in", 50000), ("Gärtner/in", 52000), ("Florist/in", 46000), ("Forstwart/in", 58000),
        ("Tierpfleger/in", 50000), ("Tiermedizinische Praxisassistent/in", 50000),
        ("Tierarzt/Tierärztin", 90000), ("Umweltingenieur/in", 85000), ("Winzer/in", 52000),
    ],
    "Energie": [
        ("Netzelektriker/in", 62000), ("Solarinstallateur/in", 58000), ("Energieberater/in", 80000),
        ("Energieingenieur/in", 92000), ("Kraftwerksoperateur/in", 72000),
    ],
    "Sicherheit und Reinigung": [
        ("Sicherheitsmitarbeiter/in", 56000), ("Reinigungsfachkraft", 44000), ("Hauswart/in", 58000),
        ("Fachmann/Fachfrau Betriebsunterhalt", 56000), ("Leiter/in Facility Management", 95000),
        ("Teamleiter/in Reinigung", 62000), ("Teamleiter/in Sicherheit", 72000),
    ],
}

# Schneller Zugriff: Beruf -> (Branche, Basislohn)
BERUF_INFO = {beruf: (branche, lohn) for branche, liste in BERUFE.items() for beruf, lohn in liste}
ALLE_BERUFE = sorted(BERUF_INFO, key=str.casefold)
BRANCHEN = list(BERUFE)
