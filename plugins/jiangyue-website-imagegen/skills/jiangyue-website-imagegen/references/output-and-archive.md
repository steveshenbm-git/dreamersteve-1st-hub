# Output And Archive

Use this reference when saving Jiangyue website image outputs.

## Folder Structure

Use the fixed Jiangyue project output root. Each meaningful option/draft gets one short task folder so later conversations and tools can locate it without depending on a conversation title.

```text
/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images/{content-type}/{page-or-type}-{image-role}-{option-code}-draft-{number}/
```

Recommended content folders:

- `home/`
- `product/`
- `application/`
- `about-us/`
- `contact/`
- `technical-resources/`
- `brand/`
- `shared/`

Use short lowercase kebab-case names. Keep the task folder limited to page/type, image role, a short option code such as `a1`, `a2`, or `b1`, and the draft number:

```text
/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images/home/home-hero-a1-draft-1/
/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images/product/product-controller-a1-draft-1/
```

Use clear short filenames inside each task folder:

```text
{page-or-section}-{position}-{draft-or-final}-{number}.{ext}
```

Examples:

- `home-hero-draft-01.png`
- `product-hero-final-01.png`
- `contact-hero-draft-02.png`

Avoid scattering files directly under `{content-type}`. Avoid conversation-title folders, Chinese numbered process folders, long prompt fragments, repeated company names, repeated category words, and date-first task folders. Keep revisions and source/review/output subfolders inside the matching short task folder when they belong to the same accepted direction.

## Archive Levels

### Trial

Use for exploratory or clearly not-yet-usable output.

Minimum structure:

- `output/` for local test PNG/JPG/WebP files
- `source/` only for inputs needed to inspect or reuse the trial
- `trial-note.md` only when the trial changed the concept or contains useful learning

Do not create full production documentation for every trial.

### Usable Draft

Use when the image passes basic intent, composition, size, and artifact review and may be shown for decision.

Include when applicable:

- `README.md` or `REPRODUCTION.md`
- `recipe.json` for compact reusable parameters
- `source/` for generated bases, references, masks, SVGs, or editable inputs
- `scripts/` for deterministic rebuild scripts
- `output/` for exported assets
- `review/` for thumbnails or comparison images

### Final

Use when the user accepts the visual or it is production-intended.

Update the usable draft archive with final outputs, final dimensions, source files, exact text, fonts, colors, crop boxes, masks, export settings, prompts, model/tool metadata, revision history, known non-reproducible parts, and fast edit instructions.

Use `references/reproduction-archive-template.md` for the full archive format.

## Efficiency Rules

- Preserve generated base images and make later edits on top when possible.
- Use deterministic edits for text, CTA, logo placement, cropping, masks, color variants, layout variants, and compression.
- Do not force a new image generation round for changes that can be handled with saved source assets or deterministic scripts.
- Do not promise exact regeneration for AI-generated imagery unless seed, model version, inputs, and tool behavior are available and verified.

## Delivery Report

Report:

- final file path
- task folder path
- reproduction archive path, or `not created yet` for trial-only outputs
- dimensions and format
- production method
- what was visually verified
- what could not be verified
- remaining limitation, if any

Only claim browser, mobile, SEO, compression, WordPress behavior, or exact reproducibility when those checks were actually performed.
