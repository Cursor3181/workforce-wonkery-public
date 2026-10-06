# Workforce Wonkery Depth Layers v1

Status: Staged for preview and governed implementation  
Date: 2026-09-28  
Audience: Workforce development board staff  
Site architecture: Policy · Data · Practice. Decoded.

## Purpose

Strengthen Workforce Wonkery around five analytical layers without adding new top-level navigation or creating a dashboard wall.

The five layers are:

1. AI and technology change inside Occupation Explorer.
2. Workforce-system performance inside Workforce Access & Equity.
3. Labor-market dynamics inside Labor Market Profiles.
4. A recurring Structural Shift feature inside the California Workforce Intelligence Report.
5. Implementation & Impact timelines inside major policy briefs.

## Design rule

Each layer belongs inside an existing decision path. It should answer a question before presenting more metrics.

- Policy: What changed, what happens next, and what evidence of implementation exists?
- Data: What is happening in the labor market, occupations, communities, and workforce system?
- Practice: What can a workforce team learn, adapt, or do?
- Intelligence Report: How do the signals connect?

No new primary navigation item is created.

## 1. Occupation Explorer: AI + technology lens

### Reader question

How might technology change the tasks, skills, or demand around this occupation?

### Governed sources

- Workforce Wonkery Technology Watch v1.1, already published in the technical feed.
- U.S. Bureau of Labor Statistics AI exposure categories and methodology:
  https://www.bls.gov/emp/publications/ai-exposure-categories.htm
- O*NET AI impact research may be used for task-level research when a governed occupation review is completed:
  https://www.onetcenter.org/reports/AI_Impact_Review.html

### Publication rules

- AI exposure is not a job-loss score.
- Technology Watch classifications do not predict replacement probability.
- Separate exposure from the expected type of change: automation, augmentation, task shift, or complementary demand.
- Do not change a training recommendation from technology evidence alone. Local demand, job quality, supply, access, and employer evidence remain required.
- Display a source date and evidence state.

### First-release fields

- Technology effect
- Review state
- Workforce response
- Local grounding requirement
- Reopen trigger
- BLS exposure methodology note

## 2. Workforce Access & Equity: workforce-system performance

### Reader question

What do current performance measures tell us about how the public workforce system is functioning here?

### Governed sources

- U.S. Department of Labor ETA local WIOA performance reporting:
  https://www.dol.gov/agencies/eta/performance
- California EDD PY 2024 annual performance reporting:
  https://edd.ca.gov/en/jobs_and_training/Information_Notices/wsin25-19/
- Existing Workforce Access & Equity Need / Reach / Service / Outcome model.

### First-release measures

Where official local values are available and verified:

- Participants served
- Training participation
- Employment rate, second quarter after exit
- Employment rate, fourth quarter after exit
- Median earnings, second quarter after exit
- Credential attainment
- Measurable skill gains
- Registered apprenticeship participation

### Guardrails

- Do not rank boards.
- Do not combine measures into an overall score.
- Keep Adult, Dislocated Worker, and Youth populations distinct unless an official combined value is explicitly published.
- Separate negotiated-goal performance from raw outcome levels.
- Suppression, missingness, cohort size, and program mix must stay visible.
- Integrate performance with Need / Reach / Service / Outcome rather than presenting a standalone league table.

## 3. Labor Market Profiles: labor-market dynamics

### Reader question

Is the market changing because employers are hiring more, workers are leaving more, jobs are being created, or some combination?

### Governed source

U.S. Census Bureau Quarterly Workforce Indicators:
https://ledextract.ces.census.gov/static/data.html
https://api.census.gov/data/timeseries/qwi/sa/variables.html

### Target measures

- Employment
- All hires / accessions (HirA)
- Separations (Sep)
- Stable-job turnover rate (TurnOvrS)
- Firm job gains / job creation (FrmJbGn)
- Average monthly earnings for stable new hires (EarnHirNS)

### Publication rules

- Use the existing current-LWDA geography recipes where administrative workforce geography is required.
- Preserve Census status flags.
- Do not substitute a neighboring geography without an explicit context label.
- Static governed releases are preferred over a runtime Census API dependency.
- When a flow measure is not yet ingested, do not show a zero or infer it from another measure.

## 4. Intelligence Report: Structural Shift

Every issue should include one compact deep dive on a structural change affecting work.

Required structure:

1. What is changing?
2. Where is California likely to feel it?
3. Which occupations, industries, workers, or systems are exposed?
4. What should WDB staff watch?
5. What is still uncertain?

Possible themes include AI and automation, demographic change, climate and energy transition, migration, funding structure, aging, and technology-driven task change.

The feature must distinguish evidence from interpretation and must not turn exposure into a forecast when the underlying source does not support that conclusion.

## 5. Policy briefs: Implementation & Impact timeline

Major policy briefs may include a compact timeline when the policy has multiple implementation stages.

Standard stages:

- Authority issued
- Effective or implementation date
- California guidance or local implementation milestone
- Local action or reporting milestone
- First point when outcome evidence can reasonably be assessed

The timeline describes documented status. It does not rate political actors, infer motives, or claim impact before evidence is available.

## Release approach

### Release 1

- Expose existing Technology Watch in Occupation Explorer.
- Add Labor Market Dynamics to the labor-market profile pattern using already-governed QWI employment and hiring evidence, with the schema ready for the remaining flow variables.
- Add a workforce-system performance module to Workforce Access & Equity using verified statewide benchmarks immediately and local values only as the official 45-board dataset is ingested.
- Add Structural Shift to the Intelligence Report template and publication standard.
- Add Implementation & Impact to the policy-brief standard and selected major briefs.

### Release 2

- Complete the static QWI flow acquisition for all governed geographies.
- Ingest and validate all available local PY 2024 WIOA performance rows.
- Add BLS AI exposure categories to the governed occupation data release after the official supplemental table is ingested and crosswalked.

## Acceptance criteria

- No new top-level navigation.
- No overall board ranking or equity score.
- No technology “job-loss probability.”
- Missing data stays missing.
- Every new metric displays period, geography, source, and interpretation limit.
- Existing evidence confidence and publication gates remain in force.
- Desktop, mobile, keyboard, and live-page acceptance checks pass before WordPress publication.
