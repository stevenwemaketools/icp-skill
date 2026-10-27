# Path B worksheets: choosing a market before there are customers

Use with `method.md` section 3. The lead has no customers (or fewer than 10, or a new line of business). The output
is a hypothesis profile plus a plan to validate it with the next 10 customers.

## 1. What you know (B0)

Ask for the three sources Hormozi starts from, in one question with examples:
- a pain they lived and solved for themselves;
- a profession they are already paid for (the Y Combinator point: past experience in the space);
- a passion they will not quit after a bad month;
- and who they already know (former employers, colleagues, clients, communities).
A niche the lead knows nothing about fails before it starts: they do not know the lingo, the avatar, or the problems.

## 2. Candidate segments (B1)

Three to five. A segment is a group that buys similar things, has similar sales cycles, and talks to each other
(Aulet). "Small businesses" is not a segment. "Independent dental clinics with 2 to 5 dentists in Texas" is.
If the lead is blank, propose candidates from B0: the people they served before, the people like them, and an
underserved adjacent group.

## 3. Scorecard per segment (B2)

Score each candidate on the four market indicators (1 to 10 each, total out of 40):

| Indicator | 1 to 3 | 4 to 7 | 8 to 10 |
|---|---|---|---|
| Pain | a nice-to-have; nothing gets worse if they wait | a real cost they tolerate | urgent, measurable, gets worse every month |
| Purchasing power | would need a loan or a committee | can pay, with hesitation | pays without blinking; already pays for worse |
| Easy to target | no list, no community, no event | reachable through two or three channels | congregated: a list exists, a community, an event, an ally who sells to them |
| Growing | shrinking or seasonal | flat | more of them every year |

Bands: 32 to 40 strong · 24 to 31 attractive · 16 to 23 difficult · 15 or less weak. Below 24, do not pick it.

Then Aulet's beachhead criteria, 1 to 5 each (used to break ties and to explain the pick):

| Criterion | Question |
|---|---|
| Customer money | Is the target customer well funded? |
| Accessibility | Can the lead reach them directly, today? |
| Reason to buy | Do they have a compelling reason to buy now? |
| Whole product | Can the lead deliver the complete solution, alone or with partners? |
| Competition | Is there entrenched competition that will block them? (5 = little) |
| Expansion | Does winning this segment open adjacent ones? |
| Founder fit | Does it fit the lead's experience, values and goals? |

Pick the highest total. If the lead picks a lower one, write the reason in `evidence.basis`. Record every candidate
in `evidence.segments_considered` with `picked: true` on exactly one.

## 4. The problem and the money question (B3)

Hormozi's three questions, asked in the lead's words: where is the problem; how much do they think it is a problem;
can you solve it and charge for it. The answer to the second one becomes the pain language of the profile.

## 5. Hypothesis avatar and niche ladder (B4)

Write 3 to 5 qualifiers that are observable (size, volume, role, tool, location, trigger). Then walk the ladder:
start one rung too broad, narrow one descriptor at a time, and stop one rung before the 100-in-a-week test fails.
Write the rungs into `evidence.niche_ladder` so the reader sees why the profile is this narrow and not narrower.

## 6. Anti-ICP (B6)

Three to six groups the lead will decline, each with a why. For a new business the most useful anti-ICP entries
are the ones that look like easy money: the too-small, the enterprise with procurement, the customer who wants a
different product.

## 7. Next 10 customers and the validation plan

Name 5 to 10 real or realistic first customers (`next_10_customers`). Plan inquiry-mode interviews (Aulet): show
the problem and the offer, ask, listen, do not sell. Measure real enthusiasm, not politeness. The profile is
confirmed when the next 10 fit the requirements and buy faster than strangers do; if they do not, adjust one
qualifier and test again. Rerun Path A at 10 to 20 customers.
