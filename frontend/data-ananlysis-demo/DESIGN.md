# Enterprise Intelligence Workspace — Design System

## 1. Visual Theme & Atmosphere

**A restrained, clinical-analytical workspace that feels like collaborating with a senior data scientist.** The interface communicates trust, precision, and intelligence — not flashy AI. Think Palantir Foundry meets Linear meets Notion: clean, high-information-density, with purposeful use of color to encode meaning rather than decoration.

The AI analyst is a trusted colleague, not a chatbot. Every design decision reinforces this: evidence is visible, reasoning is traceable, uncertainty is acknowledged.

**Mood**: Confident restraint. Premium without being flashy. Dense without being cluttered. The interface should feel like a well-organized research lab.

---

## 2. Color Palette

### Semantic Color System (Purpose-Driven, Not Decorative)

| Token | Hex | Role |
|-------|-----|------|
| `canvas` | `#FAFAFA` | Application background |
| `surface` | `#FFFFFF` | Cards, panels, elevated surfaces |
| `surface-subtle` | `#F4F5F7` | Secondary surfaces, hover states |
| `ink-primary` | `#111827` | Primary text, headlines |
| `ink-secondary` | `#6B7280` | Descriptions, metadata |
| `ink-tertiary` | `#9CA3AF` | Timestamps, labels |
| `border-default` | `#E5E7EB` | Dividers, panel borders |
| `border-strong` | `#D1D5DB` | Active borders |

### Status Colors (Semantic, Consistent Meaning)

| Token | Hex | Meaning |
|-------|-----|---------|
| `accent-teal` | `#0D9488` | Primary actions, success, active states |
| `accent-teal-soft` | `#CCFBF1` | Success backgrounds |
| `accent-teal-muted` | `#F0FDFA` | Subtle success tint |
| `status-fact` | `#0D9488` | Verified facts (teal) |
| `status-inference` | `#2563EB` | Inferences (blue) |
| `status-qualified` | `#D97706` | Qualified/partial claims (amber) |
| `status-rejected` | `#DC2626` | Rejected, errors (red) |
| `status-warning` | `#F59E0B` | Warnings, needs attention |
| `status-info` | `#3B82F6` | Informational |

### The ONE Accent Rule

**Teal (`#0D9488`) is the only accent color.** It appears on:
- Primary CTAs
- Active navigation
- Success states
- Key data highlights

No purple, no gradients, no neon. The status colors above are semantic signals, not decorative accents.

---

## 3. Typography

### Font Stack

**Primary**: Inter (acceptable for B2B/enterprise context per Taste Skill rules)
**Mono**: JetBrains Mono (for code, metrics, timestamps)

### Scale

| Level | Size | Weight | Line-height | Use |
|-------|------|--------|-------------|-----|
| `display` | 28px | 600 | 1.2 | Page titles |
| `heading` | 20px | 600 | 1.3 | Section headers |
| `subheading` | 16px | 500 | 1.4 | Card titles |
| `body` | 14px | 400 | 1.6 | Primary content |
| `caption` | 13px | 400 | 1.5 | Secondary descriptions |
| `label` | 11px | 500 | 1.4 | Labels, badges, uppercase |

### Typography Rules

- Headlines: Sentence case, no all-caps unless for status badges
- Body: 14px minimum, 1.6 line-height for readability
- Numbers in tables/charts: Use `font-variant-numeric: tabular-nums`
- Labels: 11px uppercase with `letter-spacing: 0.05em`

---

## 4. Spatial System

### Spacing Scale (4px Base)

| Token | Value | Use |
|-------|-------|-----|
| `space-1` | 4px | Tight gaps, icon padding |
| `space-2` | 8px | Inline spacing |
| `space-3` | 12px | List item gaps |
| `space-4` | 16px | Card padding, section gaps |
| `space-6` | 24px | Major section spacing |
| `space-8` | 32px | Page margins |
| `space-12` | 48px | Hero-level spacing |

### Component Spacing

- **Cards**: 16px internal padding
- **Panels**: 20px internal padding
- **Section gaps**: 24px between sections
- **Page margins**: 32px horizontal, 24px vertical

---

## 5. Component Styling

### Buttons

**Primary Button**
- Background: `#0D9488` (teal)
- Text: `#FFFFFF`
- Hover: `#0F766E` (darker teal)
- Active: `scale(0.98)` + `#115E59`
- Padding: `px-4 py-2` (14px horizontal, 8px vertical)
- Radius: `rounded-lg` (8px)
- Font: 14px medium

