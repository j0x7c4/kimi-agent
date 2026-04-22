# Anti-AI Writing Patterns Reference

> **Usage**: Orchestrator reads this file and inlines its content into writer subagent system prompts. Writers follow these rules during drafting. Editors use this as a checklist during review.

## Detection Severity Tiers

### Critical (instant AI flag — must never appear)

- Citation artifacts: `oaicite`, `turn0search`, hallucinated reference markers
- Knowledge cutoff phrases: "as of my last update," "based on available information"
- Chatbot artifacts: "I hope this helps!", "Let me know if you need anything else"
- Markdown leakage: stray `**`, `##`, backticks in creative text

### High-Signal (strong AI indicators)

- **Inflated significance**: "stands as a testament to," "marking a pivotal moment," "indelible mark"
- **Promotional language**: "vibrant," "breathtaking," "groundbreaking," "nestled in," "in the heart of"
- **AI vocabulary**: Additionally, delve, tapestry, landscape (abstract), pivotal, foster, underscore, interplay, intricate, enhance, embark, beacon, multifaceted, myriad
- **Copula avoidance**: "serves as," "stands as," "boasts," "features" where "is" / "has" is natural
- **Chinese AI vocabulary**: 助力, 彰显, 凸显, 焕发, 深度剖析, 赋能, 闭环, 数字化转型, 智慧时代
- **Chinese structural markers**: "首先…其次…最后…" chains, "值得注意的是", "综上所述", "不难发现" — replace with conversational equivalents ("说真的", "其实", "所以")
- **Chinese rhetorical excess**: > 2 parallel couplets (对偶句), > 1 排比句 cluster, > 4 quotation-as-authority sentences per piece
- **Sycophantic tone**: "Great question!", "You're absolutely right!"
- **Hedging stacks**: "could potentially possibly be argued that perhaps"
- **Em-dash (——) overuse in Chinese fiction**: density > 5 per 1000 Chinese chars is a strong AI indicator. Target: ≤ 15 per 3000-char chapter. Especially dangerous in long-form writing where density escalates with context length. Replace with commas, periods, or sentence restructuring.

### Medium-Signal (AI tendencies)

- **Vague attributions**: "experts believe," "industry reports suggest" — name sources or cut
- **Superficial -ing clauses**: "highlighting…", "showcasing…", "symbolizing…"
- **False ranges**: "from X to Y" where X/Y aren't on a meaningful scale ("from the birth of stars to the dance of dark matter") — use specific items instead
- **Inline-header vertical lists**: "- **Topic:** description" bullet patterns where every item has bolded header + colon — collapse into prose or vary the format
- **Filler phrases**: "In order to" → "To"; "Due to the fact that" → "Because"
- **Transition chains**: "Furthermore… Moreover… Additionally… In conclusion…"
- **Formulaic wrap-ups**: "Despite these challenges…", "Looking ahead…"

### Style-Level (cumulative signal)

- Negative parallelisms ("It's not just X, it's Y")
- Rule of three overuse (forcing triplets)
- Synonym cycling ("protagonist" → "main character" → "central figure")
- Uniform sentence/paragraph length
- Boldface inflation
- Curly quotation marks
- Generic endings ("The future looks bright")

## Genre-Specific AI Patterns

| Genre | Patterns to Watch |
|-------|-------------------|
| Fiction/Novel | 璀璨/瑰丽/绚烂 adjective excess; abstract emotions instead of actions — replace with graduated physiological actions: light (clenched jaw, swallowed hard), medium (hands shaking, voice cracking), heavy (slammed fist, legs buckled); 四字格律 overuse (心潮澎湃/热血沸腾); uniform dialogue voices; causal-connector chains (因为/所以/由于/鉴于/为了/试图) creating instruction-manual prose — show causation through action sequence, not explicit connectors |
| Poetry | "tapestry of emotions," cliché nature imagery, forced profundity |
| Lyrics | Generic love metaphors, over-rhyming, abstract emotion without grounding |
| Essay | Throat-clearing ("In today's fast-paced world…"), summarizing endings |
| Screenplay | On-the-nose dialogue, wall-of-text action blocks |
| Fanfiction | All characters sound the same; modern idioms in period settings |

## The Antidote: Writing with a Pulse

- **Have opinions.** React to facts. Mixed feelings are human.
- **Let mess in.** Tangents, asides, half-formed thoughts.
- **Be specific.** Not "this is concerning" but concrete detail.
- **Vary rhythm.** Short sentences. Then longer flowing ones.
- **Acknowledge complexity.** Uncertainty and contradiction are features.
- **Use "I" when genre allows.** First person is honest, not unprofessional.
