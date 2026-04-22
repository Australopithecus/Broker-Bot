# Day Overview App - MVP Spec

## Summary
A daily ~15-minute audio briefing that is ready by 5:00 a.m. on iPhone. The briefing combines your local calendar, weather, news, an ICU trial summary, a historical fact, and a 30-minute workout recommendation with the best available time slot.

## Primary Goals
- Create a predictable morning routine: one tap to listen to a fresh overview.
- Keep private calendar data on-device.
- Make the content concise and trustworthy.

## Non-Goals (for MVP)
- Android or Apple Watch support.
- Full offline mode beyond cached audio for the current day.
- Complex personalization models.

## User Experience (MVP)
- At 5:00 a.m., the app prepares a new briefing.
- The home screen shows a “Today’s Overview” card with a Play button, total duration, and last generated time.
- A local notification can alert you when the briefing is ready.
- The app can regenerate on demand.

## Content Sections and Behavior
1. Calendar summary
- Source: iPhone Calendar via EventKit.
- Content: today’s events with start times and locations if available.
- Privacy: calendar data never leaves the phone.

2. Weather overview
- Source: weather API (server or device).
- Content: high/low, precipitation chance, and a short sentence on what to expect.

3. News brief
- Source: backend pulls from a small set of reputable outlets.
- Content: 3 to 5 top stories, each 1 to 2 sentences.
- Model output is summarized once per morning and cached.

4. Workout recommendation
- Duration: 30 minutes.
- Type: alternating running and weight lifting day by day.
- Time suggestion: choose first 30-minute free slot within a preferred window.

5. ICU trial summary
- Source: backend uses a curated list of landmark and recent trials.
- Content: 3 to 5 sentences including the clinical question, population, and primary outcome.
- Mix rule: rotate between landmark and recent trials.

6. Historical fact
- Source: backend from a vetted dataset.
- Content: 1 to 2 sentences.

## Workout Scheduling Logic (MVP)
- Preferred windows: 5:30 a.m. to 9:00 a.m., then 11:30 a.m. to 2:00 p.m., then 5:00 p.m. to 8:00 p.m.
- Select the earliest 30-minute free slot from those windows based on today’s calendar.
- If no slot exists, recommend a short walk and explain why.

## Scheduling Constraints (Important iOS Detail)
- iOS background tasks are not guaranteed to run at exactly 5:00 a.m.
- Strategy: schedule a background refresh around 5:00 a.m. and also schedule a local notification at 5:00 a.m. that opens the app and triggers generation if needed.
- The briefing is generated the first time either background refresh succeeds or the app is opened after 5:00 a.m.

## Architecture

### iPhone App (Swift/SwiftUI)
- Permissions: Calendar access (EventKit), Notifications.
- Local data: cached script and audio for “today.”
- Text-to-speech: AVSpeechSynthesizer for on-device audio.

### Backend (FastAPI recommended)
- Runs a daily job at 4:30 a.m. to fetch and summarize content.
- Stores daily content in a simple database or JSON blob.
- Exposes one endpoint for the app to fetch the day’s content.

### Data Flow
1. Backend generates daily content: news, ICU trial, historical fact.
2. App pulls daily content at or after 5:00 a.m.
3. App reads local calendar and weather, builds a final script, and speaks it.

## Data Model (Simple)
- `DailyContent` with fields: date, news_items[], icu_trial_summary, historical_fact.
- `NewsItem` with fields: headline, brief_summary, source_name.

## Privacy
- Calendar data stays on the phone.
- Backend does not receive personal schedule data.
- Minimal analytics, if any.

## Open Choices (We can decide next)
- Weather API choice.
- News source set and summarization model.
- ICU trial source list and how to keep it updated.

## MVP Build Plan
1. iOS prototype: calendar access, local playback, static content.
2. Backend MVP: daily content generation endpoints.
3. Integrate: fetch daily content, merge with calendar and weather, generate final script.
4. Reliability: caching, retry rules, and notification when ready.

## Acceptance Criteria
- By 5:00 a.m., a new daily overview is ready or generated on first app open.
- Calendar summary is correct for the day.
- Workout suggestion includes a specific time slot or a fallback.
- Audio length is 12 to 15 minutes.

