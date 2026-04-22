# Systems / Technical Paper Style

## Voice and Tone
- Engineering-oriented: focus on design decisions, trade-offs, and practical constraints
- Concrete: architecture diagrams, performance benchmarks, resource measurements
- Pragmatic: acknowledge real-world constraints (latency, cost, scalability)
- Direct: lead with what was built and why, then how

## Structure Conventions
- Introduction: motivating use case → design requirements → solution overview → evaluation summary
- System design section replaces traditional "Methodology": architecture, components, APIs, data flow
- Implementation section: technology stack, optimization techniques, deployment considerations
- Evaluation: end-to-end benchmarks, component benchmarks, scalability tests, comparison with alternatives
- Include architecture diagrams and data flow figures

## Language Patterns
- Prefer: "The system processes 10K requests/sec at p99 latency of 23ms on 4× A100 GPUs" over "The system achieves high throughput"
- Prefer: "We chose PostgreSQL over MongoDB because our access patterns are primarily relational joins across 3 tables" over "We used PostgreSQL for storage"
- Version everything: "Python 3.11, PyTorch 2.1, CUDA 12.1"

## Prohibited Patterns
- Unquantified performance claims: "fast," "efficient," "scalable" without numbers
- Missing resource specs: benchmarks without hardware/config details
- Architecture without rationale: presenting design without explaining trade-offs considered
- Ignoring failure modes: systems papers must discuss what happens under edge cases
