# Role routing, evidence patterns, and delivery checks

Use this reference when tailoring or rewriting a resume. Adapt the information architecture of popular resume-template repositories without copying their sentences, claims, metrics, or outdated keyword lists.

## Route the resume

Infer one primary role family from the target job and the candidate's demonstrated evidence:

| Role family | Prioritize evidence of |
|---|---|
| Backend | service ownership, data consistency, performance, reliability, interfaces, debugging |
| Frontend | user interaction, accessibility, performance, design-system work, cross-team delivery |
| Mobile or client | platform expertise, release quality, device constraints, stability, adoption |
| Data or machine learning | data quality, experiment design, model or pipeline impact, reproducibility |
| Infrastructure, SRE, or security | availability, automation, observability, incidents, risk reduction |
| Architecture or technical leadership | trade-offs, system boundaries, migration, standards, mentoring, cross-team influence |
| Product, design, or operations | user problem, prioritization, research, process ownership, measurable outcome |
| AI product or AI strategy | user problem, model capability and limits, data or knowledge inputs, evaluation, workflow design, experimentation, adoption, commercial outcome, safety and cost trade-offs |
| General or uncertain | transferable ownership, problem solving, delivery, learning, communication |

Infer one level: `new graduate`, `individual contributor`, `senior`, `staff or architect`, or `manager`. Use scope and demonstrated ownership, not years alone. When the evidence is mixed, choose the lower-confidence level and state the assumption.

Do not use a static technology-frequency list. Extract terminology from the current job description, then label each important requirement as proved, partly proved, or unproved using the evidence ledger.

For AI product or AI strategy candidates, do not treat API calls, prompt writing, local model deployment, or a list of AI tools as product experience by themselves. Look for a supported chain such as `user problem → product hypothesis → model or workflow choice → evaluation → iteration → adoption or business result`. Preserve partial evidence and label missing links instead of inventing a complete product case.

## Select representative evidence

For each project or experience, assess:

- relevance to the target role;
- strength of evidence;
- candidate ownership;
- recency or continued relevance.

Keep the smallest set that proves the most important capabilities. Prefer a representative project over several repetitive projects. Preserve older work only when it proves a capability not shown elsewhere.

For technical candidates, consider public proof such as open-source contributions, technical writing, talks, demos, portfolios, or reproducible projects. Include only verifiable items supplied by the user.

## Build evidence-first bullets

Use the supported parts of this chain:

`Problem or context → Action → Differentiator → Scope → Result → Business meaning`

Useful skeletons:

- `针对[真实问题]，使用[真实方法]完成[真实动作]，在[真实范围]内实现[真实结果或占位符]。`
- `负责[真实范围]，通过[真实技术或流程]解决[真实难点]，使[已证实结果或占位符]。`
- `主导[真实项目或决策]，协调[真实参与方]完成[真实交付物]，带来[已证实业务影响或占位符]。`
- `在[真实项目]中承担[真实职责]；当前材料未提供结果，补充问题：[最有价值的事实问题]。`

Do not force every field into every bullet. A precise action with a clear deliverable is better than a fabricated outcome. Never copy example numbers, awards, employers, user counts, team sizes, technologies, or titles.

When metrics are missing, ask about verifiable dimensions such as latency, throughput, error rate, availability, cost, time saved, user scale, delivery time, defect reduction, conversion, revenue, or team scope. Keep the answer as a placeholder until the user supplies it.

## Scenario guardrails

### Backend social-hire scenario

Source states only that the candidate developed an order API using Redis. The job description asks for a framework, high concurrency, and observability.

- Route to backend; do not infer seniority without ownership or scope evidence.
- Mark Redis as proved.
- Mark the framework, high-concurrency experience, and observability as unproved unless other source evidence exists.
- Rewrite the supported action and ask for the Redis use case, traffic or latency evidence, production scope, and ownership. Do not manufacture a performance improvement.

### Frontend new-graduate scenario

Source states only that the candidate built a course project with a frontend framework. The job description asks for production performance and accessibility.

- Route to frontend and new graduate unless stronger evidence exists.
- Preserve the course-project context.
- Mark production performance and accessibility as unproved.
- Ask for the candidate's concrete contribution, interaction implemented, constraints, testing, deployment, and user feedback. Do not convert coursework into employment or production experience.

## Delivery checklist

Before final delivery, verify:

- contact details and links are present only when supplied and appear internally consistent;
- chronology is reverse-ordered unless the format has a clear reason otherwise;
- dates, titles, education, employers, and project attribution do not conflict;
- the target role is clear and the most relevant evidence appears early;
- every important job-description keyword is contextualized by evidence or labeled unproved;
- bullets distinguish the candidate's action from the team's result;
- no new number, award, tool, credential, employer, title, or outcome was introduced;
- repeated projects and generic self-praise are removed;
- section headings and layout are ATS-readable;
- length serves relevance and readability rather than obeying a universal one-page rule;
- unresolved placeholders and clarification questions are visible;
- the output filename is professional and role-specific when a file is generated.

If any fact-safety check fails, withhold the final rewrite and surface the unsupported claim.
