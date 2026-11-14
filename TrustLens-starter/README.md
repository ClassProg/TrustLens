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
2. Integrated Gradients `pipeline/explain.py`
3. Quantus evaluation in `pipeline/evaluate.py` (precomputed first)
4. Verified RIGA grading lookup in `pipeline/disagreement.py`
5. Real model and integration tests, then deployment hardening

## file-by-file notes 



## 1. Frontend — React + Vite

**Purpose:** React builds the interface and Vite runs the
development server and creates production builds.

### Main Files

- `frontend/index.html`
  - Main HTML file containing the React root.

- `frontend/package.json`
  - Frontend dependencies and npm scripts.
  - Includes React, Vite, React Router, and testing tools.

- `frontend/vite.config.js`
  - Configures Vite and Vitest.
  - Proxies `/api` requests to the Flask backend.

- `frontend/src/main.jsx`
  - Starts the React application.
  - Defines routes `/` and `/app`.

- `frontend/src/App.jsx`
  - Main analysis dashboard.
  - Manages uploaded images, model selection, results,
    loading states, and errors.
  - Calls the backend API.

- `frontend/src/App.css`
  - Main frontend styling.
  - Includes responsive layouts and animations.

### Components

- `components/LandingPage.jsx`
  - Public landing page.
  - Explains TrustLens and links to `/app`.
  - Includes scrolling animations.

- `components/UploadPanel.jsx`
  - Image upload, model selection, and Analyze button.

- `components/PredictionResult.jsx`
  - Displays the image, prediction, and confidence.

- `components/ExplanationPanel.jsx`
  - Displays XAI heatmaps when available.

- `components/QuantusReport.jsx`
  - Displays faithfulness, robustness, and localization.

- `components/ExpertDisagreement.jsx`
  - Displays verified RIGA expert disagreement data.

- `components/Header.jsx`
  - Legacy header component, currently unused.

### API Communication

- `frontend/src/services/api.js`
  - `getHealth()` → checks backend status.
  - `getModels()` → retrieves available models.
  - `analyze(file, model)` → sends an image to Flask.
  - `parse()` → handles responses and errors.

---

## 2. Backend — Python + Flask

**Purpose:** Flask handles API requests, image validation,
and the future machine learning pipeline.

### Main Files

- `backend/app.py`
  - Creates the Flask application.
  - Defines API routes.
  - Validates requests and returns JSON responses.
  - Currently returns simulated analysis results.

- `backend/config.py`
  - Stores backend configuration.
  - Includes `MOCK_MODE`.

- `backend/requirements.txt`
  - Runtime Python dependencies.
  - Flask, Flask-CORS, and Pillow.

- `backend/requirements-dev.txt`
  - Development dependencies, including pytest.

### AI Pipeline

- `backend/pipeline/__init__.py`
  - Makes the pipeline a Python package.

- `backend/pipeline/preprocess.py`
  - `validate_image()`
  - Checks file size, type, and image content.
  - Converts valid images to RGB.

- `backend/pipeline/classify.py`
  - `predict()`
  - Placeholder for one trained CNN model.
  - Will return glaucoma predictions and confidence.

- `backend/pipeline/explain.py`
  - `generate_explanations()`
  - Placeholder for Grad-CAM, Integrated Gradients,
    and LIME explanations.

- `backend/pipeline/evaluate.py`
  - `evaluate_explanations()`
  - Placeholder for Quantus evaluation metrics.

- `backend/pipeline/disagreement.py`
  - `get_disagreement()`
  - Placeholder for verified RIGA grader analysis.
  - Currently returns unavailable results.

### Other Files

- `backend/results/precomputed.json`
  - Reserved for verified precomputed results.

- `models/`
  - Reserved for trained model checkpoints.

- `data/`
  - Reserved for REFUGE and RIGA datasets.

---

## 3. API Routes

**Purpose:** Connect the React dashboard to Flask.

### GET /api/health

Function: `health()`

- Checks whether Flask is running.
- Returns server and mock-mode status.

Response:
`{status, model_loaded, mock_mode}`

### GET /api/models

Function: `models()`

- Returns available model choices.
- MVP will use one trained CNN model.

Response:
`[{id, name}, ...]`

### GET /api/demo-images

Function: `demo_images()`

- Reserved for approved sample images.
- Currently returns an empty list.

Response:
`[]`

### POST /api/analyze

Function: `analyze()`

- Accepts PNG/JPG image uploads.
- Accepts the selected model.
- Validates the uploaded image.
- Currently returns mock analysis results.

Request:
- `file`: uploaded image
- `model`: model identifier

Response:
- `prediction`
- `explanations`
- `quantus`
- `expert_disagreement`
- `timing_ms`
- `demo_mode`

### API Error Handling

- Invalid requests return an HTTP error status.
- Error responses contain:
  `{error: "plain-language message"}`
- HTTP 413 handles files that exceed the upload limit.

### Data Flow

Browser
  → React Dashboard
  → POST /api/analyze
  → Flask
  → Image Preprocessing
  → CNN Classification
  → XAI Explanations
  → Quantus Evaluation
  → Optional RIGA Expert Disagreement
  → JSON Response
  → React Dashboard

**Note:** The real AI pipeline is not integrated yet.

---



## 4. Automated Testing

**Purpose:** Automatically check functionality and catch
errors after code changes.

### Backend — pytest

**Status: PASSED (November 14, 2026)**

File: `backend/tests/test_api.py`

- All 8 backend tests passed.
- Execution time: 0.28 seconds.
- No failed tests.

Command (from `src/backend/`):
```bash
PYTHONPATH=. python3 -m pytest -q tests
```

Result:
```text
........                 [100%]
8 passed in 0.28s
```

Tests cover:
- Backend health endpoint.
- Available model list.
- Missing image uploads.
- Invalid or unsupported images.
- Model selection validation.
- Mock API response structure.

**Note:** Tests ran using system Python 3.13 because
the project virtual environment was not found.
Set up `.venv` for consistent development.

### Frontend — Vitest + Testing Library

**Status: NOT YET VERIFIED**

Files:
- `frontend/src/test/setup.js`
- `frontend/src/components/LandingPage.test.jsx`

Run from `src/frontend/`:
```bash
npm test -- --run
npm run build
```

TODO:
- [ ] Run frontend automated tests.
- [ ] Verify production build succeeds.
- [ ] Add dashboard upload and error-state tests.

### GitHub Actions — CI

**Status: NOT YET VERIFIED**

File: `.github/workflows/tests.yml`

TODO:
- [ ] Confirm workflow runs on GitHub.
- [ ] Confirm backend tests pass in CI.
- [ ] Confirm frontend tests pass in CI.
- [ ] Confirm frontend production build passes.

### Future AI Tests

- [ ] Test trained CNN model loading.
- [ ] Test REFUGE/RIGA preprocessing.
- [ ] Test real model inference.
- [ ] Test XAI explanation generation.
- [ ] Test Quantus evaluation output.
- [ ] Test RIGA expert disagreement lookup.
- [ ] Add end-to-end browser tests.

### Testing Progress

- [x] Backend automated tests — 8/8 passed.
- [ ] Frontend automated tests.
- [ ] Frontend production build.
- [ ] GitHub Actions CI.
- [ ] Full MVP integration tests.

**Important:** Passing the backend tests verifies the
existing test cases, not model accuracy or the complete
AI pipeline.