**Ghost Button**
- Background: transparent
- Border: 1px `#E5E7EB`
- Text: `#374151`
- Hover: Background `#F9FAFB`
- Active: Background `#F3F4F6`

**Text Button**
- No border, no background
- Text: `#0D9488`
- Hover: underline

### Cards

Cards are used **only when elevation communicates hierarchy**. Otherwise, use:
- Border-top dividers
- Negative space
- Background color shifts

**Card Style** (when used):
- Background: `#FFFFFF`
- Border: 1px `#E5E7EB`
- Border-radius: `rounded-lg` (8px)
- Shadow: none by default
- Padding: 16px

### Inputs

- Height: 40px
- Border: 1px `#E5E7EB`
- Border-radius: `rounded-lg` (8px)
- Focus: 2px ring `#0D9488` at 20% opacity
- Placeholder: `#9CA3AF`
- Label: Above input, 13px, `#374151`

### Badges / Status Pills

| Type | Background | Text | Border |
|------|-----------|------|--------|
| FACT | `#CCFBF1` | `#0F766E` | none |
| INFERENCE | `#DBEAFE` | `#1D4ED8` | none |
| QUALIFIED | `#FEF3C7` | `#B45309` | none |
| REJECTED | `#FEE2E2` | `#DC2626` | none |
| RUNNING | `#CCFBF1` | `#0F766E` | none (with pulse dot) |

---

## 6. Layout Architecture

### Information Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Top Bar: Logo · Breadcrumb · Dataset Status · User         │
├─────────┬───────────────────────────────────────────────────┤
│         │                                                    │
│  Nav    │   Main Content Area                               │
│  Rail   │                                                    │
│         │   - Full width for analysis workspace             │
│  Today  │   - Centered max-w-4xl for data pages            │
│  Analyses│                                                   │
│  Data   │                                                    │
│  Semantics│                                                  │
│  Eval   │                                                    │
│  Settings│                                                   │
│         │                                                    │
└─────────┴───────────────────────────────────────────────────┘
```

### Navigation Rail

- Width: 56px collapsed, 200px expanded
- Icons: Phosphor icons, 20px size
- Active state: Background `#F0FDFA`, icon `#0D9488`
- Hover state: Background `#F9FAFB`

### Responsive Strategy

- **Desktop (1024px+)**: Full layout with expanded nav
- **Tablet (768-1023px)**: Collapsed nav rail, 2-column grids become 1
- **Mobile (< 768px)**: Bottom tab navigation, single column

---

## 7. Motion Philosophy

### Motion Principles

**Restrained and purposeful.** Motion communicates state changes and guides attention — it does not decorate.

- **Micro-interactions**: 150-200ms transitions on hover/active states
- **Page transitions**: 200ms fade between routes
- **Data loading**: Skeleton shimmer, not spinners
- **AI activity**: Subtle pulse on running states (not flashy)

### Animation Specs

| Interaction | Duration | Easing | Property |
|------------|----------|--------|---------|
| Hover | 150ms | ease-out | background-color, transform |
| Active | 100ms | ease-in | scale(0.98) |
| Focus ring | 150ms | ease-out | box-shadow |
| Page enter | 200ms | ease-out | opacity |
| Skeleton shimmer | 1.5s | linear | background-position |

### Reduced Motion

All animations must respect `prefers-reduced-motion`. When enabled:
- All transitions: instant
- Skeleton shimmer: static placeholder
- Pulse animations: disabled

---

## 8. Evidence-Centric Design

The workspace must make evidence **visible and traceable**.

### Evidence Inspector Pattern

Every claim/finding must have:
1. Clear type badge (FACT/INFERENCE/QUALIFIED)
2. Confidence indicator (when applicable)
3. Evidence count badge
4. Click to expand evidence detail

### Evidence Detail Structure

```
┌────────────────────────────────────────┐
│ CLAIM                                   │
│ "Vendor X contributed 31% of decline" │
│                                        │
│ Type: INFERENCE · Confidence: 87%      │
├────────────────────────────────────────┤
│ EVIDENCE                               │
│                                        │
│ Observation #128                       │
│ Query: SQL-53                          │
│ Dataset: iowa_liquor_v1                │
│                                        │
│ ✓ Metric validated                     │
│ ✓ Time range confirmed                 │
│ ✓ Join verified                        │
│ ✓ Reconciliation passed                 │
└────────────────────────────────────────┘
```

