---
version: alpha
name: Acme Console
description: Calm, dense, keyboard-first admin UI. Neutral surfaces, one confident accent.
colors:
  primary: "#3B5BDB"
  onPrimary: "#FFFFFF"
  primaryHover: "#364FC7"
  surface: "#FFFFFF"
  surfaceRaised: "#F8F9FA"
  onSurface: "#1A1C1E"
  onSurfaceMuted: "#5F6368"
  border: "#DADCE0"
  danger: "#D93025"
  onDanger: "#FFFFFF"
  success: "#188038"
typography:
  display:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.25
  heading:
    fontFamily: "{typography.display.fontFamily}"
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.35
  body:
    fontFamily: "{typography.display.fontFamily}"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 4px
  md: 8px
  lg: 12px
spacing:
  1: 4px
  2: 8px
  3: 12px
  4: 16px
  6: 24px
  8: 32px
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.onPrimary}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "{spacing.3}"
  buttonHover:
    backgroundColor: "{colors.primaryHover}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.onSurface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.6}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.onSurface}"
    rounded: "{rounded.md}"
    padding: "{spacing.2}"
    height: 36px
---

## Overview

Acme Console is a tool people live in for hours. The visual language is
deliberately quiet: near-white surfaces, high text contrast, a single indigo
accent reserved for primary actions and active state. Nothing decorative
competes with data. Density is a feature — default to compact spacing and let
whitespace come from structure, not padding.

## Colors

Color is semantic. `surface` is the default background; `surfaceRaised` marks
panels and sticky headers that sit above it. `onSurface` is body text;
`onSurfaceMuted` is for secondary labels, timestamps, and disabled text —
never for content the user must read carefully. `primary` is the only accent:
one primary button per view, plus active nav and focus rings. `danger` and
`success` appear only on status and destructive confirmation — never as
decoration. Borders are `border`, 1px, used instead of shadow wherever a line
will do.

## Typography

One family (Inter) for everything except code, which uses `mono`. The scale is
tight: `display` for page titles only, `heading` for section and card titles,
`body` for everything else. Weight carries hierarchy more than size — prefer
600 on 14px over jumping to 18px. Line length caps around 72ch in prose areas.

## Layout

8px base grid; `spacing` steps are the only allowed gaps. Content sits in a
max 1200px column with a fixed 240px left nav. Forms are single-column.
Tables go full-bleed to their container. Below 768px the nav collapses to a
drawer and padding drops one step.

## Elevation & Depth

Depth is mostly borders and background shifts, not shadow. Three levels:
base (`surface`), raised (`surfaceRaised` + 1px border) for panels and
dropdowns, and overlay (`surface` + a soft shadow) for modals and the nav
drawer only. Never stack more than two raised levels.

## Shapes

`rounded.sm` for tags and inline chips, `rounded.md` for buttons, inputs, and
menus, `rounded.lg` for cards and modals. No fully-round elements except
avatars and the loading spinner. Corners stay consistent within a component
group.

## Components

**Button** — one `primary` per view; everything else is a text or bordered
button (same padding, transparent background, `onSurface` text). Disabled =
`onSurfaceMuted` text, no background change. **Card** — `lg` radius, `border`,
no shadow; the header uses `heading`. **Input** — 36px tall, `border` default,
`primary` border on focus with a 2px focus ring. Error state swaps the border
to `danger` and shows help text in `danger` below.

## Do's and Don'ts

- Do use `onSurfaceMuted` for metadata; don't use it for anything actionable.
- Do reserve `primary` for the single most important action on screen.
- Don't introduce a new accent color for a feature — use weight, border, or
  an icon instead.
- Don't add shadows to make something "pop"; raise the surface or add a border.
- When a spacing value isn't on the scale, round to the nearest step, don't
  invent one.
- When unsure which type style to use, pick the smaller one and add weight.
