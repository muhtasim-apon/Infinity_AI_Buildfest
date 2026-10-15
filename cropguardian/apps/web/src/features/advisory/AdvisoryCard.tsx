// Advisory card: summary, steps, chemical (dose verbatim + pre-harvest interval), safety line,
// citations, voice playback. Renders text only — never HTML from the LLM/KB (XSS, threat T19). Stub.
import type { Advisory } from "../../lib/api";

export default function AdvisoryCard({ advisory }: { advisory: Advisory }) {
  return <section data-status={advisory.status}>{/* TODO(sara, raisa) */}</section>;
}
