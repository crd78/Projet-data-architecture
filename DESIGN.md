---
name: Urban Data Explorer
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#46464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#77767e'
  outline-variant: '#c7c5ce'
  surface-tint: '#585d77'
  primary: '#03071d'
  on-primary: '#ffffff'
  primary-container: '#1a1f36'
  on-primary-container: '#8286a2'
  inverse-primary: '#c1c5e3'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#00081f'
  on-tertiary: '#ffffff'
  tertiary-container: '#001f4b'
  on-tertiary-container: '#3f85f9'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#c1c5e3'
  on-primary-fixed: '#151a31'
  on-primary-fixed-variant: '#41455f'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a42'
  on-tertiary-fixed-variant: '#004395'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.5'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.05em
  data-mono:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  margin-page: 24px
  panel-width: 380px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is engineered for high-density urban intelligence and sophisticated spatial analysis. It targets urban planners, logistics analysts, and civic researchers who require a balance of deep data immersion and aesthetic clarity. 

The style marries **Corporate Modernism** with **Glassmorphism**. The foundational layout uses a heavy, authoritative midnight blue to anchor the navigation, while information overlays utilize translucent glass effects to maintain a sense of place within the map context. The emotional response is one of precision, "prestige tech," and calm authority over complex datasets.

## Colors

The palette is driven by the contrast between deep architectural shadows and vibrant data signals. 
- **Midnight Blue (#1a1f36):** Used for primary headers, sidebar backgrounds, and high-level navigation to provide a solid frame.
- **Emerald Green (#10b981) & Electric Blue (#3b82f6):** These act as functional "data-ink." Use Emerald for positive growth, sustainability metrics, or active status. Use Electric Blue for connectivity, movement, and interactive highlights.
- **Crisp White:** Reserved for physical cards and information modules to ensure maximum legibility against the map.
- **Translucency:** Glass layers should use a 70-80% opacity white with a saturation boost to keep the map colors from appearing muddy.

## Typography

The design system utilizes **Inter** for all functional and editorial text to maintain a systematic, utilitarian aesthetic. 

- **Weight Strategy:** Use Semibold (600) for headers to provide clear hierarchy against the map. 
- **Data Display:** For coordinates, timestamps, and specific numerical values, a secondary monospaced font (Space Grotesk) is introduced to evoke a technical, futuristic feel. 
- **Hierarchy:** Maintain tight line-heights for data labels to allow for high-density information layouts without visual clutter.

## Layout & Spacing

The layout operates on a **Hybrid Fluid Grid**. The map canvas is fully fluid, expanding to the edges of the viewport. Overlays and data panels are governed by a strict 4px baseline grid.

- **Side Panels:** Fixed at 380px to accommodate complex data visualizations while preserving map visibility.
- **Floating Controls:** Elements like zoom levels and layer toggles are grouped into modular clusters with 8px internal spacing.
- **Safe Zones:** A 24px margin is maintained from the viewport edges for all floating glass panels to prevent a "cramped" feel.

## Elevation & Depth

Visual hierarchy in the design system is achieved through a combination of backdrop blurring and layered shadows.

1.  **Level 0 (Base):** The map layer.
2.  **Level 1 (Surface):** Glassmorphism panels. These use a `backdrop-filter: blur(12px)`, a `1px` solid white border at 20% opacity, and no shadow. They appear "docked" or secondary.
3.  **Level 2 (Active Cards):** Solid white cards. These feature a soft, diffused ambient shadow (`0 10px 25px -5px rgba(26, 31, 54, 0.1)`) and a subtle grey border.
4.  **Level 3 (Popovers/Modals):** High-contrast elements with a deeper shadow to indicate immediate focus.

All edges of elevated elements should feel crisp, using the 1px border technique to ensure they pop against both light and dark map areas.

## Shapes

The design system adopts a **Rounded** shape language to soften the density of the data and provide a modern, approachable feel.

- **Standard Radius:** 0.5rem (8px) for all primary cards, buttons, and input fields.
- **Large Components:** Side panels and large modal containers use 1.5rem (24px) for the corners facing the map to emphasize their "floating" nature.
- **Pill Elements:** Status badges and map markers use a full pill-shape (999px) to distinguish them from structural UI components.

## Components

### Buttons & Controls
- **Primary Action:** Solid Midnight Blue with white text.
- **Data Toggle:** Ghost style with an 8px radius and Electric Blue active state indicators.
- **Refined Form Controls:** Input fields use a 1px border in a light grey-blue, shifting to Electric Blue on focus with a soft outer glow.

### KPI Cards
Elegant modules featuring a large `headline-lg` value in Midnight Blue, a `label-caps` descriptor, and a small sparkline chart utilizing the Emerald Green accent for trend visualization.

### Map Markers
Markers are designed as "Pins" with a 2px white halo to ensure visibility against varied terrain. Use Emerald Green for "Points of Interest" and Electric Blue for "Infrastructure Nodes."

### Glass Overlays
Used for legend controls and layer switchers. They must include a subtle inner "sheen" (a top-to-bottom white gradient at very low opacity) to enhance the glass effect.

### Lists
Data lists within panels should use "zebra-striping" with a 2% opacity version of the primary color or a 1px bottom border to separate dense rows of urban statistics.