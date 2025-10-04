# Agent Avatar Design Guide

## Overview

This document describes the design specifications for the ANZX AI agent avatars. Each avatar represents a distinct AI agent persona with unique characteristics and visual identity.

## Design Philosophy

- **Professional yet Approachable**: Avatars should convey expertise while remaining friendly and accessible
- **Distinctive**: Each avatar should be immediately recognizable and distinct from others
- **Scalable**: Designs work at multiple sizes (from 32px to 400px)
- **Modern**: Clean, contemporary design aesthetic
- **Inclusive**: Diverse representation across gender and ethnicity

## Agent Avatars

### Emma - AI Recruiting Agent

**File**: `public/avatars/emma.svg`

**Color Palette**:
- Primary: Purple (#8B5CF6 to #6366F1 gradient)
- Skin: Warm beige (#FED7AA)
- Hair: Brown (#8B4513)
- Accent: Green badge (#10B981)

**Characteristics**:
- Professional appearance
- Confident posture
- Green checkmark badge (symbolizing approval/qualification)
- Purple gradient background (represents wisdom and professionalism)

**Personality Traits**:
- Detail-oriented
- Professional
- Empathetic
- Organized

**Use Cases**:
- Recruiting pages
- Candidate screening interfaces
- Interview scheduling
- Resume analysis features

---

### Olivia - Customer Service AI

**File**: `public/avatars/olivia.svg`

**Color Palette**:
- Primary: Pink (#EC4899 to #F472B6 gradient)
- Skin: Light pink (#FECACA)
- Hair: Red (#DC2626)
- Accent: Headset (black #1F2937)

**Characteristics**:
- Warm, friendly smile
- Customer service headset
- Pink gradient background (represents warmth and care)
- Approachable demeanor

**Personality Traits**:
- Empathetic
- Patient
- Solution-oriented
- Friendly

**Use Cases**:
- Customer service pages
- Support chat interfaces
- Help center
- FAQ sections

---

### Jack - AI Sales Agent

**File**: `public/avatars/jack.svg`

**Color Palette**:
- Primary: Blue (#3B82F6 to #2563EB gradient)
- Skin: Warm beige (#FED7AA)
- Hair: Dark (#1F2937)
- Accent: Red tie (#DC2626), Gold badge (#F59E0B)

**Characteristics**:
- Confident expression
- Professional attire (tie)
- Dollar sign badge (symbolizing sales success)
- Blue gradient background (represents trust and professionalism)

**Personality Traits**:
- Confident
- Persuasive
- Results-driven
- Relationship-focused

**Use Cases**:
- Sales pages
- Demo request forms
- Lead qualification
- Pricing pages

---

### Liam - Support Agent

**File**: `public/avatars/liam.svg`

**Color Palette**:
- Primary: Green (#10B981 to #059669 gradient)
- Skin: Warm beige (#FED7AA)
- Hair: Light brown (#B45309)
- Accent: Glasses (black #1F2937), Purple tech badge (#6366F1)

**Characteristics**:
- Glasses (symbolizing technical expertise)
- Friendly, approachable smile
- Gear icon badge (symbolizing technical support)
- Green gradient background (represents growth and support)

**Personality Traits**:
- Patient
- Methodical
- Technical but approachable
- Problem-solver

**Use Cases**:
- Technical support pages
- Documentation
- Troubleshooting guides
- API documentation

## Technical Specifications

### File Formats

**SVG (Primary)**:
- Vector format for perfect scaling
- Small file size
- Editable and customizable
- Located in: `public/avatars/`

**WebP (Optimized)**:
- Raster format for better performance
- Multiple sizes: 32px, 64px, 128px, 256px, 512px
- To be generated from SVG
- Located in: `public/avatars/webp/`

**AVIF (Next-gen)**:
- Modern format for best compression
- Same sizes as WebP
- To be generated from SVG
- Located in: `public/avatars/avif/`

### Sizes

| Size | Use Case |
|------|----------|
| 32px | Navigation, small icons |
| 64px | Chat bubbles, inline mentions |
| 128px | Cards, thumbnails |
| 256px | Profile headers, feature sections |
| 512px | Hero sections, large displays |

### Optimization

**SVG Optimization**:
```bash
# Using SVGO
npx svgo public/avatars/*.svg
```

**Generate WebP**:
```bash
# Using sharp-cli
npx sharp-cli -i public/avatars/emma.svg -o public/avatars/webp/emma-256.webp --width 256
```

**Generate AVIF**:
```bash
# Using sharp-cli
npx sharp-cli -i public/avatars/emma.svg -o public/avatars/avif/emma-256.avif --width 256
```

## Usage in Components

### React Component

```typescript
import Image from 'next/image';

interface AgentAvatarProps {
  agent: 'emma' | 'olivia' | 'jack' | 'liam';
  size?: number;
  className?: string;
}

export function AgentAvatar({ agent, size = 128, className }: AgentAvatarProps) {
  return (
    <Image
      src={`/avatars/${agent}.svg`}
      alt={`${agent} avatar`}
      width={size}
      height={size}
      className={className}
    />
  );
}
```

### With Fallback

```typescript
<picture>
  <source srcSet="/avatars/avif/emma-256.avif" type="image/avif" />
  <source srcSet="/avatars/webp/emma-256.webp" type="image/webp" />
  <img src="/avatars/emma.svg" alt="Emma avatar" width="256" height="256" />
</picture>
```

## Accessibility

### Alt Text Guidelines

- **Emma**: "Emma, AI recruiting agent avatar"
- **Olivia**: "Olivia, customer service AI avatar"
- **Jack**: "Jack, AI sales agent avatar"
- **Liam**: "Liam, technical support agent avatar"

### ARIA Labels

```html
<img 
  src="/avatars/emma.svg" 
  alt="Emma, AI recruiting agent avatar"
  role="img"
  aria-label="Emma, your AI recruiting assistant"
/>
```

## Animation Guidelines

### Hover Effects

```css
.agent-avatar {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.agent-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}
```

### Pulse Animation (for active state)

```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.agent-avatar.active {
  animation: pulse 2s ease-in-out infinite;
}
```

## Brand Guidelines

### Do's ✅

- Use avatars at appropriate sizes
- Maintain aspect ratio (1:1)
- Use on contrasting backgrounds
- Include alt text for accessibility
- Use SVG for scalability

### Don'ts ❌

- Don't distort or stretch avatars
- Don't change the color schemes
- Don't add filters or effects that obscure the design
- Don't use on busy backgrounds
- Don't use below 32px size

## Future Enhancements

### Planned Additions

1. **Animated Versions**:
   - Lottie animations for loading states
   - Subtle breathing animations
   - Talking animations for chat

2. **Expressions**:
   - Happy, thinking, confused states
   - Different poses
   - Seasonal variations

3. **3D Versions**:
   - 3D models for immersive experiences
   - VR/AR ready versions

4. **Customization**:
   - User-selectable color themes
   - Accessory options
   - Background variations

## Version History

- **v1.0.0** (2025-03-10): Initial avatar designs created
  - Emma (Recruiting Agent)
  - Olivia (Customer Service AI)
  - Jack (Sales Agent)
  - Liam (Support Agent)

## Credits

- **Design**: ANZX Design Team
- **Format**: SVG (Scalable Vector Graphics)
- **License**: Proprietary - ANZX.ai

---

**Last Updated**: 2025-03-10
**Version**: 1.0.0
