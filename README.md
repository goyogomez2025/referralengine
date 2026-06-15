# Yirra Referral Engine

MVP para crear una máquina interna de prospección NDIS para Yirra Care.

El sistema no envía emails automáticos por defecto. Crea contactos, cualifica, redacta emails personalizados y crea borradores en Gmail para revisión humana.

## Workers incluidos

1. `find_contacts` — busca webs/contactos de Support Coordinators, OTs, Recovery Coaches y Plan Managers.
2. `scrape_emails` — visita webs, extrae emails, teléfonos y texto relevante.
3. `qualify_contacts` — clasifica contacto y decide si merece outreach.
4. `write_emails` — redacta emails personalizados con OpenAI o fallback template.
5. `create_gmail_drafts` — crea borradores en Gmail.
6. `export_contacts` — exporta CSV para revisar en Sheets.

## Instalación

```bash
cd yirra-referral-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y mete tu `OPENAI_API_KEY`.

## Inicializar DB

```bash
python -m app.main init-db
```

## Ejecutar pipeline MVP

```bash
python -m app.main run-campaign --campaign cleaning_sc_brisbane --query "NDIS support coordinator Brisbane email" --limit 20
```

## Crear drafts en Gmail

Primero descarga `client_secret.json` desde Google Cloud Console con Gmail API habilitada.

Luego:

```bash
python -m app.main create-drafts --limit 10
```

La primera vez abrirá OAuth en navegador y guardará `token.json`.

## Exportar CSV

```bash
python -m app.main export-contacts
python -m app.main export-emails
```

## Reglas de seguridad comercial

- No uses esto para spam masivo.
- Trabaja con volumen bajo: 10–30 drafts/día al principio.
- Revisa manualmente cada draft antes de enviar.
- Incluye identidad clara y opt-out.
- No uses scraping agresivo ni LinkedIn automático.
- Prioriza calidad: SCs y Recovery Coaches con fit real.

## Prioridad de campañas

1. NDIS Cleaning + Domestic Tasks — Support Coordinators.
2. Domestic Tasks + Laundry — Recovery Coaches.
3. Moving / Decluttering / Home Transition — SCs y Housing Providers.
4. Provider intro — Plan Managers, menor prioridad.

## Estructura

```text
yirra-referral-engine/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── workers/
│   ├── services/
│   └── utils/
├── prompts/
├── data/
├── exports/
└── docs/
```
