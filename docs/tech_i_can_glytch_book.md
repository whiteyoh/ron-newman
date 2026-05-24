# Tech I Can: Glytch

## Preface

Glytch was built for one practical reason: many people are asked to use AI before they are given a clear way to judge it.

Most learners are shown a chat interface, a prompt, and a polished output. They are not always shown what changed between a quick answer and a controlled workflow with checks, evidence, review points, and accountability.

This book makes that journey visible.

You do not need to be a software engineer to use this material. You need curiosity, caution, and a willingness to compare what AI produces at different levels of structure.

## Disclaimer

Glytch is a workshop-safe simulation for education and discussion.

It is not a production automation platform, not a decision engine for high-stakes contexts, and not a replacement for teacher, manager, or professional judgement.

Always apply local safeguarding, data protection, and policy requirements in school and workplace environments.

## About the Author

Teaching intent: The teaching intent is simple: clear steps, honest evidence,
and confidence through practice.

I'm Paul McMurray, a software engineer, problem-solver, and lifelong learner
from the North East of England.

My work has taken me deep into the world of technology, reliability,
automation, and complex systems, but the part I enjoy most is making difficult
things easier to understand. Whether I'm building tools, improving systems,
writing guidance, or helping others find a clearer way forward, I'm drawn to
practical ideas that make a real difference.

Outside of work, I'm a dad, a music lover, and someone who believes in staying
curious. I enjoy soul, funk, and disco, long walks, good food, and finding new
ways to teach my son how the world works - from computers and games to
kindness, resilience, and asking good questions.

This book is personal to me because it reflects how I think: take something
complicated, break it down, make it useful, and leave people with something
they can actually do.

I don't pretend to have all the answers, but I've learned that progress often
starts with asking better questions, being honest about what you don't know,
and being willing to keep going.

---

# Chapter 1: AI Beyond The Chat Box

## About this chapter

This chapter sets the foundation for the whole book. You will frame AI as a capability journey, not a tool popularity contest. The goal is to make clear why one prompt can be useful for some tasks but risky for others.

## What you are going to use

- Glytch running locally
- one safe scenario
- your observation notes

## What you will learn in this chapter

- why polished output is not enough
- how to separate fluency from reliability
- how Glytch levels support comparison

## The work, clearly laid out

1. choose one scenario
2. run Level 1 once
3. list what is useful and what is uncertain
4. define one human review checkpoint

## Examples of what you might see

- clear wording but unsupported claims
- confident tone with missing caveats
- useful starting structure that still needs review

## Why This Matters

People often trust style before they test quality. That is risky in classrooms, teams, and public services. Early awareness reduces over-trust and creates better habits.

## Action 1: What You Learned

- A clean answer can still hide weak assumptions.
- Human review is not optional for meaningful tasks.
- AI literacy starts with process awareness.

## Action 2: Reflect

- Which part of the Level 1 output would you verify first?
- What looked convincing but remained unproven?
- What should never be accepted without review in your context?

## Action 3: Do This Next

- Pair with a colleague and compare your risk notes for the same output.
- Share one verification checklist item with your group.

---

# Chapter 2: The Lowest Safe Level Principle

## About this chapter

This chapter introduces the central decision rule in Glytch: use the lowest level that safely gets the task done. You will learn why higher complexity is sometimes justified and sometimes wasteful.

## What you are going to use

- one repeated scenario
- Level 1 and Level 3 runs
- a side-by-side comparison table

## What you will learn in this chapter

- what changes between prompt and checked workflow
- how to choose level based on risk
- why "more advanced" does not automatically mean "better"

## The work, clearly laid out

1. run Level 1 for baseline
2. run Level 3 on the same prompt
3. compare claims, checks, and confidence
4. decide which level is sufficient

## Examples of what you might see

- Level 3 adds clearer intermediate logic
- tool-assisted checks reduce obvious arithmetic errors
- baseline remains faster for low-risk drafting

## The 8 levels, layer by layer

This section gives a practical understanding of what each level adds, what that
layer is doing, and what users should understand before moving up.

### Level 1 - Prompt baseline

