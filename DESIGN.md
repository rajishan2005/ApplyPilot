# ApplyPilot Design System

## 1. Visual theme & atmosphere
A considered student-facing research workspace: editorial clarity, quiet confidence, precise hierarchy. Avoid generic AI tropes. The interface should feel closer to a modern research tool than a chatbot landing page.

## 2. Colour palette & roles
Retain existing project CSS tokens as the source of truth. Use deep ink for the application shell, warm near-white surfaces for reading areas, muted slate for secondary metadata, and one restrained teal accent for primary actions. Amber is reserved for caution; red for material risk signals. Never use colour alone to communicate status.

## 3. Typography rules
Use the existing DM Sans / Space Grotesk pairing. Display headings are compact and human; body copy prioritizes readability. Metadata remains legible and never drops below 11px on desktop or 12px on mobile.

## 4. Component stylings
Opportunity cards foreground title, organizer, source type, deadline and evidence confidence. Tags are quiet and semantic. Buttons have clear hover, focus, disabled and loading states. Risk labels always include explanatory text.

## 5. Layout principles
Desktop content max-width around 1440px with a stable navigation rail and generous page gutters. Opportunity results use a responsive grid. Search controls remain visually dominant. On mobile, navigation collapses and cards become a single column.

## 6. Depth & elevation
Prefer subtle borders and tonal separation over stacked shadows or glass effects. Dialogs use a single elevation layer and clear focus management.

## 7. Animation & interaction
Use short 140–220ms transitions for hover, disclosure and modal states. Loading states communicate actual work. Respect `prefers-reduced-motion`. No decorative looping animations that compete with opportunity data.

## 8. Do's and don'ts
- Do show original source links beside extracted claims.
- Do distinguish extracted facts from unknowns.
- Do show last-checked timestamps.
- Do explain each ScamShield signal.
- Do preserve explicit user approval for consequential actions.
- Don't invent ratings, organizer verification or deadline dates.
- Don't label an opportunity safe based only on HTTPS.
- Don't use fake counters or sample listings in live mode.
- Don't auto-submit applications.
- Don't use generic AI sparkle gradients as decoration.

## 9. Responsive behaviour
At 1100px collapse secondary panels; at 760px use a single-column layout and compact navigation. Keep tap targets at least 44px. Search and filters wrap naturally. Dialogs fit within viewport height and scroll internally.
