# TrustLens — Team explAIn

Research-only prototype: not for diagnosis. **The current API returns explicitly simulated results.** No trained model, Captum heatmap, or Quantus metric is integrated yet.

## Architecture
- `/` animated React landing page; `/app` research dashboard (React Router)
- Vite serves React during development and proxies `/api` to Flask
- Flask handles in-memory PNG/JPG validation and a mock analysis response
- `backend/pipeline/` contains integration placeholders for classification, explanations, Quantus, and RIGA agreement
- No login system or uploaded-image storage

## Start backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```

## Start frontend (second terminal)
```bash
cd frontend
npm install
npm run dev
```
Visit http://127.0.0.1:5173 for the landing page and http://127.0.0.1:5173/app for the dashboard.

## Automated tests
```bash
# From backend with virtual environment active
PYTHONPATH=. pytest -q tests
# From frontend
npm test
npm run build
```
GitHub Actions also runs these checks on pushes and pull requests.

## API contract
- `GET /api/health`: server/model readiness
- `GET /api/models`: available model choices
- `GET /api/demo-images`: future licensed sample images
- `POST /api/analyze`: multipart `file` + `model`; mock JSON currently

## Next integrations
1. Fine-tuned checkpoint loading and inference in `pipeline/classify.py`
2. Captum Grad-CAM, Integrated Gradients, LIME in `pipeline/explain.py`
3. Quantus evaluation in `pipeline/evaluate.py` (precomputed first)
4. Verified RIGA grading lookup in `pipeline/disagreement.py`
5. Real model and integration tests, then deployment hardening

For detailed file-by-file notes see `TrustLens_Development_Notes.docx` supplied alongside the starter archive.
