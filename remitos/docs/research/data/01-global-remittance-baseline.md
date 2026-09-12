# Research Note 01 — Global Remittance Baseline

> **Provenance rule:** every figure below carries a source and an access date. No number
> enters the master report unless it appears in this folder first.
> Access date for all rows: **2026-09-12** unless stated otherwise.

## 1.1 Cost of sending money — World Bank Remittance Prices Worldwide (RPW)

| Metric | Value | Period | Source |
|---|---|---|---|
| Global average cost to send USD 200 | **6.36 %** | Q3 2025 | RPW Issue 54, Sep 2025 [R1] |
| Global average cost | 6.49 % | Q1 2025 | RPW Issue 52 [R2] |
| Global average cost | 6.26 % | Q4 2024 | RPW Issue 52 [R2] |
| Global average — **digital** remittances | **4.59 %** | Q3 2025 | RPW Issue 54 [R1] |
| Global average — **non-digital** remittances | **7.30 %** | Q3 2025 | RPW Issue 54 [R1] |
| South Asia — lowest-cost receiving region | **4.80 %** | Q1 2025 | RPW Issue 52 [R2] |
| SDG 10.c / G20 target | **3 %** by 2030; no corridor above 5 % | target | UN SDG 10.c [R3] |
| RPW coverage | 377 corridors · 48 sending · 111 receiving countries | 2025 | RPW [R4] |

**The single most important derived fact for this project:**
digital costs **2.71 percentage points** less than non-digital (7.30 − 4.59). The entire
economic thesis of RemitOS lives inside that gap — and inside the further gap between
4.59 % and the 3 % SDG target.

## 1.2 Bangladesh position

| Metric | Value | Period | Source |
|---|---|---|---|
| Annual remittance inflow | **USD 35.56 bn** | FY Jul 2025 – Jun 2026 | Bangladesh Bank via press [R5] |
| Prior fiscal year | USD 30.33 bn | FY 2024-25 | [R5] |
| Year-on-year growth | **+17.3 %** (+USD 5.23 bn) | FY 2025-26 | [R5] |
| Calendar-year inflow | USD 32.8 bn | CY 2025 | World Bank [R6] |
| Global rank by remittance received | **7th** | 2025 | World Bank [R6] |
| Rank within South Asia | 3rd | 2025 | World Bank [R6] |
| Remittances as % of GDP | 5.26 % | 2023 (latest firm WB figure) | World Bank indicator BX.TRF.PWKR.DT.GD.ZS [R7] |
| World average, same indicator | 5.13 % | 2023 | [R7] |

> **Caution flag for the report:** the % of GDP figure lags. State it as "5.26 % in 2023,
> the latest confirmed World Bank observation" rather than implying a 2026 value.

## 1.3 Settlement-rail benchmark — BIS Project Nexus

| Fact | Detail | Source |
|---|---|---|
| What it is | Scheme connecting *domestic* instant-payment systems via common APIs and **ISO 20022** messages | BIS [R8] |
| Target settlement time | **≤ 60 seconds** | [R9] |
| Blueprint status | Phase-3 blueprint, scheme rulebook and ISO 20022 message specs complete | BIS / BNM [R10] |
| Governance | Nexus Global Payments incorporated 2025 by central banks of India, Malaysia, Philippines, Singapore, Thailand | [R10] |
| Live target | **2027** go-live across India + 4 ASEAN states | [R11] |
| Bangladesh status | **Not a founding member.** This is an opportunity and a risk — see report §5 and §19 | derived |

Nexus matters to us twice over: it is the credible benchmark for "fast and cheap"
(60 s, ISO 20022), and Bangladesh's absence from the founding set is a concrete
gap our architecture should be designed to close rather than ignore.

---

## References

- [R1] World Bank, *Remittance Prices Worldwide*, Issue 54, September 2025 — https://remittanceprices.worldbank.org/sites/default/files/2026-04/RPW_main_report_and_annex_Q325.pdf
- [R2] World Bank, *Remittance Prices Worldwide*, Issue 52, March 2025 — https://remittanceprices.worldbank.org/sites/default/files/rpw_main_report_and_annex_q125_1_0.pdf
- [R3] UN, Sustainable Development Goal indicator 10.c.1 — https://unstats.un.org/sdgs/
- [R4] World Bank Data Catalog, Remittance Prices Worldwide — https://datacatalog.worldbank.org/search/dataset/0037898/remittance-prices-worldwide
- [R5] Bangladesh record annual remittance inflow reporting — https://en.banking.gurukul.edu.bd/bangladesh-sets-record-with-35-56bn-annual-remittance-inflows/
- [R6] World Bank / KNOMAD migration and development data — https://www.knomad.org/
- [R7] World Bank, Personal remittances received (% of GDP), Bangladesh — https://data.worldbank.org/indicator/BX.TRF.PWKR.DT.GD.ZS?locations=BD
- [R8] BIS, *Nexus: enabling instant cross-border payments* — https://www.bis.org/publ/othp86.htm
- [R9] BIS Nexus documentation — https://docs.bis.org/nexus/introduction
- [R10] Bank Negara Malaysia, Nexus blueprint press release — https://www.bnm.gov.my/-/nxs-pr
- [R11] BIS Innovation Hub, Nexus topic page — https://www.bis.org/about/bisih/topics/fmis/nexus.htm
