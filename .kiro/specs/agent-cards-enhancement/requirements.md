# Agent Cards Enhancement - Requirements

## Overview
Enhance the ANZx.ai marketing site with interactive, animated agent cards that provide a more engaging user experience similar to live chat interfaces.

## Requirements

### 1. Remove ANZX.ai Logo
**User Story:** As a visitor, I want a clean hero section without the large ANZX.ai text logo so the focus is on the AI agents.

#### Acceptance Criteria
1. WHEN viewing the hero section THEN the large "ANZX.ai" text logo SHALL be removed
2. WHEN the logo is removed THEN the layout SHALL remain balanced and professional
3. WHEN viewing on mobile THEN the hero section SHALL still be properly formatted

### 2. Improve Button Visibility
**User Story:** As a visitor, I want clearly visible CTA buttons that stand out against the background.

#### Acceptance Criteria
1. WHEN viewing "Get Your Agents" button THEN it SHALL have high contrast colors
2. WHEN viewing "Watch Demo" button THEN it SHALL be clearly distinguishable from primary button
3. WHEN hovering over buttons THEN they SHALL provide clear visual feedback
4. WHEN buttons are displayed THEN they SHALL follow professional design standards

### 3. Add Animated Agent Avatars
**User Story:** As a visitor, I want to see realistic animated agent avatars that make the agents feel alive and interactive.

#### Acceptance Criteria
1. WHEN viewing agent cards THEN each agent SHALL have a unique animated avatar
2. WHEN an agent is "typing" THEN realistic typing responses SHALL be displayed
3. WHEN viewing Emma's card THEN her avatar SHALL be animated
4. WHEN viewing Olivia's card THEN her avatar SHALL be animated
5. WHEN viewing Jack's card THEN his avatar SHALL be animated
6. WHEN viewing Liam's card THEN his avatar SHALL be animated
7. WHEN typing animation plays THEN it SHALL cycle through realistic AI responses
8. WHEN responses are shown THEN they SHALL be relevant to each agent's role

### 4. Implement Agent Card Interactions
**User Story:** As a visitor, I want to click "Get Your Agents" and be taken to the agent cards section, and I want agent templates to work properly.

#### Acceptance Criteria
1. WHEN clicking "Get Your Agents" button THEN the page SHALL smooth scroll to agent cards
2. WHEN clicking on an agent card THEN the agent template page SHALL open
3. WHEN agent template loads THEN it SHALL display correctly without errors
4. WHEN navigating to agent templates THEN all agent data SHALL be properly loaded
5. WHEN returning from agent template THEN the user SHALL be able to navigate back smoothly

## Technical Constraints
- Must use Next.js 14 with App Router
- Must maintain current teal/navy color scheme
- Must be mobile responsive
- Must maintain accessibility standards (WCAG AA)
- Avatar animations should use CSS/SVG (no heavy libraries)
- Smooth scroll should use native browser APIs

## Success Criteria
- All 4 requirements implemented and working
- No TypeScript errors
- Passes accessibility audit
- Smooth 60fps animations
- Fast page load times (<3s)
