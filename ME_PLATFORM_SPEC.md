# Me Platform - Product and Technical Spec

## Why this document exists
This project can become much more than a "daily briefing" app. The underlying opportunity is a private personal data platform that collects information from multiple sources, organizes it into a consistent timeline, and then answers useful questions or makes suggestions.

The key recommendation is:

- Build the larger platform intentionally.
- Use the existing `Day Overview` work as the first vertical slice of that platform.

That approach gives us something useful early, without locking us into a narrow design.

## Product vision
Create a flexible personal assistant system that can:

- sync data from multiple personal sources
- answer questions in natural language
- generate proactive suggestions
- support multiple interfaces such as an iPhone app and WhatsApp
- preserve privacy and provide traceable answers

Examples:

- "What does my day look like tomorrow?"
- "When does my flight leave next week?"
- "Do I have time for a workout tomorrow morning?"
- "How has my sleep and exercise changed over the last two weeks?"
- "What are the top things I should know before clinic tomorrow?"

## Product principles

### 1. Local-first for sensitive data
Calendar and Apple health data are especially sensitive. The system should collect them on-device first, then only sync the minimum needed to a backend if remote access is desired.

### 2. Structured data before AI prose
The best answers should come from real data retrieval and rules first. The language model should mainly:

- interpret the question
- choose the right retrieval tools
- produce a readable response

This reduces hallucinations and makes answers more trustworthy.

### 3. Every answer should be explainable
If the system says your flight is at 6:15 p.m., it should be able to say where that came from:

- calendar event
- WhatsApp message
- imported itinerary
- travel confirmation note

### 4. Build one high-value workflow first
The first workflow should be the one that creates daily value with the fewest integration risks. In this project, that is the daily overview / planning assistant.

## Recommended build strategy

### Recommendation
Treat the platform as having 3 layers:

1. Ingestion layer
2. Knowledge layer
3. Experience layer

#### Ingestion layer
Connectors bring in raw data from sources.

#### Knowledge layer
Raw records are normalized into a common schema so the system can reason over them consistently.

#### Experience layer
Apps and chat interfaces ask questions, display summaries, and deliver recommendations.

## Phase structure

### Phase 1: Day Overview MVP
This is the best first product to build.

Why:

- it is immediately useful
- it uses relatively accessible data sources
- it tests the central architecture
- it creates a path to future query-based features

Phase 1 answers questions like:

- what is on my calendar today?
- what is tomorrow likely to look like?
- when is the best workout slot?
- what weather and major news should I know?

### Phase 2: Queryable personal assistant
After Phase 1 is stable, add a question-and-answer interface:

- iPhone app chat
- later, WhatsApp bot

This phase adds:

- "ask anything about my schedule"
- travel extraction
- event lookup
- trend summaries across health and calendar data

### Phase 3: Recommendation engine
After querying works reliably, add suggestions:

- workout timing recommendations
- recovery-aware exercise suggestions
- schedule-aware preparation prompts
- travel reminders

## Data sources

### Strong early sources

#### Calendar
Best early source. High value, relatively clean structure.

Useful fields:

- title
- start time
- end time
- location
- notes
- attendees
- time zone

#### Apple Watch / HealthKit
Also a strong early source.

Useful fields:

- workouts
- step count
- sleep
- heart rate
- resting heart rate
- HRV
- active energy

Important note:
Health data is sensitive and should be handled conservatively. Recommendations based on this data should be framed as wellness support, not medical advice.

#### Weather
Easy and high value.

Useful fields:

- hourly forecast
- daily forecast
- precipitation probability
- severe weather alerts

#### News
Reasonable to add early if source quality is curated.

Useful fields:

- headline
- source
- publish time
- short summary
- topic tag

### Medium-difficulty sources

#### WhatsApp as a chat interface
This is a good medium-term integration.

Use it for:

- asking the assistant questions
- receiving summaries or reminders

It is much cleaner as an interface than as a full historical personal-message ingestion source.

#### Travel documents
Useful and practical.

Potential inputs:

- calendar notes
- forwarded itinerary text
- email exports or pasted confirmation text

This may be a better early strategy than trying to fully ingest every message source.

### Hard / defer-for-now sources

#### Apple Messages / SMS / iMessage history
This is the riskiest early integration.

Why:

- Apple does not provide a straightforward supported API for full personal message history ingestion
- workarounds tend to be brittle, local-only, or operationally awkward

Recommendation:
Do not make this a core dependency of the MVP.

#### Full historical personal WhatsApp ingestion
Also messy as an early goal.

Recommendation:
Use WhatsApp first as a question interface, not as the main historical source of truth.

## System architecture

### 1. iPhone app
Primary responsibilities:

- obtain permissions
- read local calendar and HealthKit data
- cache recent content locally
- provide a native UI for daily overview and Q&A
- optionally push normalized data to backend

This should likely be a SwiftUI app.

### 2. Backend API
Primary responsibilities:

- receive synced data from the phone
- fetch weather and news
- normalize incoming records
- expose query endpoints
- run scheduled jobs
- manage audit logging

Suggested backend:

- Python with FastAPI

Reason:

- straightforward to build
- strong ecosystem for APIs, data processing, and LLM orchestration

### 3. Database
Use a relational database as the core system of record.

Suggested:

- Postgres

Optional:

- `pgvector` for semantic retrieval over long text such as notes, imported messages, or travel confirmations

### 4. LLM orchestration layer
Responsibilities:

