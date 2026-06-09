---
name: Cyber Safety Collective
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#c4c9ac'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#8e9379'
  outline-variant: '#444933'
  surface-tint: '#abd600'
  primary: '#ffffff'
  on-primary: '#283500'
  primary-container: '#c3f400'
  on-primary-container: '#556d00'
  inverse-primary: '#506600'
  secondary: '#ffb59a'
  on-secondary: '#5a1b00'
  secondary-container: '#ff5e07'
  on-secondary-container: '#531900'
  tertiary: '#ffffff'
  on-tertiary: '#00363a'
  tertiary-container: '#7df4ff'
  on-tertiary-container: '#006f77'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#c3f400'
  primary-fixed-dim: '#abd600'
  on-primary-fixed: '#161e00'
  on-primary-fixed-variant: '#3c4d00'
  secondary-fixed: '#ffdbce'
  secondary-fixed-dim: '#ffb59a'
  on-secondary-fixed: '#370e00'
  on-secondary-fixed-variant: '#802a00'
  tertiary-fixed: '#7df4ff'
  tertiary-fixed-dim: '#00dbe9'
  on-tertiary-fixed: '#002022'
  on-tertiary-fixed-variant: '#004f54'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-xl:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: '900'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Public Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  title-md:
    fontFamily: Public Sans
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.1em
  data-mono:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-margin: 24px
  gutter: 16px
  stack-sm: 4px
  stack-md: 12px
  stack-lg: 24px
---

## Brand & Style

The design system bridges the gap between rigid industrial compliance and the high-energy, digital-first aesthetic of the MZ generation. It transforms dry legal data and safety protocols into a high-performance "gaming-dashboard" experience. The personality is aggressive yet precise—projecting an image of a tech-enabled workforce that values both safety and style.

The visual style is **Cyber-Industrial Glassmorphism**. It utilizes deep, ink-like backgrounds to provide maximum contrast for high-visibility "Safety Neon" accents. By layering frosted glass surfaces over subtle background glows, the UI achieves a sense of technological depth and sophistication, making the "Industrial Jurisprudence" framework feel like a cutting-edge OS rather than a document repository.

## Colors

This design system is built on a "Dark-First" philosophy to reduce eye strain in high-glare environments and to lean into the cyberpunk aesthetic.

- **Primary (Electric Lime):** Used for critical action buttons, safety status indicators, and primary branding. It mimics high-visibility safety vests.
- **Secondary (Cyber Orange):** Dedicated to warnings, alerts, and time-sensitive legal deadlines.
- **Tertiary (Neon Cyan):** Used for data visualization, interactive elements, and tech-oriented decorative accents.
- **Neutral (Deep Charcoal):** The foundation. We use a range of blacks (from `#080808` to `#1A1A1A`) to create depth without losing the "void" feel of the background.

## Typography

Typography focuses on high-impact hierarchy. **Public Sans** is pushed to its limits with heavy weights and tight tracking for a "brutal" and authoritative look. **Inter** provides high readability for dense legal text. **Space Grotesk** is used for "HUD" (Heads-Up Display) elements, labels, and technical data points to reinforce the gaming-dashboard feel.

All headlines should favor lowercase or heavy uppercase to maintain the trend-forward aesthetic. Tracking is tightened on displays to create a solid block of text that feels industrial and sturdy.

## Layout & Spacing

The layout follows a **Fluid Grid** model inspired by modular dashboards. 
- **Desktop:** 12-column grid with generous 24px gutters. Elements are housed in "modules" that can span 3, 4, 6, or 12 columns.
- **Mobile:** 4-column grid with 16px gutters.
- **Spacing Rhythm:** Based on an 8px scale. Use tight spacing (stack-sm) for grouping related metadata and larger gaps (stack-lg) for separating distinct legal sections or safety categories.

Layouts should prioritize a "center-stack" for mobile and a "multi-pane" sidebar-heavy approach for desktop to mimic professional monitoring software.

## Elevation & Depth

Depth is achieved through **Glassmorphism and Glow**, not traditional drop shadows.
- **Surface 0 (Background):** Pure `#080808`.
- **Surface 1 (Cards):** Semi-transparent black (`rgba(20, 20, 20, 0.7)`) with a 1px border of `rgba(255, 255, 255, 0.1)` and a `backdrop-filter: blur(20px)`.
- **Surface 2 (Popovers/Modals):** Lighter transparency with a 1px primary-colored border at 30% opacity.
- **Active State:** Elements should have an "outer glow" using the primary color (`box-shadow: 0 0 15px rgba(204, 255, 0, 0.4)`) to simulate a powered-on screen.

## Shapes

The design system uses a **Rounded** (0.5rem) approach to balance the harshness of the dark mode and industrial theme. 
- **Small elements (Buttons/Inputs):** 8px (0.5rem).
- **Medium elements (Cards/Containers):** 16px (1rem).
- **Large elements (Modals/Hero areas):** 24px (1.5rem).

Interactive elements like chips and status badges may use a "Pill" shape to distinguish them from structural layout components.

## Components

- **Buttons:** Primary buttons use solid Electric Lime with black text. Secondary buttons are "Ghost" style with a 1px lime border and semi-transparent fill.
- **Glass Cards:** All content containers must use the frosted glass effect defined in the Elevation section.
- **Data HUDs:** Instead of simple lists, use "Stat Blocks" with large `data-mono` numbers and `label-caps` descriptions, reminiscent of a player's stats in a game.
- **Safety Indicators:** Use circular progress rings with neon gradients (Lime to Cyan) to track compliance percentages.
- **Input Fields:** Dark backgrounds with a bottom-only border that glows primary color when focused. Use `Space Grotesk` for placeholder text.
- **Legal Chips:** High-contrast tags with black background and thick 2px colored borders (Orange for urgent, Cyan for informational).
- **Scrollbars:** Custom slim, neon-colored scrollbars to maintain the tech-heavy aesthetic.