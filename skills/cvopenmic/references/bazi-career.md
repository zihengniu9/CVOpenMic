# Bazi career-reflection bridge

Use this reference only after the user explicitly requests Bazi-based career reflection. Treat the result as traditional-culture entertainment and a prompt for self-reflection, not scientific assessment or decision evidence.

## Required inputs

CVOpenMic owns this workflow. Do not require another skill. Obtain or accept a chart and retain only:

- four pillars;
- day master and strength summary;
- five-element balance and useful elements;
- high-level ten-god tendencies relevant to work style.

Do not request or analyze name changes, health, romance, wealth, lifespan, living status, historical-event validation, luck cycles, or unrelated fortune topics.

Minimum inputs are Gregorian birth date, local birth time, and birth city. Do not collect a name, former name, alive/deceased status, lunar birthday, gender, or unrelated life history for this narrow career-reflection use case. Gender is unnecessary because this module does not calculate luck-cycle direction.

Use a reliable calendar or ephemeris capability for the year, month, day, and hour pillars. Year and month pillars must follow solar-term boundaries rather than lunar-month boundaries. Use local time and check whether longitude or equation-of-time correction could cross a two-hour branch boundary. If reliable charting is unavailable, ask once for a chart created by a trusted calendar. Do not calculate the day pillar or exact solar-term boundary from memory.

Retain these core correspondences when interpreting a supplied chart:

| Lens | Work-style theme only |
|---|---|
| 印星 | learning, research, documentation, synthesis, mentorship |
| 食伤 | expression, creation, teaching, product output, problem framing |
| 财星 | customers, resources, commercial outcomes, negotiation, execution |
| 官杀 | responsibility, rules, deadlines, constraints, visible accountability |
| 比劫 | autonomy, competition, entrepreneurship, peer collaboration |

Use five-element balance only as a prompt to reflect on growth, expression, structure, analysis, or adaptability. Never convert an element directly into a job title.

## Interpretation dimensions

Convert traditional symbols into questions, not personality facts:

| Traditional lens | Reflective work question |
|---|---|
| 官杀 | Does the user prefer clear responsibility, rules, deadlines, and visible accountability? |
| 印星 | Do learning, research, credentials, documentation, and mentorship energize the user? |
| 食伤 | Does the role reward expression, creation, teaching, product output, or problem framing? |
| 财星 | Does the user enjoy customers, resources, commercial outcomes, negotiation, or execution? |
| 比劫 | Does the user prefer autonomy, competition, entrepreneurship, or peer collaboration? |
| Five-element balance | Which environment deserves reflection: growth, expression, structure, analysis, or adaptability? |

Never map a symbol directly to a profession. Compare these questions with the actual JD's environment: autonomy, structure, pace, ambiguity, collaboration, customer exposure, creative output, analytical depth, and risk tolerance.

## AI product and strategy bridge

When the target is AI strategy or AI product management, compare the chart reflection with demonstrated evidence in these dimensions:

- comfort with ambiguity and incomplete model capability;
- research synthesis and structured problem framing;
- translating technical constraints into user or business choices;
- experimentation, evaluation, and iteration;
- customer exposure, adoption, monetization, cost, safety, and risk trade-offs;
- cross-functional communication and accountable delivery.

Resume evidence always wins. For example, publications may support research depth, a monetized content project may support user and commercial awareness, and an API or local-deployment experiment supports technical curiosity only—not end-to-end product ownership unless the missing links are evidenced.

## Output format

Return:

1. `命盘摘要` — only the chart facts supplied by the charting source.
2. `工作方式映射` — 3–5 tentative preferences, each phrased as “可能更偏好…，请结合真实经历验证”.
3. `与目标岗位的张力` — `较顺势 / 中性 / 有张力`, with the JD feature being compared.
4. `现实证据对照` — compare each reflection with facts already present in the resume; avoid a questionnaire when evidence is available.
5. `边界说明` — state that the module is traditional-culture entertainment and does not affect the evidence-based resume score or career recommendation.

## Safety rules

- Do not output destiny, guaranteed success, guaranteed failure, or a fixed suitable/unsuitable conclusion.
- Do not use birth information to evaluate another person in employment, education, lending, insurance, housing, or other consequential decisions.
- Do not store or repeat exact birth details unnecessarily.
- Prefer the user's demonstrated experience and preferences whenever they conflict with the traditional interpretation.

## Attribution

The charting workflow and core correspondence review were informed by [jinchenma94/bazi-skill](https://github.com/jinchenma94/bazi-skill), released under the MIT License. CVOpenMic keeps a narrower career-reflection scope, does not require that skill at runtime, does not copy its classical reference corpus, and does not claim scientific validity for Bazi analysis.
