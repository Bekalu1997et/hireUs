
Module 1 — Role Blueprint (AI = Yes, LLM only)
Why AI is justified:

# FEATURES

## Introduction
A Structured Technical Interview Platform with Hiring Intelligence for Founders. The product is divided into two main layers:
- **Structured Interview Platform**: Operational layer
- **Hiring Intelligence**: Decision layer

---

## Module 1 — Role Blueprint (AI = Yes, LLM only)
**Purpose:** Help founders define roles properly using AI.

**MVP Features:**
- **Input:**
	- Role title
	- Seniority
	- Stack
	- Team context
- **Output:**
	- Role mission
	- 5–8 core competencies
	- Must-have vs nice-to-have
	- Interview stage suggestions
- LLM structured output → stored as structured JSON

**Exclusions:**
- No salary benchmarking
- No labor market data
- No complex taxonomy engine

---

## Module 2 — Interview Kit Builder (AI = Yes, controlled)
**Purpose:** Use AI for question generation and rubric drafting.

**MVP Features:**
- Choose:
	- Role
	- Interview type (coding / system design / PM case)
- Generate:
	- Problem statement
	- Evaluation rubric
	- Red flags
	- Expected good answer outline

**Exclusions:**
- No adaptive difficulty
- No embeddings
- No memory system
- Static generation per request

---

## Module 3 — Structured Scorecard (AI = Minimal)
**Purpose:** UI and structure for competency-based scoring.

**MVP Features:**
- Competency list from Module 1
- Scoring scale (1–5)
- Required written evidence
- Submit-before-view rule

**AI Usage:**
- "Improve feedback clarity" button (LLM suggests rewriting vague feedback)

**Exclusions:**
- No bias detection
- No ML normalization
- No analytics model

---

## Module 4 — Simple Hiring Workflow (No AI Needed)
**Purpose:** Product design and logic for hiring workflow.

**MVP Features:**
- Customizable pipeline stages
- Assign interviewers
- Track feedback completion
- Block progression until feedback submitted

**Exclusions:**
- No AI

---

## Module 5 — Candidate Comparison View (Light AI)
**Purpose:** Simple visualization for candidate comparison.

**MVP Features:**
- Side-by-side competency scores
- Average score
- Standard deviation
- Interviewer confidence average
- Basic math only

**Optional:**
- LLM-generated summary (e.g., "Candidate A shows strong system design but weaker communication…")

**Exclusions:**
- No ML prediction model

---

## Module 6 — Contract Generator (AI = Yes, but controlled)
**Purpose:** Generate structured contract templates.

**MVP Features:**
- Country selector
- Employment type
- Generate structured template
- Template + editable document
- Clear disclaimer

**Exclusions:**
- No compliance intelligence
- No legal automation engine

---

## Product Core for V1

You are not building a full hiring OS anymore. Focus on:

### 1️⃣ Structured Interview Engine (Operational Core)
### 2️⃣ Founder Decision Intelligence Layer (Insight Core)

Everything else is secondary.

---

## 🎯 V1 Scope — Strict and Focused

### CORE 1: Structured Technical Interview Engine

**Must-Have Features:**
1. **Role Setup (Simple Version of Module 1)**
	 - Role title
	 - Seniority
	 - Tech stack
	 - Core competencies (AI-suggested but editable)
	 - Interview stages (AI-suggested but editable)
	 - **AI usage:**
		 - Generate competency suggestions
		 - Suggest stage flow
	 - **Exclusions:**
		 - No salary logic
		 - No forecasting

2. **Interview Kit Generator**
	 - For: Coding, System Design, PM Case, Design Challenge
	 - AI generates:
		 - Problem statement
		 - Evaluation rubric
		 - Red flags
		 - Good answer outline
	 - **Exclusions:**
		 - No adaptive system
		 - No ML
		 - Just structured generation

3. **Structured Scorecards**
	 - Competency-based scoring
	 - Required written evidence
	 - 1–5 scale
	 - Confidence score
	 - Feedback submission lock
	 - **Exclusions:**
		 - No AI analytics yet
		 - Just clean data

4. **Interview Workflow Board**
	 - Simple Kanban:
		 - Applied
		 - Screening
		 - Technical 1
		 - Technical 2
		 - Decision
	 - **Rules:**
		 - Cannot move forward without required feedback
		 - Interviewers assigned per stage
	 - **Exclusions:**
		 - No automation engine
		 - No agents

---

### 🧠 CORE 2: Hiring Intelligence for Founders

AI adds visible value — but carefully.

**Feature 1 — Candidate Comparison Dashboard**
- Side-by-side:
	- Competency heatmap
	- Average score
	- Confidence variance
	- Written feedback summary
- Math only + LLM summary
- **Exclusions:** No prediction model

**Feature 2 — Decision Brief Generator**
- Founder clicks: "Generate Hiring Brief"
- AI outputs:
	- Candidate strengths
	- Risk areas
	- Signal gaps
	- Interview agreement level
	- Suggested hire / no hire (with explanation)
- Uses structured data already collected
- **Exclusions:** No ML required

**Feature 3 — Interview Signal Gap Detection**
- Simple logic:
	- If competency X has no score
	- Or confidence average < threshold
	- Or variance too high
- System flags: "Signal weak. Recommend additional system design interview."
- **Exclusions:** No ML, just logic rules

---

You are not building a full hiring OS anymore.

You are building:

1️⃣ Structured Interview Engine (Operational Core)
2️⃣ Founder Decision Intelligence Layer (Insight Core)

Everything else is secondary.

🎯 V1 Scope — Strict and Focused
🔹 CORE 1: Structured Technical Interview Engine

This is the main product.

Must-Have Features
1. Role Setup (Simple Version of Module 1)

Role title

Seniority

Tech stack

Core competencies (AI-suggested but editable)

Interview stages (AI-suggested but editable)

AI usage:
✔ Generate competency suggestions
✔ Suggest stage flow

No salary logic. No forecasting.

2. Interview Kit Generator

For:

Coding

System Design

PM Case

Design Challenge

AI generates:

Problem statement

Evaluation rubric

Red flags

Good answer outline

No adaptive system.
No ML.
Just structured generation.

3. Structured Scorecards

This is critical and NOT AI-heavy.

Competency-based scoring

Required written evidence

1–5 scale

Confidence score

Feedback submission lock

No AI analytics yet.
Just clean data.

This becomes your moat later.

4. Interview Workflow Board

Simple Kanban:

Applied

Screening

Technical 1

Technical 2

Decision

Rules:

Cannot move forward without required feedback

Interviewers assigned per stage

No automation engine.
No agents.

🧠 CORE 2: Hiring Intelligence for Founders

This is where AI adds visible value — but carefully.

Feature 1 — Candidate Comparison Dashboard

Side-by-side:

Competency heatmap

Average score

Confidence variance

Written feedback summary

Math only + LLM summary.

No prediction model.

Feature 2 — Decision Brief Generator

Founder clicks:
“Generate Hiring Brief”

AI outputs:

Candidate strengths

Risk areas

Signal gaps

Interview agreement level

Suggested hire / no hire (with explanation)

This is powerful — but simple to build.

It uses structured data you already collected.

No ML required.

Feature 3 — Interview Signal Gap Detection

Very simple logic:

If:

Competency X has no score

Or confidence average < threshold

Or variance too high

System flags:
“Signal weak. Recommend additional system design interview.”

No ML.
Just logic rules.

That’s intelligent enough for V1.
