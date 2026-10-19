# Business-Website auf Basis von Cms.Idseefeld.Web aufbauen (Umbraco, parallel zur Privatseite)

## Kontext aus Analyse

- Projekt: `latest\Cms.Idseefeld.Web` (Umbraco CMS 18.2.2, .NET 10, Razor-Views), Core-Logik in `latest\Cms.Idseefeld.Core`.
- Bestehende Doctypes/Views: `IdsRootPage`, `IdsMaster.cshtml` (globales Layout), `IdsStandardPage` → `IdsStandard.cshtml` (BlockGrid-basierte Inhaltsseite), `idsBlogPage`/`idsBlogGridPage`/`idsBlogsOverviewPage` (Blog), `ContactFormPage.cshtml` + `Views/Partials/ContactFormView.cshtml` + `ContactFormController` (Kontaktformular mit Validierung, DSGVO-Consent-Checkbox, Session-basiertem Anti-Spam-Timing).
- `IdsMaster.cshtml` enthält bereits eine `siteName`-Weiche (`if (siteName == "iDSeefeld")`) für site-spezifische Assets (z.B. Google Font). Dieses Pattern wird für die Business-Trennung wiederverwendet.
- Es existiert **kein** Buchungs-/Terminsystem im Code. `SystemNetMailService` in Core ist aktuell per `<Compile Remove>` deaktiviert. Die Mailversand-Anbindung muss geprüft/reaktiviert werden, falls Buchungsbestätigungen per Mail nötig sind.
- uSync wird zur Content-/Doctype-Synchronisierung genutzt. Neue Doctypes sollten nach Anlage im Backoffice über uSync exportiert werden, damit sie versioniert im Repo landen (`uSync`-Ordner).
- Mehrsprachigkeit: aktuell nur Deutsch (Dictionary-Werte), kein vollwertiges i18n-Routing. Wird in diesem Schritt nicht ausgebaut.

## Entscheidungen aus Rückfragen

- Art des Business: Dienstleistung mit Terminbuchung.
- Die bestehende Privatseite (Blog, Mastodon) bleibt unverändert; der Business-Bereich wird als eigener Zweig/eigene Seiten ergänzt (kein Rebranding der gesamten Site).
- Kernfeature: Buchungs-/Terminsystem.
- Content (Leistungen, Preise, Über-mich-Text) muss komplett neu erstellt werden. Platzhaltertexte im Code, redaktionelle Befüllung später über das Umbraco-Backoffice.

## Offene technische Entscheidung

Für die Terminbuchung gibt es keine Bestandslösung. Empfehlung: **Embed-Lösung** (z.B. Cal.com oder Calendly iframe/Script-Embed) statt eigener Buchungslogik mit Datenbank/Konflikterkennung. Umsetzung als Partial `BookingWidget.cshtml`, austauschbar über eine Umbraco-Property (URL/Embed-Code), damit der Anbieter ohne Code-Änderung wechselbar ist.

## Risiken

- Neue Doctypes erfordern Anlage im Umbraco-Backoffice (nicht rein code-basiert).
- Mailversand (`SystemNetMailService`) ist deaktiviert. Für Buchungsbestätigungen per Mail muss er separat reaktiviert/geprüft werden (SMTP-Secrets liegen in User Secrets).
- Ohne redaktionellen Content wird zunächst mit Platzhaltertexten gearbeitet.

## Steps

1. Business-Rubrik anlegen: im Umbraco-Backoffice einen neuen Content-Knoten (z.B. "Business") unterhalb der Root anlegen, der die Business-Seiten bündelt, analog zur Blog-Sektion.
2. Doctype `IdsBusinessLandingPage` erstellen: Properties für Hero-Text, Leistungsübersicht (BlockGrid wie bei `IdsStandardPage`), CTA zur Buchungsseite; View `Views/IdsBusinessLandingPage.cshtml` nach Vorbild von `IdsStandard.cshtml` (Layout = `IdsMaster.cshtml`).
3. Doctype `IdsServicePage` für einzelne Leistungen/Preise erstellen: Titel, Beschreibung, Preis, Dauer, Buchungs-Link/CTA; View `Views/IdsServicePage.cshtml`.
4. Property `BookingEmbedUrl` (Textstring) ergänzen, z.B. auf `IdsBusinessLandingPage` oder global auf `IdsRootPage`, damit die Embed-URL redaktionell pflegbar ist.
5. Partial `Views/Partials/ids/BookingWidget.cshtml` erstellen: rendert iframe/Script-Embed basierend auf `BookingEmbedUrl`, mit Lazy-Loading und Platzhalter-Hinweis, falls URL nicht gesetzt.
6. Navigation erweitern: `Views/Partials/ids/ids-TopNavi.cshtml` um einen Business-Menüpunkt ergänzen (nur anzeigen, wenn Business-Knoten existiert/publiziert ist).
7. `IdsMaster.cshtml` um Business-Branding-Zweig ergänzen: zusätzlich zum `if (siteName == "iDSeefeld")`-Muster einen Zweig für den Business-Site-Namen (z.B. eigener Favicon/Title-Zusatz), ohne die Mastodon/OpenGraph-Logik der Privatseite zu ändern.
8. Platzhalter-Content für Leistungen/Preise/Über-mich in `latest/Cms.Idseefeld.Web/BUSINESS-CONTENT-TODO.md` festhalten (zu befüllende Felder).
9. Kontaktformular für Business wiederverwenden: prüfen, ob `ContactFormController`/`ContactFormView.cshtml` einen zweiten Zweck (z.B. "Anfrage") per Hidden-Field/Betreff-Vorbelegung unterscheiden soll.
10. uSync-Export durchführen, damit Schema-Änderungen im Repo (`uSync`-Ordner) versioniert werden.
11. Lokal bauen und smoke-testen: `dotnet build` auf `Cms.Idseefeld.sln`, Website starten, Business-Seiten, Booking-Partial und Navigation prüfen.