What this layer does:
- Takes one prompt and returns one draft response.
- Keeps human decision-making fully external.

What users should understand:
- Fast drafting value is high.
- Reliability and traceability are low unless the user adds checks manually.

Best use:
- Early brainstorming, wording ideas, low-risk first drafts.

### Level 2 - Instruction framing

What this layer does:
- Adds stronger instructions, constraints, and output format expectations.
- Reduces ambiguity compared with raw prompting.

What users should understand:
- Better structure does not guarantee correctness.
- Compliance with format can hide weak reasoning if evidence is not checked.

Best use:
- Structured summaries, checklists, first-pass procedural outputs.

### Level 3 - Tool and check integration

What this layer does:
- Uses bounded helper tools and checkable intermediate steps.
- Makes parts of the run more inspectable than pure prompting.

What users should understand:
- Tool output can improve consistency but still needs interpretation.
- Human review is still required for edge cases and context.

Best use:
- Tasks where small calculation or retrieval checks reduce avoidable mistakes.

### Level 4 - Evidence grounding

What this layer does:
- Links claims to supplied source material.
- Encourages answer construction from known context instead of free-form guessing.

What users should understand:
- Grounding improves auditability.
- Missing or weak source material still leads to weak outputs.

Best use:
- Fact-sensitive educational, operational, or policy discussions.

### Level 5 - Planning and decomposition

What this layer does:
- Breaks broad tasks into explicit sub-steps.
- Makes process intent visible before final output.

What users should understand:
- Better planning can reduce confusion.
- Excess planning can add overhead for simple tasks.

Best use:
- Multi-step tasks where order and scope matter.

### Level 6 - Critique and revision

What this layer does:
- Produces draft, critique, and improved draft flow.
- Separates initial generation from quality improvement.

What users should understand:
- Revision improves clarity and robustness when critique criteria are strong.
- Polished wording after revision is still not proof of truth.

Best use:
- Deliverables that need quality uplift before human approval.

### Level 7 - Controlled loop

What this layer does:
- Repeats observe-act-check style cycles with boundaries.
- Adds explicit stop and control mechanics.

What users should understand:
- Loops increase process power and process risk.
- Stop conditions and escalation criteria must be clear.

Best use:
- Iterative tasks where each pass should be reviewed against a goal.

### Level 8 - Orchestration

What this layer does:
- Coordinates specialist worker roles with verifier and approval gates.
- Produces taskboard, merge decision path, and final status signal.

What users should understand:
- Highest structure means highest governance burden.
- A merged status is a process result, not automatic factual validity.

Best use:
- Complex tasks where coordination, traceability, and explicit human approvals are essential.

### Quick comparison table

| Level | Primary value | Main risk if misused |
|---|---|---|
| 1 | speed and ideation | over-trust in fluent draft text |
| 2 | clearer structure | false confidence from tidy formatting |
| 3 | checkable helper steps | tool output accepted without context review |
| 4 | evidence traceability | weak source quality mistaken for strong evidence |
| 5 | process clarity | unnecessary complexity for simple work |
| 6 | quality improvement loop | polish mistaken for correctness |
| 7 | bounded iteration | control drift if stop rules are weak |
| 8 | coordinated governance | process confidence replacing human judgement |

## Why This Matters

Teams waste time when they over-engineer small tasks and create risk when they under-control important tasks. The lowest safe level principle balances both.

## Action 1: What You Learned

- Level choice should follow task risk, not feature excitement.
- Checks add value when mistakes are costly.
- Simpler flow can be the right answer.

## Action 2: Reflect

- Which scenario in your school or team is over-complicated today?
- Which scenario is under-checked and needs more control?
- How would you explain "lowest safe level" to a new colleague?

## Action 3: Do This Next

- Work in pairs to classify three tasks by appropriate level.
- Compare your classifications with another pair and resolve disagreements.

---

# Chapter 3: Evidence And Grounding

## About this chapter

This chapter focuses on Level 4 behavior and the difference between unsupported claims and evidence-tied claims.
You will practice tracing claims to provided material so learners can see what is substantiated, what is uncertain, and what should be revised before use.

## What you are going to use

