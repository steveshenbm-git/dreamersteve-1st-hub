# Reproduction Archive Template

Use this template for each usable draft, accepted draft, final, or meaningful revision folder. Keep it concise and practical. The goal is fast reuse: a future agent should be able to rebuild this exact version, make common edits, or understand non-reproducible parts without rereading the chat history.

Do not create this full archive for every exploratory trial image. For trial-only outputs, keep the local test image in the version folder and add only a short `trial-note.md` when the trial contains reusable learning.

Create this as `REPRODUCTION.md` in each version folder, for example:

```text
outputs/jiangyue-website-images/home/2026-06-18-pmsm-drive-hero-draft-01/REPRODUCTION.md
outputs/jiangyue-website-images/home/2026-06-18-pmsm-drive-hero-final/REPRODUCTION.md
```

```text
# Image Reproduction Archive

## Task

- Content type:
- Task slug:
- Date:
- Version: draft-01 / draft-02 / draft-03 / final / revision-01
- Previous version folder:
- Next version folder:
- Request summary:
- Page / usage:
- Final selected image:
- Dimensions:

## Intent Lock

- Original job:
- Core message:
- Image must communicate:
- HTML / page copy carries:
- Must not become:

## Output Files

- Output image(s):
- Variants:
- Review images:

## Source Inputs

- Base image(s):
- Reference image(s):
- Logo / brand assets:
- Fonts:
- Other inputs:

## Production Method

- Method: deterministic / AI-generated / image-edit / hybrid
- Tooling:
- Runtime:
- Rebuild command:

## Editable Parameters

- Text:
- Font settings:
- Colors:
- Layout constants:
- Crop / mask settings:
- Export settings:

## AI Generation Record

Use this section only when an AI model generated or edited pixels.

- Tool / model:
- Prompt:
- Negative constraints:
- Reference inputs:
- Seed / generation ID, if available:
- Non-reproducible limitations:

## Revision History

- This version:
- Changes from previous version:
- Reason for changes:
- User / planner feedback addressed:
- Remaining issues:

## Fast Edit Guide

- To change copy:
- To change logo color:
- To change crop:
- To adjust left/right balance:
- To export again:

## Verification

- Checked dimensions:
- Checked text:
- Checked visual defects:
- Not checked:
```

When the output is deterministic or hybrid, also create a compact `recipe.json` next to this file. Keep values machine-readable and avoid long prose.

```json
{
  "task_slug": "",
  "content_type": "home|product|application|about-us|contact|technical-resources|brand|shared",
  "date": "",
  "version": "draft-01|draft-02|draft-03|final|revision-01",
  "previous_version_folder": "",
  "next_version_folder": "",
  "method": "deterministic|ai-generated|image-edit|hybrid",
  "final_outputs": [],
  "source_inputs": [],
  "scripts": [],
  "rebuild_command": "",
  "text": {},
  "fonts": {},
  "colors": {},
  "layout": {},
  "export": {},
  "ai_generation": {
    "tool": "",
    "model": "",
    "prompt_ref": "",
    "seed_or_generation_id": "",
    "exact_regeneration_verified": false
  }
}
```

Do not use the archive as a design essay. Put design rationale in the revision history only when it affects how to reproduce or modify the image.
