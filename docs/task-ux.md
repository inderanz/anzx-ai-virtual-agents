
**Acceptance**
- Component/file path reported.
- Tags present and unique.

**Tests**
- Devtools: querySelectorAll('[data-testid^="cricket-"]').length >= 3
- No visual diffs on page load.

## 1) Hero That Moves (priority)

### 1.1 Animated Background (CSS, cheap on GPU)
Replace the hero background with CSS gradients + subtle conic rotation:

Deep navy → teal; add soft radial highlights.

Animation period ~20s; guard with prefers-reduced-motion.

No heavy canvas/WebGL.

**Acceptance**
- Smooth animation on desktop; disabled when prefers-reduced-motion is on.
- No CLS/LCP regressions (hero renders instantly).

**Tests**
- Lighthouse Performance ≥ 90 after change.
- OS-level "Reduce Motion" disables animation.

### 1.2 Product Visual (Chat Preview Card) + Dual CTAs

Inside hero, add a compact animated "chat + reply" card:

Show a real example from current page (fixtures/ladder).

Stream text in (typing dots → content).
Add primary CTA: "Try the Cricket Agent" and secondary: "Watch 60-sec Demo".


**Acceptance**
- Card shows one example and streams its reply.
- CTAs visible above the fold on 1440×900 and mobile 390×844.

**Tests**
- Click "Watch 60-sec Demo" opens modal/video (placeholder ok).
- a11y: buttons have accessible names; focus order correct.

### 1.3 Trust Row in Hero

Surface compliance/trust badges directly under CTAs:

"Australian Hosted", "SOC 2 Compliant", "Privacy Act compliant".
Use grayscale → color on hover. Keep originals in footer too.

**Acceptance**
- Badges render in hero and footer; consistent style.

**Tests**
- Contrast AA for label text.
- Hover state only on pointer devices (no accidental tap highlight on mobile).


## 2) Make Chat the Star (persistent, mobile‑first)

### 2.1 Persistent Chat Dock

Add <ChatDock/> mounted in /cricket layout:

Desktop: right panel 420–520px, collapsible.

Mobile: bottom sheet covering 92–96% height; open via 64px FAB.

Persist state in ?chat=1 + localStorage (thread, draft, scroll).

Do not cover hero CTAs when collapsed.

**Acceptance**
- Chat survives refresh and route changes.
- FAB never overlaps iOS home indicator (safe areas).

**Tests**
- Open/close dock; refresh page → state restored.
- iPhone Safari: keyboard open does not push content off screen.

### 2.2 Full‑Page Chat Route

Add route /cricket/chat that shares the same chat state with <ChatDock/>.
Add link "Open full chat" in hero and sticky header; add breadcrumb back.

**Acceptance**
- Seamless switch dock ↔ full page without losing thread/draft.

**Tests**
- Navigate back/forth: scroll and input preserved.

### 2.3 Streaming & Smart Autoscroll

Implement token streaming:

Typing dots → token stream (200–500ms jitter).

Stick-to-bottom only if user is at bottom; show "New messages" pill otherwise.

Virtualize message list >200 nodes.

Actions: Copy, Retry, Regenerate.

**Acceptance**
- No jank during long streams.
- Scroll never snaps unexpectedly when scrolled up.

**Tests**
- 300-message conversation remains smooth (60fps target).
- Copy/regenerate work with keyboard and screen reader.


## 3) Turn “What You Can Ask” Into Scannable Value Cards

### 3.1 Feature Cards (4)

Transform the existing "What You Can Ask" into 4 cards:

Player Info, Fixtures, Ladder, Stats.
For each card:

Icon (lucide/phosphor), one-line value prop, 1–2 real examples from current page.

Staggered reveal on scroll; hover lift/glow on desktop only.

**Acceptance**
- All existing examples preserved (no deletions), now grouped.

**Tests**
- Tab through cards: clear focus states; contrast AA.
- Motion turns off with prefers-reduced-motion.

### 3.2 Inline “Live Demo”

Below the cards, add 3 prompt chips using real examples:

"Fixtures for Blue U10 this week"

"Ladder position for White U10"

"Who scored most runs last match?"
On click: insert into input and auto-send; stream mocked reply; show CTA "Connect your club data".

**Acceptance**
- Chips insert/submit; streaming works; CTA visible.

**Tests**
- Keyboard users can focus/activate chips.
- Mobile: tapping chip scrolls input into view without jump.

## 4) Outcomes + Social Proof

### 4.1 Metrics Row

Add 3 KPIs with count-up:

- "<10s to answer fixtures"

- "100% club coverage"

- "24/7 availability"
- Provide data attributes for analytics.

**Acceptance**
- Numbers animate once in view; readable on mobile.

**Tests**
- Prefers-reduced-motion: disable count-up (instant render).

### 4.2 Testimonial

Add a testimonial glass card:

Quote: "Cut team admin by 85% with ANZX Cricket Agent."

Club logo placeholder.

Left-to-right fade; strong contrast; alt text on logo.

**Acceptance**
- Card passes AA contrast; logo has meaningful alt or aria-hidden if decorative.

**Tests**
- Screen reader reads quote and attribution correctly.

## 5) Navigation & Footer Polish

### 5.1 Sticky Header with CTA State

Make header sticky; on scroll add shadow + solid background.
CTA "Get Started" transitions from outline→filled after 80px scroll.

**Acceptance**
- No layout shift; CTA remains visible; keyboard focus preserved.

**Tests**
- Tab navigation unaffected; scroll performance stays smooth.