- Level 4 run
- teacher-provided or facilitator-provided source notes
- a claim-check table

## What you will learn in this chapter

- what grounding looks like in output
- how to inspect whether claims map to supplied material
- where evidence still leaves judgement questions open

## The work, clearly laid out

1. run a scenario with evidence notes
2. highlight claims in the output
3. map each claim to provided evidence
4. flag unsupported statements

## Examples of what you might see

- direct claims that clearly map to source material
- generic claims not supported by provided notes
- mixed outputs where only part of the answer is grounded

## Why This Matters

Evidence discipline is essential in education, operations, and public communication. Grounding creates traceability and reduces accidental misinformation.

## Action 1: What You Learned

- Evidence-backed statements are easier to trust and audit.
- Unsupported claims should be treated as draft material.
- Grounding reduces, but does not eliminate, risk.

## Action 2: Reflect

- Which claim from your run had the strongest evidence link?
- Which claim should be removed until better support exists?
- What evidence standard should your team adopt?

## Action 3: Do This Next

- Swap outputs with a partner and run independent claim checks.
- Build a shared evidence checklist with your group.

---

# Chapter 4: Critique And Revision

## About this chapter

This chapter explores Level 6 patterns where the first draft is reviewed and improved before wider use.
You will look at revision quality in practical terms: clearer structure, stronger caveats, better reasoning flow, and reduced risk language before any release decision.

## What you are going to use

- Level 6 output
- critique notes
- revised output comparison

## What you will learn in this chapter

- why first draft quality is only a starting point
- how critique changes reliability and clarity
- when revision loops should stop

## The work, clearly laid out

1. run Level 6 once
2. identify weak points in the first draft
3. review revised output
4. assess if revision addressed the weaknesses

## Examples of what you might see

- improved structure after critique
- clearer caveats in revised text
- unresolved risk despite stylistic polish

## Why This Matters

Many AI failures happen because first drafts are treated as final. Revision introduces accountability and reduces avoidable errors.

## Action 1: What You Learned

- Revision is a quality process, not an optional extra.
- Strong critique criteria produce better second drafts.
- Not every revision cycle improves truthfulness.

## Action 2: Reflect

- Which critique point produced the biggest improvement?
- What risk remained after revision?
- When should a human decide to stop revising and escalate?

## Action 3: Do This Next

- Pair with a classmate to critique each other’s run outputs.
- Agree one common revision rubric for your team.

---

# Chapter 5: Controlled Loops And Limits

## About this chapter

This chapter introduces loop-based behavior and control boundaries. You will focus on how repeated AI actions need explicit stop conditions and monitoring.

## What you are going to use

- Level 7 run
- loop summary
- stop-condition checklist

## What you will learn in this chapter

- why loops can help and harm
- how to interpret loop status safely
- what stop rules should be explicit

## The work, clearly laid out

1. run Level 7
2. inspect loop phases
3. identify stop and check conditions
4. record one potential runaway risk

## Examples of what you might see

- clear observe-act-check progression
- incomplete checks in one iteration
- loop output that still needs human approval

## Why This Matters

Without clear boundaries, iterative systems can amplify mistakes quickly. Responsible loop design improves safety and predictability.

## Action 1: What You Learned

- Loops need clear limits and accountability.
- Repetition without verification can increase error propagation.
- Human checkpoints remain essential.

## Action 2: Reflect

- Which stop condition felt most important in your run?
- What signal would tell you to halt the loop?
- How would you explain loop safety to a beginner group?

## Action 3: Do This Next

- In small groups, draft a loop stop-policy card for one scenario.
- Compare cards and agree the strongest boundary language.

---

# Chapter 6: Orchestration And Taskboards

## About this chapter

This chapter centers on Level 8, where multiple worker roles coordinate through verification and approval gates.
You will focus on interpreting orchestration signals responsibly so teams can avoid false confidence and keep named human accountability at final decision points.

## What you are going to use

- Level 8 run
- taskboard view
- approval and merge summary

## What you will learn in this chapter

- how worker decomposition changes workflow
- what verifier and approval gates signal
- why "merged" is not the same as "perfect"

## The work, clearly laid out

