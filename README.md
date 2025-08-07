# Travel‑Recommender

A full‑stack demo that turns a short trip brief into **ranked destination ideas** (0‑100 satisfaction score):

```
Form  ➜  FastAPI  ➜  Cloudflare Workers AI (Llama‑3‑8B)  ➜  Rule‑based scorer  ➜  JSON / UI
```

If the LLM is offline or the free quota is gone, the API gracefully falls back to a local rule‑engine so the UX never breaks.

---

## ✨ Key Features

| ✔ | Feature                                                                   |
| - | ------------------------------------------------------------------------- |
| ✅ | End‑to‑end flow: **RN Web UI → REST → AI → results**                      |
| ✅ | Thoughtful prompt + robust JSON/regex parsing                             |
| ✅ | Offline fallback with identical response schema                           |
| ✅ | Tiny "ML" scorer (`backend/model.py`) – pluggable with real sklearn later |
| ✅ | Single‑command dev setup, CORS enabled, `.env` driven                     |

---

## 🛠 Tech Stack

* **Backend** – FastAPI 0.116 · Pydantic v2 · Uvicorn hot‑reload
* **AI** – Cloudflare Workers AI, Llama‑3‑8B (100k free tokens/day)
  *(swap to HF / OpenAI by changing one helper)*
* **Scoring** – hand‑tuned rule model (40/35/25 weights)
* **Frontend** – Expo / React‑Native Web (slider, picker, responsive)

---

## 🚀 Quick Start

### 1  Clone & install

```bash
# backend + frontend in one repo
$ git clone https://github.com/<you>/travel-recommender.git
$ cd travel-recommender

# Python env
$ python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
$ pip install -r requirements.txt

# Frontend deps
$ cd frontend && npm install && cd ..
```

### 2  Create `.env`

```dotenv
# .env (project root)
CLOUDFLARE_ACCOUNT_ID=<your CF account id>
CLOUDFLARE_AI_TOKEN=<Bearer token>
```

* **Find account ID** – top right of Cloudflare dash → *Profile*.
* **Create AI token** – Dash → *AI* → *API Tokens* → *Create* → copy.

> Skip the vars to immediately see the **local fallback** in action.

### 3  Run the backend

```bash
$ uvicorn main:app --reload   # http://127.0.0.1:8000/docs
```

### 4  Hit the API

```bash
curl -X POST http://127.0.0.1:8000/api/recommendations \ \
     -H "Content-Type: application/json" \
     -d '{"climate":"cold","duration":7,"budget":2500,"interests":["culture","adventure"]}' | jq
```

### 5  Launch the UI (optional)

```bash
$ cd frontend && npm start   # press "w" for web preview
```

The pink *Get Recommendations* button calls the same endpoint.

---

## 🧩 Code Structure

```
travel-recommender/
├── backend/
│   ├── model.py            # tiny rule‑based scorer
│   ├── travel.py           # Cloudflare LLM + fallback router
│   ├── …
├── frontend/               # Expo RN web app
├── sample_output.json      # static seed data
├── requirements.txt
└── README.md
```

---

## 🔄 Extending

| Idea                 | Where                                          |
| -------------------- | ---------------------------------------------- |
| Swap to OpenAI or HF | `backend/travel.py::_call_cloudflare`          |
| Train real model     | drop sklearn `pickle` into `backend/model.py`  |
| Add auth             | wrap FastAPI dependency, CORS already open     |

---

## 📝 License

MIT – use freely, attribution appreciated.
