# ✈️ ApplyPilot

**Discover smarter. Verify before you apply.**

ApplyPilot is a student-focused opportunity assistant designed to make finding and evaluating hackathons, internships, scholarships, and other opportunities less time-consuming.

Instead of jumping between multiple websites and manually checking every listing, students can use one simple workflow to discover relevant opportunities, compare them, review potential risks, and keep track of applications.

---

## 🔎 The workflow

```text
Discover  →  Shortlist  →  Compare  →  ScamShield  →  Apply & Track
```

| Step | What it does |
| --- | --- |
| **Discover** | Find opportunities from different sources and narrow them down with useful filters. |
| **Shortlist** | Save opportunities that are relevant to your interests and goals. |
| **Compare** | Review two opportunities side by side, including details such as eligibility, fees, deadlines, and location when available. |
| **ScamShield** | Review the source and highlight warning signs or details that could not be verified. |
| **Apply & Track** | Keep a record of opportunities you're applying to and follow their application status. |

## ✨ Why ApplyPilot?

- **Less searching:** bring opportunity discovery into one workflow.
- **Better decisions:** compare important details before spending time on an application.
- **More awareness:** look for suspicious signals and distinguish verified details from unknowns.
- **Stay organised:** keep shortlisted opportunities and application progress together.

## 🧩 Technology

The project is designed around a lightweight web application and AI-assisted services.

| Layer | Technology |
| --- | --- |
| Frontend | React (project design) |
| Backend | Python / FastAPI (project design) |
| AI assistance | Google Gemini and OpenAI |
| Web discovery | Tavily |
| Voice experience | ElevenLabs |
| Optional file backup | AWS S3 |
| Data storage | SQLite |

*Integrations and components may vary by demo build. Optional services such as AWS S3 require separate configuration.*

## 🛡️ Safety and transparency

ApplyPilot is intended to help students make more informed decisions, not to guarantee that an opportunity is legitimate. A warning or a missing detail should be treated as a prompt to verify information directly with the organiser. Users remain in control of their applications.

## 🚧 Project status

ApplyPilot is being prepared as a hackathon demo. This repository currently contains the deployment scaffold and project documentation; the application source files and a live deployment still need to be added.

## ☁️ Deployment

A Render Blueprint is included in [`render.yaml`](./render.yaml). Once the application source is added, configure the required API keys as environment variables in the Render dashboard.

**Never commit your real `.env` file, API keys, or local database.** Use [`.env.example`](./.env.example) as a reference for variable names.

## 🗺️ Next steps

- [ ] Add the application source code
- [ ] Verify the local setup and API integrations
- [ ] Deploy the demo on Render
- [ ] Add screenshots and a short demo video
- [ ] Document setup instructions for contributors

## 🤝 Contributions

Ideas, bug reports, and suggestions are welcome. If you find an issue, please open a GitHub Issue with steps to reproduce it.

---

<p align="center">
  <strong>ApplyPilot</strong><br/>
  <em>Find opportunities. Make informed choices. Keep moving forward.</em>
</p>
