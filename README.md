# Auto Kids YouTube

Automated production pipeline for original Hindi children's videos.

## Pipeline

Trend research -> content planning -> story -> characters/world -> scene plan -> video -> Hindi voice -> music/SFX -> thumbnail -> safety/quality review -> Shorts/long video packaging -> YouTube publishing -> analytics optimization.

## Safety and originality

The system is designed to create original stories and visuals rather than copy or re-upload other creators' videos. Trend research informs topics and formats; it does not authorize copying copyrighted characters, scripts, footage, or audio.

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `/health` and POST `/pipeline/run`.

## Provider adapters

External providers will be connected through isolated adapters. Secrets belong in environment variables, never in Git.
