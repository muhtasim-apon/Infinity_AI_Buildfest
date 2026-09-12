# Congress Day Demo Script

**Format (§9.3):** 5 minutes per team — 1 min transition + **3 min pitch** + 1 min
scoring. Judged once, in an assigned group. Structure required:
**Problem → Solution → Demo → AI → Impact**, then judge questions.

Three minutes of speaking. Budget every second.

---

## Pre-demo checklist

- [ ] Demo runs **fully offline** — the hall wifi will be saturated with 5,000 people
- [ ] Second device ready, already at the demo state
- [ ] Recorded fallback video, offline, on the machine (not streamed)
- [ ] All data labelled **synthetic** on screen (§20.4)
- [ ] Bangla rendering verified on the projector, not just the laptop
- [ ] Screen brightness and font sizes legible from the back of the room
- [ ] Presenter knows the four source numbers without notes

---

## 0:00 – 0:25 · Problem

> Thirty-five and a half billion dollars came into Bangladesh last fiscal year. Seventh
> largest in the world.
>
> About **half** of the total flow doesn't come through the formal system. It goes through
> hundi — because hundi is faster and the rate is better.
>
> Formal channels don't lose on compliance. They lose on **the decision**: nobody tells a
> sender which route actually delivers the most money.

## 0:25 – 0:50 · Solution

> We're not a wallet. bKash and Nagad are rails; rails aren't the gap.
>
> RemitOS is the intelligence layer above every rail. ML routing, compliance automation
> grounded in the actual circulars, predictive FX timing. Bangla-first, and it works on a
> feature phone with no internet.

## 0:50 – 2:05 · Demo — the 75 seconds that decide the score

**Do not narrate the UI. Show the decision.**

| Time | Action | Say |
|---|---|---|
| 0:50 | Enter Tk 45,000 | "Forty-five thousand to his mother." |
| 0:58 | **Three routes appear** | "We lead with what *reaches her* — not the fee. Three hundred and twenty taka more, two hours slower. One line, in Bangla." |
| 1:15 | Change to **Tk 120,000** | "Now the case nobody designs for. A medical emergency." |
| 1:22 | **Split proposal appears** | "Bangladesh Bank caps agent cash-out at thirty thousand a day." |
| 1:30 | Point at the two legs | "Every other product would quote this, take his money, and she finds out at the counter — after a forty-minute journey. We know before we quote. Thirty thousand today, ninety tomorrow, both priced, both legal." |
| 1:50 | **Play the IVR audio** | "And she hears this. A voice call, in Bangla. She doesn't have a smartphone — and nor do about sixty-nine million mobile connections in this country." |

Let the Bangla audio play. Do not talk over it. Silence in a demo hall is powerful and
nobody else will use it.

## 2:05 – 2:35 · AI

> Four layers. None of them a chatbot.
>
> ML predicts landed cost and ETA per rail. Retrieval over Bangladesh Bank circulars
> answers compliance questions **with citations** — and refuses if it can't find the rule.
> A knowledge graph catches the network signature per-transaction scoring misses. Agents
> investigate and build the evidence file — but **no agent moves money**.
>
> Personal data never leaves Bangladesh. Tokenised before any external model call, with an
> egress filter that blocks it if we get it wrong.

## 2:35 – 3:00 · Impact

> One percent off a thirty-five billion dollar flow is three hundred and fifty million
> dollars a year staying with families.
>
> We measure landed amount per hundred sent, time to her hand, and false-positive rate
> **by group** — because a held transfer is somebody's medicine.
>
> The core is domain-agnostic: credit, fraud, wealth and SME are configuration.
>
> Next step: Bangladesh Bank sandbox, one corridor, real users.

---

## Judge Q&A — prepared answers

**"Why won't bKash just build this?"**
> They might. Two reasons they haven't: an incumbent rail has little incentive to
> commoditise itself by comparing against competitors, and routing across rails requires
> neutrality they structurally don't have. Our realistic path is partnering with a PSP
> that wants the intelligence — which is why compliance-as-a-service is in the model.
> It's the largest risk in the project and it's in our risk register with an owner.

**"What's your accuracy?"**
> We haven't trained the models — this is an architecture and a specification, and I
> won't quote a number I haven't measured. What I can show you is the evaluation plan:
> the golden sets, the targets, and the fairness gates that block a release. Including
> the one most teams miss — device tier is a wealth proxy, and a model that flags cheap
> handsets has learned to penalise poverty.

**"Where's the money?"**
> Basis points on landed value, FX spread share, and licensing the compliance stack to
> smaller PSPs. The unit-economics model is in the PRD — with human review cost included,
> because a mandatory human gate is a real cost per transfer and leaving it out is how
> fintech models flatter themselves.

**"What can't you do?"**
> Outbound payments from Bangladesh. That's a capital-account policy question, not a
> product one — it's the same reason PayPal isn't available here. We also have no
> licence, no float and no agent network. All three are in the gap analysis with
> mitigations. A project that claims to have solved cross-border payments without
> addressing licensing has built a demo, not a business.

**"Is any of this running?"**
> The architecture, documentation, evaluation plan and this client flow — yes, what
> you're seeing is real. The models are specified, not trained; I'd rather tell you that
> than show you a number I made up.

---

## Failure drills

| If | Then |
|---|---|
| Demo device fails | Second device, already at demo state. Keep talking |
| Both fail | Recorded video, offline |
| Everything fails | Deliver the pitch from the printed split-screen handout. The argument works without the screen |
| Over time at 2:05 | **Cut the AI section to one sentence.** Never cut the demo |
| Judge interrupts early | Answer, then jump straight to Impact. Never abandon Impact |
