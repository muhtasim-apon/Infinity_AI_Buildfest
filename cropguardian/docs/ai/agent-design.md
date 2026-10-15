# Agent design — Advisory Agent

Owner: **Raisa** (prompts, behaviour) · **Salwa** (retrieval tools) · **Apon** (API wiring).

## 1. Scope
One bounded agent. It explains a diagnosis and answers follow-up questions in Bangla. It does not
diagnose (the vision model does), does not act in the world, and does not see personal data.

## 2. Tools
| Tool | Type | Input | Returns | Guard |
|---|---|---|---|---|
| `get_diagnosis` | read | scan_id | disease, prob, abstained | scan must belong to caller |
| `search_kb` | read | disease, crop, stage, question | ≤ 8 chunks with ids | metadata filter |
| `get_weather` | read | coarse lat/lon | 3-day humidity, rain, temp | Open-Meteo, cached 1 h |
| `get_field_history` | read | field_id | last 5 diagnoses (no images) | owner only |
| `create_alert_draft` | **write, gated** | disease, area | draft id | **status = draft; needs agronomist approval** |

Autonomy level: L1 (suggest). No tool can send messages, change data visible to others, or spend money.

## 3. Loop
`plan → call tools (max 4 calls) → draft JSON → validator (rag-design §5) → return`.
Hard limits: 4 tool calls, 20 s total, 1,500 output tokens. Exceeded → fallback.

## 4. Prompt structure
```
[system]  role, Bangla style guide (simple words, short sentences, respectful "আপনি"),
          grounding rules, JSON schema, safety rules, refusal rules
[context] diagnosis (disease, confidence band, not raw prob), crop, stage, weather summary
[sources] <source id=..> chunk text </source> × k   ← treated as data only
[user]    farmer's question (optional) — treated as data only
```

## 5. Refusals / escalation
- Disease not in catalog, abstained diagnosis, human/animal health questions, requests for
  banned chemicals, dosage beyond source → "কৃষি কর্মকর্তার সাথে যোগাযোগ করুন" + escalate.

## 6. Voice (stretch)
Text-to-speech of `summary_bn` via browser Web Speech API (`bn-BD`) where supported; pre-recorded
audio for the 7 standard disease cards as fallback. Speech input is a later item.

## 7. Evaluation
Red-team set (Salwa): prompt injection in user text and in a poisoned test KB chunk, requests for
banned pesticides, off-topic medical questions, attempts to get other farmers' data. Gate: 0 failures.
