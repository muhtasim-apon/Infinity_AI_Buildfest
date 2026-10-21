# Personas

Illustrative composites for design — not real people, not research results. Validate in interviews
(Gantt 16–20 Oct). Reviewed against the build spec on 17 Oct (Raisa): added the reviewer persona and
aligned the operator persona with the human-approved alert flow (spec 2, 11.5).

## Rahima — smallholder rice farmer (primary)
- Grows boro and aman rice on a small plot; shared low-end Android phone; prepaid data.
- Reads Bangla slowly; prefers voice and pictures; trusts the local input dealer and neighbours.
- Pain: does not know which disease; afraid of wasting money; advice is often a product sale.
- Needs: one big button to scan; answer in simple Bangla; "what to do today"; works with weak signal;
  an honest "not sure — retake the photo" instead of a wrong answer.
- Design implications: icon-first UI, voice playback, ≤ 3 taps to result, offline outbox, large text
  (Bangla body ≥ 18 px), bands instead of percentages, never blame the user.
- Demo counterpart: "রহিমা (Demo)" — always labelled DEMO DATA.

## Karim — reviewer (agriculture extension officer or trained volunteer)
- Checks photos the model was not sure about; corrects labels; approves or rejects outbreak alert drafts
  for his region (division/upazila) with step-up 2FA.
- Time-poor; works on a laptop or phone between field visits; wants keyboard shortcuts (C / X / U).
- Pain: false alarms damage trust; cannot approve what he cannot understand.
- Needs: a queue sorted by risk; the photo, the model's top-3 with exact probabilities and the heat map;
  field context; one-click verdict; a draft alert in Bangla and English with validator feedback;
  an agreement view showing how often reviewers and the model agree.
- Design implications: dense, fast console; every decision audited; nothing reaches farmers without his
  approval. Demo counterpart: "Karim (Demo)".

## Nadia — Crop Guardian operator (admin; a team member)
- Manages model versions, thresholds and knowledge-base documents; answers to partners about safety.
- Needs: one place to change τ (with a reason and step-up), roll back a model, retire a KB document,
  disable advice for one disease, run the simulation console (demo tenant only), verify the audit chain
  and export an audit report — every action logged. She does not approve alerts herself unless acting as
  a reviewer.

## Judge (evaluation persona)
- Has minutes, not hours. Needs one-click demo, visible architecture, honest data, one-click audit.
- Design implications: `/demo` entry, SIMULATED labels everywhere, Trust Centre with "Not yet measured"
  markers, no number without a source.
