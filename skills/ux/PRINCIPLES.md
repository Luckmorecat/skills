# UX principles

Reference for auditing an interface. Each entry gives the rule, the symptom visible in a screenshot or walkthrough, and the usual fix. Project conventions found during inventory count alongside these; a consistent local convention beats a generic one.

## Evaluation methods

**Cognitive walkthrough.** At every step of a framed task, ask:

1. Will the user try to achieve the right result?
2. Will they notice that the correct action is available?
3. Will they associate that action with their goal?
4. After acting, will they see progress toward the goal?

Any "no" is a finding. The method matters most for new or unfamiliar interactions; standard patterns rarely need it. [NN/g](https://www.nngroup.com/articles/cognitive-walkthroughs/)

**Heuristics.** Tag each finding with what it violates: visibility of system status; match with the real world; user control and freedom; consistency and standards; error prevention; recognition over recall; flexibility and efficiency; aesthetic and minimalist design; error recognition and recovery; help and documentation. Use a WCAG success criterion instead when one applies. [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/)

**Severity (0–4).** 0 not a problem, 1 cosmetic, 2 minor, 3 major, 4 blocks the task. Rate by frequency, impact, and persistence: how many users hit it, whether they can recover, and whether it recurs every time. [NN/g](https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/)

**Limits of expert review.** It predicts problems; it does not observe them. It yields false positives, misses problems rooted in users' domain knowledge and mental models, and single evaluators miss many issues. Screenshots cannot show real latency, screen-reader output, or motion. State what was not verifiable. Polished visuals make users tolerate problems (aesthetic-usability effect); do not discount a finding because the screen looks good.

## System status and feedback

- **Acknowledge input within 0.1 s; keep waits under 1 s where possible; 10 s is the limit of attention.** Symptom: a click with no pressed state or change; a long wait with no progress. Fix: immediate visual response; spinner for a module or skeleton for a page from about 1 to 10 s; determinate progress with cancel beyond 10 s; nothing under 1 s, since a flashing spinner distracts. [NN/g](https://www.nngroup.com/articles/response-times-3-important-limits/), [skeletons](https://www.nngroup.com/articles/skeleton-screens/)
- **Keep state visible**: selection, current page or tab, active filters, saved or unsaved, online or offline. Symptom: no confirmation after save; unclear which filter applies.
- **Optimistic updates** only for reversible actions that rarely fail. On failure, roll back visibly and say why. Symptom: an item appears saved, then silently disappears.

## Signifiers

- **Interactive elements must look interactive.** Weak signifiers cost users time and confidence even when they see the element. [NN/g](https://www.nngroup.com/articles/flat-ui-less-attention-cause-uncertainty/) Symptoms: buttons as plain text; links indistinguishable from body text; unlabeled icons; low-contrast ghost buttons; decorative text styled like a link; cards clickable only in part. Fix: filled or outlined buttons; underlined links; icon labels, or at least a tooltip and an accessible name; whole-card hit areas.

## Errors

- **Prevent first**: constraints, safe defaults, pickers for bounded values, forgiving input formats (accept spaces and dashes).
- **Prefer undo to confirmation.** Routine confirmations are clicked through out of habit. Confirm only destructive, irreversible, or costly actions; name the object and consequence ("Delete 'Q3-report.pdf'?") and use specific verbs ("Delete file", "Keep file"), not Yes and No. Add friction, such as typing the name, only for the most dangerous. [NN/g](https://www.nngroup.com/articles/confirmation-dialog/) Symptoms: "Are you sure?" on routine actions; destructive action with neither undo nor confirmation; destructive button beside or styled like the primary.
- **Error messages** sit next to the problem, use text and icon rather than colour alone, say what went wrong in plain language and how to fix it, avoid blaming words such as "invalid", and preserve what the user entered. Modals only for severe errors. [NN/g](https://www.nngroup.com/articles/error-message-guidelines/) Symptoms: "An error occurred"; raw codes; a cleared form; errors listed only at the top of a long form; a red border without text.

## Cognitive load

- **Recognition over recall.** Show options, recent items, and context. Symptom: the user must remember a value from an earlier screen or type an identifier they cannot see.
- **Progressive disclosure.** Core options first, advanced behind one level of disclosure. Deep nesting hurts findability.
- **Defaults** are usually accepted, so pick the safe and common choice for the user, not for the business.
- **Choice count.** Hick's law applies to simple choices among familiar options. Grouping, ordering, and labelling matter more than count; flag poor grouping, not length alone. [Laws of UX](https://lawsofux.com/hicks-law/)
- **Absorb complexity.** Some complexity cannot be removed, only moved; the system should carry it rather than the user. [Tesler's law](https://lawsofux.com/teslers-law/)

## Targets

- **Size and distance.** Make frequent and primary targets large and near where the pointer or thumb already is; keep destructive targets away from frequent ones.
- **Minimums**: 24×24 CSS px or equivalent spacing (WCAG 2.5.8 AA); 44×44 pt on Apple platforms; 48×48 dp touch targets in Material. [WCAG](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) Symptoms: a 16 px close icon; small targets packed without gaps; checkbox labels that are not clickable.

## Hierarchy and layout

- **One clear primary action per view**; visual weight follows importance. Symptom: several equal primary buttons, or nothing stands out.
- **Proximity groups.** Related items sit closer than unrelated ones; a label sits nearer its own field than the next. Symptom: uniform spacing; labels equidistant between inputs.
- **Structure for scanning.** Descriptive headings and front-loaded keywords let users scan in a layer-cake pattern. F-shaped reading is the failure mode of unstructured text, not a layout to design for.
- **Distinctiveness draws attention**; reserve it for what matters and keep decoration from competing with the primary action.

## Forms

- **Visible labels above fields.** Placeholders are not labels: they vanish on input and usually fail contrast.
- **Single column.** Multiple columns cause skipped fields and misread order.
- **Validate after the field is complete** (on blur), never while typing; clear the error as soon as it is fixed. [Baymard](https://baymard.com/blog/inline-form-validation)
- **Make required fields unambiguous.** Conventions conflict: Baymard marks both required and optional, GOV.UK marks only optional. Flag ambiguity or inconsistency, not the chosen convention. [Baymard](https://baymard.com/blog/required-optional-form-fields), [GOV.UK](https://design-system.service.gov.uk/patterns/question-pages/)
- **Ask only for what is needed.** Every field costs completion; explain fields users may be reluctant to fill, such as phone numbers. [Baymard](https://baymard.com/blog/holistic-view-on-checkout-usability)
- **Input mechanics**: correct `type` and `inputmode`; `autocomplete` tokens; paste allowed; radios over dropdowns for short lists; field width hints at expected length; no split fields unless the format demands it. Long or complex flows benefit from one question per page.

## States

Audit each view in its ideal, empty, loading, partial, error, and first-run states.

- **Empty**: say what belongs here and offer the action that fills it. For no search results, echo the query and suggest a correction or broader filter. Symptom: a blank panel, "No data", or headers over an empty table.
- **Loading**: skeletons match the final layout to avoid shifts; load modules independently rather than blocking the page. Symptom: content jumps on arrival; a spinner that never ends.
- **Error and offline**: say what failed, what was kept, and offer retry. Do not discard content already loaded.
- **Partial**: show counts ("50 of 1,203"), freshness ("Updated 5 min ago"), and per-item failures.
- **First run**: tutorials and slide-deck onboarding do not improve task performance. Prefer contextual help at the moment it is needed; onboard only to collect required information or introduce a genuinely novel interaction. [NN/g](https://www.nngroup.com/articles/mobile-app-onboarding/) Symptom: a mandatory tour before any use; tips covering the controls they describe.

## Navigation

- **Show where the user is.** Highlight the current item; page titles match the link that led there; Back works as expected.
- **Do not hide primary navigation on desktop.** Hidden navigation is used far less than visible navigation on both desktop and mobile; on mobile, show links when there are four or fewer top-level items. [NN/g](https://www.nngroup.com/articles/hamburger-menus/)
- **Breadcrumbs** for hierarchies deeper than two levels, as a secondary aid.
- **Search**: a visible text field, not only an icon, where users expect it, tolerant of typos.
- **Label with users' words**, not internal or organisational names; avoid vague labels such as "Resources".

## Microcopy

- **Buttons name the outcome** ("Save changes", "Send invoice"), not "OK", "Submit", or "Yes".
- **Plain language**: short sentences, active voice, no internal jargon.
- **One term per concept** across the product.
- **Links make sense out of context** (WCAG 2.4.4). Symptom: repeated "Learn more" or "Click here".

## Consistency

- **Follow conventions users bring from elsewhere**: logo links home, magnifier means search, native controls behave natively. [Jakob's law](https://lawsofux.com/jakobs-law/)
- **Same control, same look and behaviour everywhere**; navigation and identification stay consistent across pages (WCAG 3.2.3, 3.2.4).
- **Follow the platform's button order** and keep it consistent within the product. Symptom: the primary button changes side between dialogs; one icon with two meanings; a custom dropdown that breaks keyboard or scroll behaviour.

## Accessibility

Baseline is WCAG 2.2 AA. WCAG 3 is still a working draft; do not audit against it. [WCAG 2.2](https://www.w3.org/TR/WCAG22/)

- **Contrast**: 4.5:1 for text, 3:1 for large text (1.4.3); 3:1 for component boundaries, icons, and focus indicators (1.4.11).
- **Colour is never the only cue** for errors, required fields, links, or chart series (1.4.1).
- **Keyboard**: everything operable (2.1.1), no traps (2.1.2), logical order (2.4.3), visible focus (2.4.7), and focus not entirely hidden by sticky headers, banners, or chat widgets (2.4.11). Symptom: `outline: none` without a replacement.
- **Names**: every control has a programmatic label that contains its visible text (1.3.1, 2.5.3, 4.1.2).
- **Dragging** has a single-pointer alternative, such as buttons or menus (2.5.7).
- **Redundant entry**: information already given in the same process is filled in or selectable (3.3.7).
- **Authentication** allows password managers and paste; no puzzle or transcription without an alternative (3.3.8). Symptom: paste blocked on a password or code field.
- **Help** appears in the same relative place on every page that offers it (3.2.6).
- **Motion and time**: respect `prefers-reduced-motion`; auto-moving content longer than 5 s can be paused (2.2.2); time limits are adjustable (2.2.1).
- **Zoom**: no horizontal scrolling at 320 CSS px width (1.4.10); text resizes to 200% (1.4.4); hover and focus popovers are dismissible, hoverable, and persistent (1.4.13).

## Anti-patterns

Deceptive patterns are findings of the highest severity regardless of business intent. [Taxonomy](https://www.deceptive.design/types)

- Confirmshaming ("No thanks, I don't like saving money").
- Easy to join, hard to cancel.
- Pre-checked add-ons, consent, or marketing boxes.
- Costs revealed only at the last step.
- Double negatives in opt-outs.
- Fake urgency or scarcity.
- Repeated prompts without a "never" option.
- Asymmetric choices, such as a large "Accept all" beside a faint "Reject".
- Trials that silently convert to paid.

Usability anti-patterns:

- Unlabeled mystery icons.
- Auto-rotating carousels holding key content.
- Modals or interstitials on load that block the task.
- Infinite scroll that hides the footer or loses position on Back.
- Disabled submit buttons with no stated reason; prefer allowing submission and showing errors.
- Hover-only disclosure on touch devices.
- Scroll-jacking.
- Key information available only in tooltips.
- Session timeouts that discard work.

## Myths

Do not raise these as findings.

| Claim | Reality |
| --- | --- |
| Menus must have at most 7±2 items | Miller measured recall of unfamiliar chunks; visible menus rely on recognition. [Laws of UX](https://lawsofux.com/millers-law/) |
| Everything must be within 3 clicks | Success and satisfaction do not drop after three clicks; clear labels and information scent matter. [NN/g](https://www.nngroup.com/articles/3-click-rule/) |
| Users don't scroll | They do, though the top still earns the most attention; place key content high without cramming. [NN/g](https://www.nngroup.com/articles/scrolling-and-attention/) |
| Fewer choices are always better | Only for simple, familiar choices; grouping matters more. |
| Design for the F-pattern | The F-pattern signals unstructured text; add headings instead. |
| Flat design is unusable | Weak signifiers cost time; flat design works with strong contrast and conventional layout. |
| Tutorials improve usability | No measured task-performance gain. |
| Top-aligned labels are mandatory | A good default from limited evidence; other placements are not severe. |
| Fixed font sizes or line lengths are rules | Conventions with weak direct evidence; zoom and reflow are the enforceable parts. |
| Carousels always fail | Flag auto-rotation and hidden key content, not carousels as such. |