1. run Level 8 with your scenario
2. inspect each worker output summary
3. review verifier and approval fields
4. decide whether you would release or revise

## Examples of what you might see

- one worker blocked while others complete
- verifier warning before merge
- merge deferred pending human review

## Why This Matters

Orchestration adds control possibilities and new failure points. Understanding both is critical for responsible deployment decisions.

## Action 1: What You Learned

- Coordination does not remove review obligations.
- Merge outcomes are process indicators, not truth guarantees.
- Worker specialization can improve clarity when roles are explicit.

## Action 2: Reflect

- Which worker role added the most value in your run?
- Where could orchestration create false confidence?
- What should always require a named human approver?

## Action 3: Do This Next

- Review another team’s taskboard and challenge one merge decision.
- Co-design a two-person approval workflow with a partner.

---

# Chapter 7: Classroom Delivery And Assessment

## About this chapter

This chapter helps educators and facilitators run effective sessions, keep safety boundaries visible, and collect useful learning evidence.
You will connect classroom design decisions to practical outcomes so each session produces better discussion, clearer reflection, and safer AI use habits.

## What you are going to use

- teacher guide
- student worksheet
- one session reflection template

## What you will learn in this chapter

- how to sequence levels in limited time
- which misconceptions to address early
- how to evaluate understanding without overloading learners

## The work, clearly laid out

1. choose a 20, 45, or 90 minute format
2. select one safe scenario
3. run levels with comparison prompts
4. collect learner reflections and level justifications

## Examples of what you might see

- learners equating confidence with correctness
- learners over-valuing higher levels
- stronger reflection quality after side-by-side comparisons

## Why This Matters

AI literacy succeeds when learners can justify decisions, not when they memorize terms. Structured reflection builds transferable judgement.

## Action 1: What You Learned

- Time-boxed comparison is often more effective than feature tours.
- Misconceptions are predictable and teachable.
- Reflection prompts can surface true understanding.

## Action 2: Reflect

- Which prompt generated the best learner reasoning?
- What misconception appeared most often in your context?
- How can you make safety boundaries more visible next session?

## Action 3: Do This Next

- Run a paired facilitation rehearsal with a colleague.
- Exchange student worksheet feedback with another teacher.

---

# Chapter 8: Pilot Planning And Continuous Improvement

## About this chapter

This chapter explains how to run a small pilot, gather meaningful feedback, and improve your rollout responsibly.
You will use pilot evidence to decide what should scale, what should change, and what needs stronger controls before broader adoption.

## What you are going to use

- pilot plan template
- before-and-after confidence prompts
- release gate checklist

## What you will learn in this chapter

- how to start small and measure clearly
- what evidence should guide iteration
- how to decide readiness for wider rollout

## The work, clearly laid out

1. choose one cohort
2. run one baseline session
3. collect confidence and clarity signals
4. review gaps and revise materials

## Examples of what you might see

- confidence increase but uncertainty about evidence standards
- strong staff engagement with workflow detail
- need for clearer guidance on human approval gates

## Why This Matters

Pilots reduce rollout risk, reveal practical teaching gaps, and create evidence for informed scaling decisions.

## Action 1: What You Learned

- Small pilots create higher-quality improvements than big launches.
- Feedback should include both confidence and caution signals.
- Release gates prevent quality drift.

## Action 2: Reflect

- What one indicator best shows your pilot helped judgement?
- Which uncertainty remained strongest after the session?
- What should be improved before expanding to more groups?

## Action 3: Do This Next

- Debrief pilot findings with a partner team.
- Co-author one improvement sprint plan with clear owners.

---

## References (APA 7th Edition)

Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency*, 610-623.

Floridi, L., & Cowls, J. (2019). A unified framework of five principles for AI in society. *Harvard Data Science Review, 1*(1).

Ng, A. (2021). *Machine learning yearning* (Draft).

OpenAI. (2024). Usage policies. https://openai.com/policies

UNESCO. (2021). *Recommendation on the ethics of artificial intelligence*. UNESCO Publishing.

---

## One-line close

Glytch helps people build practical AI judgement by making workflow control, evidence, and human review visible.
