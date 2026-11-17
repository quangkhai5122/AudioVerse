# Long-horizon AI research questions (separate from product engineering)

## RQ1: Long-horizon consistency of Vietnamese interactive audio fiction
Compare authored graph with structured state+LLM vs world-summary-only LLM under adversarial 20/50/100-turn runs. Build rights-cleared native Vietnamese corpus, canonical fact ledger and blind human review. Metrics: violation rate, choice impact, story quality, latency and cost.

## RQ2: Decision-aware generative caching
Find when two runs have equivalent future narrative states (bisimulation-like equivalence) permitting shared text/audio without leaking private choices. Formalize canonical state equivalence, rights version, voice output and privacy boundaries. Evaluate effective cache hit vs state explosion and story diversity.

## RQ3: Vietnamese expressive TTS for narration
Benchmark domain-specific prosody and character voice across APIs and permitted open models, especially Hán-Việt, horror pacing, dialogue differentiation and 30-minute listener fatigue. Fine-tune only on correctly licensed text/audio with documented speaker consent. Report RTF, MOS, objective errors and comparison to unadapted baseline.

## RQ4: Interactive branching under fixed cost budget
Choose pre-render/prefetch/on-demand policy under latency and cost constraints. Formulate constrained MDP for prefetch policy or adaptive caching; model uncertain player choice distribution; evaluate online regret/latency on a synthetic lawful simulator first.

## RQ5: Narrative evaluator reliability
Assess whether LLM judges detect consistency errors vs deterministic validators and blinded Vietnamese human raters. Use contradictory adversarial scenes, annotated outcome labels and inter-rater reliability; do not optimize models exclusively to one LLM judge.

## Stage-gated R&D
R0 product experience and legal rights first. R1 gather original controlled benchmarks. R2 compare strong API baseline. R3 decide whether self-hosting/fine-tuning provides measurable quality or cost benefit. R5 publication-quality experiment if suitable. Research should not delay core player safety or production release gates.