---

## 9. AI Collaboration UX

### The AI Analyst Persona

The interface should feel like working with a **research analyst**:
- Questions are precise, not casual
- Progress is visible and explainable
- Uncertainty is acknowledged honestly
- Evidence is always attached to claims

### Analysis States

| State | Visual Treatment |
|-------|-----------------|
| **Running** | Teal pulse dot, progress bar, step indicator |
| **Clarifying** | Amber highlight, inline question form |
| **Completed** | Checkmarks on steps, findings expandable |
| **Partial** | Amber warning, available findings shown |
| **Failed** | Red indicator, clear error message, retry option |

### No "AI Thinking" Animations

No floating orbs, no animated brain icons, no "AI is thinking" panels. The analysis runs silently; progress is shown through concrete steps:
- "Analyzing..."
- "Testing hypothesis 2/4..."
- "Computing contributions..."

---

## 10. Anti-Patterns (Banned)

### Visual Anti-Patterns

- [ ] **No purple/blue gradient backgrounds**
- [ ] **No glowing AI orb or brain icons**
- [ ] **No glassmorphism effects**
- [ ] **No decorative gradients on cards**
- [ ] **No emoji anywhere in UI**
- [ ] **No Inter as display font** (acceptable as body)
- [ ] **No rounded pill buttons** (use rounded-lg)
- [ ] **No shadow-lg on cards**

### Layout Anti-Patterns

- [ ] **No 3-column equal card grids**
- [ ] **No centered hero layouts**
- [ ] **No excessive whitespace (> 48px gaps)**
- [ ] **No dashboard cards with rounded-xl border**

### Content Anti-Patterns

- [ ] **No "AI is thinking..." messages**
- [ ] **No generic loading spinners**
- [ ] **No "Elevate your data" type copy**
- [ ] **No placeholder "lorem ipsum"**
- [ ] **No fake round numbers (99.9%, 50%)**

### Interaction Anti-Patterns

- [ ] **No `h-screen` for full-height sections** (use `min-h-[100dvh]`)
- [ ] **No `window.addEventListener('scroll')`**
- [ ] **No instant state changes without transitions**

---

## 11. Design Tokens Reference

```css
/* Colors */
--color-canvas: #FAFAFA;
--color-surface: #FFFFFF;
--color-surface-subtle: #F4F5F7;
--color-ink-primary: #111827;
--color-ink-secondary: #6B7280;
--color-ink-tertiary: #9CA3AF;
--color-border-default: #E5E7EB;
--color-border-strong: #D1D5DB;
--color-accent: #0D9488;
--color-accent-hover: #0F766E;
--color-accent-active: #115E59;
--color-accent-soft: #CCFBF1;
--color-status-fact: #0D9488;
--color-status-inference: #2563EB;
--color-status-qualified: #D97706;
--color-status-rejected: #DC2626;

/* Typography */
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
--text-display: 28px/1.2 font-weight-600;
--text-heading: 20px/1.3 font-weight-600;
--text-subheading: 16px/1.4 font-weight-500;
--text-body: 14px/1.6 font-weight-400;
--text-caption: 13px/1.5 font-weight-400;
--text-label: 11px/1.4 font-weight-500 letter-spacing-0.05em uppercase;

/* Spacing */
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
--space-12: 48px;

/* Radius */
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;

/* Transitions */
--transition-fast: 150ms ease-out;
--transition-base: 200ms ease-out;
--transition-slow: 300ms ease-out;
```

---

## 12. Implementation Notes

### Priority Order

1. **AppShell** — Navigation, layout structure
2. **Today Page** — First impression, must be polished
3. **Workspace** — Core experience, evidence visibility
4. **Supporting Pages** — Consistent styling applied

### Key Differences from Current Design

1. Navigation: Left rail → top nav with breadcrumbs
2. Cards: No shadows, use borders
3. Status: Color-coded with semantic meaning
4. Evidence: Always visible, never hidden
5. Motion: Subtle, purposeful, never decorative

### Skills Used

- `design-taste-frontend` — Anti-slop guidelines, three-dial system
- `high-end-visual-design` — Premium component patterns
- `redesign-existing-projects` — Audit and upgrade protocol
- `stitch-design-taste` — Design system documentation format

---

*Last updated: 2026-09-03*
*Version: 1.0.0*
