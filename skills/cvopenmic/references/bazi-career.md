# Bazi career-reflection bridge

Use this reference only after the user explicitly requests Bazi-based career reflection. Treat the result as traditional-culture entertainment and a prompt for self-reflection, not scientific assessment or decision evidence.

## Required inputs

Prefer a chart produced by a compatible Bazi skill. For this module, retain only:

- four pillars;
- day master and strength summary;
- five-element balance and useful elements;
- high-level ten-god tendencies relevant to work style.

Do not request or analyze name changes, health, romance, wealth, lifespan, living status, historical-event validation, luck cycles, or unrelated fortune topics.

If a chart is unavailable, ask the user to install [jinchenma94/bazi-skill](https://github.com/jinchenma94/bazi-skill) or paste a chart created by a trusted calendar. Do not calculate solar terms or day pillars from memory.

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

## Output format

Return:

1. `命盘摘要` — only the chart facts supplied by the charting source.
2. `工作方式映射` — 3–5 tentative preferences, each phrased as “可能更偏好…，请结合真实经历验证”.
3. `与目标岗位的张力` — `较顺势 / 中性 / 有张力`, with the JD feature being compared.
4. `现实验证问题` — 3 questions about past work or study experience that could confirm or falsify the reflection.
5. `边界说明` — state that the module is traditional-culture entertainment and does not affect the evidence-based resume score or career recommendation.

## Safety rules

- Do not output destiny, guaranteed success, guaranteed failure, or a fixed suitable/unsuitable conclusion.
- Do not use birth information to evaluate another person in employment, education, lending, insurance, housing, or other consequential decisions.
- Do not store or repeat exact birth details unnecessarily.
- Prefer the user's demonstrated experience and preferences whenever they conflict with the traditional interpretation.

## Attribution

The optional charting interoperability is inspired by `jinchenma94/bazi-skill`, released under the MIT License. CVOpenMic does not copy its classical reference corpus or claim scientific validity for Bazi analysis.
