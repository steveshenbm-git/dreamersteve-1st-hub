# Revision And Planner Return

Use this reference after a draft fails, user feedback identifies a problem, or imagegen detects that the brief cannot produce a credible result.

## Failure Categories

Name the visible failure before changing anything:

- **Intent drift:** the image no longer serves the original request or planner brief.
- **Semantic weakness:** named subjects, roles, relationship, direction, or result are not visible.
- **Visual weakness:** the message is right, but the form lacks hierarchy, craft, tension, material quality, or memorable structure.
- **Recognition mismatch:** the subject is misread as the wrong object, industry, application, or asset type.
- **Claim risk:** the image implies unverified product architecture, specs, certifications, customer use, installation, compliance, or performance.
- **Composition integration failure:** elements read as separate panels, pasted layers, hard splits, or disconnected blocks.
- **Regression failure:** the user-named issue remains visible compared with the prior version.
- **Strategy failure:** the image request conflicts with page goal, attention hierarchy, image role, claim boundary, or message ownership.

## Continue In Imagegen

Continue with imagegen when the strategy is sound but execution is weak:

- composition, crop, scale, silhouette, material, lighting, realism, or visual craft is poor
- subject recognition needs clearer cues without changing the page message
- physical structure needs rebuilding but the image role remains correct
- text, logo, CTA placement, color variants, crop, mask, compression, or file format can be fixed deterministically
- the user asks for local repair such as residue removal, sharper crop, cleaner text, or export sizing

Choose a materially different correction path when the previous one failed. Do not keep adjusting only color, glow, blur, gradient, opacity, or camera angle for a structural problem.

## Return To Planner

Return to `$jiangyue-website-planner` when:

- image responsibility is too broad, overloaded, or contradictory
- first-screen attention owner is unclear
- image role conflicts with page goal, H1, CTA, logo, or conversion path
- making the image work requires changing page copy, CTA, H1, section order, positioning, or claim boundary
- the brief asks imagegen to imply unverified product architecture, customer installation, certifications, specs, application use, or performance
- user feedback questions brand direction, layout integration, visual hierarchy, credibility for European B2B buyers, or whether the visual strategy is right
- two structural image revisions fail for the same reason
- the same user-stated problem remains visible after a previous imagegen revision

## Planner Return Format

```text
Imagegen return-to-planner request

- Failure attribution: execution issue / strategy issue
- Trigger for returning to planner:
- Why the current image request does not hold:
- Visual directions already tried and why they failed:
- Directions not recommended:
- Planner needs to decide:
  - Page goal:
  - First-screen attention hierarchy:
  - Image role:
  - Image vs HTML/page-copy responsibility:
  - Claim boundary:
- Question for planner:
```

Do not produce another draft until planner returns a revised image request brief or the user explicitly narrows the task.

## Revision Pass Criteria

A revised draft must visibly improve the named failure:

- intent drift: restored original job and message ownership
- semantic weakness: relationship and subject roles are readable without explanation
- visual weakness: stronger crop, silhouette, material, hierarchy, or structure
- recognition mismatch: clearer product/application/industry cues without new claim risk
- claim risk: risky details removed or abstracted
- composition integration failure: shared lighting, depth, mask, overlap logic, or spatial relationship replaces pasted panels
- regression failure: side-by-side comparison shows the named defect improved