### 5.2 Footer Columns + Trust Consistency

Restructure footer into 4 columns: Product | Company | Legal | Social.
Keep all existing links; normalize trust/compliance icon sizes; add newsletter input with inline validation.

**Acceptance**
- Links unchanged; icons aligned; email validation with error text for invalid input.

**Tests**
- Screen reader labels for input + error; AA contrast on footer text.

## 6) Motion System (tasteful, accessible)

Create a motion utils module:

- Default entrance: fade+slide (y=16, 0.5s ease-out).

- Button hover: scale 1.02, 120ms.

- Gate all animations by prefers-reduced-motion.
- Apply to hero, feature cards, testimonial, metrics.

**Acceptance**
- Consistent easing/timing; motion disabled with system setting.

**Tests**
- Visual regression: animations not double-triggering on route changes.

## 7) Performance & Accessibility (enterprise bar)

### 7.1 Performance

Optimize assets and delivery:

- Convert images to WebP/AVIF.

- Lazy-load below-the-fold sections (demo, testimonial, metrics).

- Inline critical CSS for hero.

- Preconnect to API host; defer analytics scripts.

**Acceptance**
- LCP ≤ 2.5s desktop/3.0s mobile (lab), CLS ~0.00, TBT improved.

**Tests**
- Lighthouse Performance ≥ 90 mobile & desktop.
- Network throttling Fast 3G still usable.

### 7.2 Accessibility

Enforce WCAG AA on /cricket:

- Single <h1> in hero; logical h2/h3 hierarchy.

- Focus visible on all interactive elements.

- Contrast ≥ 4.5:1.

- Chat thread uses: <section role="log" aria-live="polite" aria-relevant="additions text">.

- All icons decorative → aria-hidden; meaningful icons have labels.

**Acceptance**
- Lighthouse Accessibility ≥ 95.

**Tests**
- VoiceOver/NVDA: new messages announced; keyboard-only can reach all controls.

### 7.3 SEO

Add page-specific meta:

- Unique <title> and <meta name="description">.

- Open Graph + Twitter card (image from hero).

- FAQ JSON-LD (3–4 Q&As) built from current examples.

**Acceptance**
- Meta present and valid; structured data passes Google Rich Results test.

**Tests**
- Inspect meta tags; JSON-LD validates without errors.

## 8) Analytics & SLOs


Instrument product analytics:

- Events: chat_opened, prompt_sent, time_to_first_token_ms, tokens_streamed,
- tool_card_viewed, failure_shown, retry_clicked, mobile_keyboard_open.
Add a light SLO dashboard:

- p95 time-to-first-token, p95 render per chunk, error rate, % mobile crash-free.

**Acceptance**
- Events fire with useful context (device, viewport, network).
- Thresholds documented (e.g., p95 TTFB ≤ 1.2s); alerts configured.

**Tests**
- Verify events in analytics console; simulate slow network and see SLOs change.

## 9) QA Matrix (blocker if fails)

Run manual and automated checks on:

- Devices: iPhone 13/15 Safari, Pixel 6/8 Chrome, Samsung S22 Chrome, iPad, Mac/Win (Chrome/Safari/Edge/Firefox).

- Scenarios: landscape/portrait, slow 3G, offline/online, long thread (300+ messages), IME input, attach/cancel, retry after network blip.
Record issues as tickets; do not ship if any P0 remains.

**Acceptance**
- All checks pass; P0/P1 closed.

**Tests**
- Session replay shows smooth streaming; no layout jumps on keyboard open/close.



## 10) Final Ship Checklist

- [ ] Hero: animated, product chat card streaming, CTAs, trust row.
- [ ] ChatDock persistent + /cricket/chat full-page, shared state.
- [ ] Feature cards (4) + Live Demo chips streaming.
- [ ] Metrics row + testimonial.
- [ ] Sticky header + polished footer.
- [ ] Motion system consistent; respects reduced motion.
- [ ] Perf: WebP/AVIF, lazy-load, inline critical CSS, preconnect, defer.
- [ ] A11y: AA contrast, ARIA roles, focus, semantic headings.
- [ ] SEO: unique title/description, OG/Twitter, FAQ JSON-LD.
- [ ] Analytics/SLOs and QA matrix passed.



Create a <AnimatedHeadline /> that renders:
"Intelligent " + [cycling phrase]

Requirements:
- Fixed word: "Intelligent" (no animation).
- Cycling words (in order): "Cricket Assistant", "Cricket Expert", "Cricket Agent", "Team Manager", "Team Assistant".
- Animate the changing word with a slide-up + fade (out → in) every 1800ms.
- Use Framer Motion's AnimatePresence with reduced-motion support.
- Accessibility: wrap only the changing word in aria-live="polite" so SRs announce updates without re-reading "Intelligent".
- Performance: pause when not in viewport (IntersectionObserver) and when prefers-reduced-motion is set.
- Provide 'speedMs' and 'words' props for configurability.


In the HeroCricket component, update the supporting paragraph ("Get real-time information about fixtures..."):

- Typography: font-semibold, text-lg on mobile, text-xl on md+.
- Color: text-teal-300 (or a brand-accent gradient from cyan to teal).
- Add bg-clip-text with gradient and text-transparent for premium look.
- Max width: 40rem, centered on mobile, left-aligned on md+.
- Accessibility: maintain ≥ 4.5:1 contrast ratio against hero background.
- Ensure bold emphasis: wrap keywords ("fixtures", "players", "ladder positions", "instant, accurate responses") in <strong> with aria-hidden="false".

