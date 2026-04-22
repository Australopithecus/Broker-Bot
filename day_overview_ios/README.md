# ICU Clinical Trials iOS App (SwiftUI)

A full Xcode project is included.

Open:
- `DayOverview.xcodeproj`

## What the app does
- Shows a rotating **Trial of the Day**.
- Provides concise, easy-to-read summaries for major landmark and recent ICU trials.
- Supports search by trial name and topic (for example: ARDS, Sepsis, Septic Shock, Fluids).
- Includes citation links to PubMed for further reading.
- Supports **Favorites** so you can save frequently referenced trials.
- Uses a modern, Apple-inspired light visual style with card-based reading.
- Adds an **Evidence Strength** badge (`Practice-Changing`, `Neutral`, `Harm Signal`) on trial cards and detail pages.
- Includes a structured **Critical Appraisal** section for each trial (clinical question, background, design, key results, strengths, weaknesses, and practical bottom line).

## Run in Xcode
1. Open `DayOverview.xcodeproj`.
2. Select a signing team for the app target.
3. Build and run on iPhone simulator or device.

## Notes
- Trial content is bundled locally in the app (no backend required).
- If you want to add or edit trials, update `DayOverview/Models.swift` in the `ICUTrialLibrary.allTrials` array.
- Favorite usage: tap the star on a trial detail page or swipe left on a trial row and tap Favorite.
- The trial library has been expanded with additional ARDS, sepsis/septic shock, fluid, transfusion, AKI/RRT, and COVID-19 ICU trials.
- Recent additions were curated using the Critical Care Reviews Hot Trials feed: `https://criticalcarereviews.com/latest-evidence/hot-trials`.
