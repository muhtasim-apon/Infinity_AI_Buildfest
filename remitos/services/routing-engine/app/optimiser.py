"""Routing optimiser — the commercial core of RemitOS.

STUB. This module has never been executed. Signatures and contracts only.

WHAT THIS SOLVES
----------------
Given a send request, choose the payout path that maximises the amount reaching the
recipient, subject to arrival-time preference and hard regulatory constraints.

The problem is small (tens of candidates) but the *constraints* are the interesting
part, and they are what every competing product handles after the fact or not at all.

THE CONSTRAINT THAT DEFINES THE PRODUCT
---------------------------------------
Bangladesh Bank caps agent cash-out at Tk 30,000/day and Tk 200,000/month, and caps a
wallet balance at Tk 500,000 (re-fixed March 2025).

A naive implementation computes the cheapest route, attempts it, and fails at payout.
In practice that means a recipient — often an older woman who has travelled 40 minutes
to an agent point during a medical emergency — is told "no" at the counter.

Here the ceilings are constraints in the solve, so the engine returns one of three
honest outcomes BEFORE the sender pays:

    1. a single compliant path,
    2. a legal split across endpoints, priced and timed,
    3. explicit infeasibility, with alternatives.

See ADR 0007 and docs/product/user-journeys.md journey J3.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

__all__ = [
    "PayoutEndpoint",
    "Candidate",
    "RegulatoryLimits",
    "OptimiserObjective",
    "Optimiser",
]


class PayoutEndpoint(str, Enum):
    MFS_WALLET = "mfs_wallet"
    BANK_ACCOUNT = "bank_account"
    AGENT_CASH = "agent_cash"
    HOME_DELIVERY = "home_delivery"


@dataclass(frozen=True, slots=True)
class RegulatoryLimits:
    """Bangladesh Bank ceilings, in **poisha**.

    Sourced from configuration with an effective date, never hard-coded — limits change
    by circular, sometimes at short notice (including temporary election-period caps),
    and a limit change must be a config change, not a deploy. Refreshed by n8n
    workflow 07. See docs/research/data/02-bangladesh-market-constraints.md §2.2.
    """

    cash_out_daily: int
    cash_out_monthly: int
    cash_in_daily: int
    p2p_daily: int
    max_wallet_balance: int
    effective_from: datetime

    #: Set when these limits came from a temporary circular. The UI must say so —
    #: a user who could send Tk 50,000 last week deserves to know why they cannot now.
    is_temporary: bool = False


@dataclass(frozen=True, slots=True)
class Candidate:
    """One feasible way to move money, before constraint filtering.

    Cost and ETA are **model predictions**, not commitments. The binding quote is
    produced by fx-service and the partner's committed fee at execution. See the
    corridor-cost-predictor model card.
    """

    partner_id: str
    endpoint: PayoutEndpoint
    predicted_cost_poisha: int
    predicted_fx_rate: float
    predicted_eta: timedelta

    #: 90 % interval on the ETA. Shown to the user rather than hidden behind a point
    #: estimate — an ETA the product cannot honour costs more trust than an honest range.
    eta_interval: tuple[timedelta, timedelta]

    partner_uptime_7d: float
    partner_liquidity_available: int
    incentive_eligible: bool

    #: True when no own-history existed for this corridor/partner and the prediction
    #: fell back to published rates. Must surface in the UI as provisional.
    is_provisional: bool = False


class OptimiserObjective(str, Enum):
    """What the user is optimising for.

    ``MAX_LANDED`` is the default because it is what senders actually optimise for —
    not the fee, which hides the FX margin (see the send_money domain note).
    """

    MAX_LANDED = "max_landed"
    MIN_TIME = "min_time"
    BALANCED = "balanced"


class Optimiser:
    """Selects payout paths under regulatory and operational constraints."""

    def solve(
        self,
        *,
        amount_poisha: int,
        candidates: list[Candidate],
        limits: RegulatoryLimits,
        recipient_usage_today: int,
        recipient_usage_month: int,
        recipient_wallet_balance: int,
        objective: OptimiserObjective = OptimiserObjective.MAX_LANDED,
        allow_split: bool = True,
    ) -> object:
        """Return a ``RoutesAvailable``, ``SplitRequired`` or ``Infeasible`` decision.

        TODO(routing): implement in this order.

        1. **Constraint filter.** For each candidate compute *headroom*:
           the remaining legal capacity at that endpoint given the recipient's usage
           today and this month, and — for wallets — the balance ceiling. Note the
           subtlety: headroom is a property of the *recipient*, not of the partner, and
           it is consumed across every sender paying that recipient. A route that looks
           available in isolation may not be.

        2. **Single-path solve.** Any candidate with headroom >= amount is feasible.
           Rank by ``objective`` and return ``RoutesAvailable``.

        3. **Split solve** (only if step 2 is empty and ``allow_split``).
           Choose the minimum number of legs that clears the amount legally. Minimising
           leg count is deliberate: every extra leg is another thing to explain to a
           low-literacy user and another thing that can fail. A two-leg split that costs
           slightly more than a four-leg split is the better product.
           Prefer legs that are available *soonest* — the first leg should be
           withdrawable today wherever possible, because the reason the amount is large
           is frequently an emergency.

        4. **Infeasible.** Return ``Infeasible`` with concrete suggestions: a smaller
           amount today, adding a bank account, collecting across days. An infeasible
           answer without a next step is a dead end, not an explanation.

        5. **Explain.** Generate a Bangla rationale naming the specific limit, and a
           reason code per option. Rationale is generated in Bangla, not generated in
           English and translated (ADR 0012).

        Constraints that are NOT optional, whatever the objective says:
          * regulatory ceilings — never traded off against cost,
          * sanctions or compliance BLOCK — the candidate is removed, not down-ranked,
          * partner liquidity — a cheap route the partner cannot fund is not a route.

        Performance budget: p95 under 400 ms including model inference, per FR-01.
        With tens of candidates this is a filter-and-rank, not a solver — if a future
        version needs an MILP, it belongs off the synchronous path with the result
        cached.

        Raises:
            ValueError: if ``amount_poisha`` <= 0 or ``candidates`` is empty.
        """
        raise NotImplementedError("Stub — see TODO above.")

    def _headroom(
        self,
        *,
        endpoint: PayoutEndpoint,
        limits: RegulatoryLimits,
        used_today: int,
        used_month: int,
        wallet_balance: int,
    ) -> int:
        """Remaining legal capacity at ``endpoint``, in poisha.

        TODO(routing):
          * AGENT_CASH  -> min(daily - used_today, monthly - used_month)
          * MFS_WALLET  -> min(p2p_daily - used_today, max_balance - wallet_balance)
          * BANK_ACCOUNT-> no MFS ceiling; bank and AML thresholds apply instead
          * HOME_DELIVERY -> partner-specific; treat as agent cash unless stated

        Never returns a negative number; clamp at zero. A negative headroom means the
        recipient is already at or over a ceiling, which is a valid state (limits can
        be lowered by circular between transactions) and must not produce a nonsense
        split proposal.
        """
        raise NotImplementedError("Stub — see TODO above.")