- parse user intent
- route to the right retrieval logic
- summarize retrieved facts
- produce readable responses with source references

The model should not be the primary source of truth.

### 5. Interfaces
Recommended order:

1. native iPhone app
2. optional audio briefing
3. WhatsApp interface

## Canonical data model

The platform should normalize all sources into a small number of core tables or collections.

### Core entities

#### `sources`
Tracks each connector and its sync status.

Example fields:

- `id`
- `name`
- `type`
- `enabled`
- `last_success_at`
- `last_error`

#### `sync_runs`
Tracks each ingestion run.

Example fields:

- `id`
- `source_id`
- `started_at`
- `completed_at`
- `status`
- `records_seen`
- `records_written`
- `error_text`

#### `events`
Canonical calendar and itinerary-like items.

Example fields:

- `id`
- `source`
- `external_id`
- `title`
- `starts_at`
- `ends_at`
- `timezone`
- `location`
- `notes`
- `category`
- `raw_payload`

#### `workouts`
Structured fitness sessions.

Example fields:

- `id`
- `source`
- `external_id`
- `workout_type`
- `started_at`
- `ended_at`
- `duration_minutes`
- `energy_burned`
- `distance`
- `raw_payload`

#### `health_metrics`
Time-series health measurements.

Example fields:

- `id`
- `metric_type`
- `value`
- `unit`
- `observed_at`
- `source`

#### `messages`
Only for supported channels we explicitly choose to ingest.

Example fields:

- `id`
- `source`
- `conversation_id`
- `sender`
- `sent_at`
- `body`
- `attachments`
- `raw_payload`

#### `weather_snapshots`
Weather by place and time.

#### `news_items`
Curated news records.

#### `entities`
Named things mentioned across records.

Examples:

- people
- places
- airlines
- airports
- hospitals
- projects

#### `entity_links`
Connects entities back to events, messages, and documents.

#### `answer_logs`
Stores what was asked and what evidence was used.

This is useful for trust, debugging, and improvement.

## Retrieval patterns

### Question type: day overview
Question:
"What does my day look like tomorrow?"

Retrieval logic:

1. fetch tomorrow's calendar events
2. sort chronologically
3. estimate gaps and transitions
4. add weather relevant to the day
5. optionally add workout recommendation based on schedule and recovery
6. generate concise prose answer

### Question type: travel lookup
Question:
"When does my flight leave next week?"

Retrieval logic:

1. search future events for airline, airport, and flight-like patterns
2. scan notes or imported itineraries
3. rank candidates by date proximity and confidence
4. answer with source and confidence

### Question type: wellness recommendation
Question:
"When should I work out tomorrow?"

Retrieval logic:

1. inspect calendar gaps
2. inspect sleep and recent workout history
3. apply simple rules first
4. return a recommendation with rationale

Important note:
For the MVP, keep this recommendation engine rule-based rather than model-based.

## Privacy and safety design

### Privacy
- keep especially sensitive data local when possible
- encrypt data in transit and at rest
- store minimal raw payloads when possible
- make it easy to delete synced data

### Trust
- provide source references in responses
- show timestamps
- log which records supported an answer

### Safety
- avoid presenting fitness suggestions as medical advice
- avoid automated actions without confirmation
- do not silently write to calendar or send messages

Because you are a physician and may use this in high-stakes settings, explainability matters more than novelty.

## Why Day Overview should be the first product
This is the most important recommendation in the document.

Day Overview is not a side project. It is the ideal first vertical slice because it exercises:

- calendar ingestion
- weather ingestion
- news ingestion
- optional health-aware recommendation logic
- response generation
- user trust through concise summaries

If that workflow works well, the same platform can later answer ad hoc questions and deliver recommendations.

In other words:
`Day Overview` is the first application of the `Me Platform`, not a competing idea.

## Proposed repo direction
The current repository already contains `Day Overview` materials. I would evolve the structure like this over time:

- `day_overview_ios/`
- `day_overview_backend/`
- `me_platform_shared/` for schemas, prompts, and shared contracts
- `docs/` for architecture and operational notes

No urgent reorganization is needed yet. The important thing is conceptual clarity.

## Recommended next build order

### Step 1
Stabilize the Day Overview MVP around:

- calendar
- weather
- curated news
- simple workout-slot logic

### Step 2
Make the backend schema future-proof enough for:

- events
- workouts
- weather snapshots
- news items
- answer logs

### Step 3
Add a native "Ask" screen in the iPhone app for a small set of supported questions:

- what does tomorrow look like
- when is my next flight
- when can I work out

### Step 4
Add HealthKit-based workout and recovery context.

### Step 5
Add WhatsApp as an interface only after the native app experience is stable.

## Concrete recommendation for what to build next
If we are choosing only one next technical step, it should be:

"Refine the Day Overview backend and data model so it clearly becomes the foundation of the broader Me platform."

That is the shortest path to a real product.

## Questions we do not need to solve yet
- full Apple Messages history ingestion
- full historical WhatsApp ingestion
- complex agentic automation
- long-term autonomous recommendations
- fancy vector search over everything

Those can come later if the first product earns its keep.

## Short version
Build this in layers:

1. Day Overview MVP
2. Queryable personal assistant
3. Recommendation engine

Use:

- SwiftUI on iPhone
- FastAPI backend
- Postgres as source of truth
- local-first handling of calendar and health data

And most importantly:

Do not start with the hardest messaging integrations.
Start with the workflow that will actually help you tomorrow morning.
