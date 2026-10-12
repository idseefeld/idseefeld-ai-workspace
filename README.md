# Claude Starter Workspace

Ein fertiges Workspace-Template für Claude Code. Gibt Claude strukturierten Kontext, damit er versteht wer du bist und woran du arbeitest — über Sessions hinweg.

## Setup

1. Fülle die Dateien in `context/` mit deinen Informationen aus:
   - `business-info.md` — dein Unternehmen oder Business
   - `personal-info.md` — deine Rolle und Verantwortlichkeiten
   - `strategy.md` — deine aktuellen Prioritäten und Ziele
   - `current-data.md` — wichtige Kennzahlen und aktueller Stand
2. Öffne diesen Ordner in Claude Code
3. Starte jede Session mit `/prime`

## Struktur

```
├── CLAUDE.md              # Anweisungen für Claude (wird automatisch geladen)
├── .claude/commands/
│   └── prime.md           # /prime Befehl — Session-Initialisierung
├── context/               # Dein Hintergrundkontext (hier ausfüllen)
├── outputs/               # Arbeitsergebnisse von Claude
└── reference/             # Beispiel-Outputs, Inputmaterial, Vorlagen
```

## Nutzung

Starte jede Session mit `/prime`. Claude liest deine Kontextdateien und bestätigt sein Verständnis bevor er arbeitet.

Lege Material in `reference/` ab, das Claude als Input nutzen soll — Beispiel-Outputs, Dokumente zur Analyse, Vorlagen oder Muster. Claudes Arbeitsergebnisse landen in `outputs/`.
