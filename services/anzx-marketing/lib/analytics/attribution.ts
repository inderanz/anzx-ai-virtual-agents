// Attribution tracking for marketing campaigns

export interface AttributionData {
  source: string;
  medium: string;
  campaign: string;
  term?: string;
  content?: string;
  referrer: string;
  landingPage: string;
  timestamp: string;
}

export interface ConversionData {
  id: string;
  type: string;
  value: number;
  timestamp: string;
  attribution: AttributionData;
}

export interface AttributionReport {
  totalConversions: number;
  conversionsBySource: Record<string, number>;
  conversionsByCampaign: Record<string, number>;
  conversionsByMedium: Record<string, number>;
  conversionsByType: Record<string, number>;
  totalValue: number;
}

export function getAttributionData(): AttributionData {
  if (typeof window === 'undefined') {
    return {
      source: 'direct',
      medium: 'none',
      campaign: 'none',
      referrer: '',
      landingPage: '',
      timestamp: new Date().toISOString(),
    };
  }

  const urlParams = new URLSearchParams(window.location.search);
  
  return {
    source: urlParams.get('utm_source') || 'direct',
    medium: urlParams.get('utm_medium') || 'none',
    campaign: urlParams.get('utm_campaign') || 'none',
    term: urlParams.get('utm_term') || undefined,
    content: urlParams.get('utm_content') || undefined,
    referrer: document.referrer || 'direct',
    landingPage: window.location.pathname,
    timestamp: new Date().toISOString(),
  };
}

export function storeAttribution() {
  if (typeof window === 'undefined') return;
  
  const attribution = getAttributionData();
  localStorage.setItem('attribution', JSON.stringify(attribution));
}

export function getStoredAttribution(): AttributionData | null {
  if (typeof window === 'undefined') return null;
  
  const stored = localStorage.getItem('attribution');
  return stored ? JSON.parse(stored) : null;
}

export function getStoredConversions(): ConversionData[] {
  if (typeof window === 'undefined') return [];
  
  const stored = localStorage.getItem('conversions');
  return stored ? JSON.parse(stored) : [];
}

export function getAttributionReport(): AttributionReport {
  const conversions = getStoredConversions();
  
  const report: AttributionReport = {
    totalConversions: conversions.length,
    conversionsBySource: {},
    conversionsByCampaign: {},
    conversionsByMedium: {},
    conversionsByType: {},
    totalValue: 0,
  };
  
  conversions.forEach(conversion => {
    const source = conversion.attribution.source;
    const campaign = conversion.attribution.campaign;
    const medium = conversion.attribution.medium;
    const type = conversion.type;
    
    report.conversionsBySource[source] = (report.conversionsBySource[source] || 0) + 1;
    report.conversionsByCampaign[campaign] = (report.conversionsByCampaign[campaign] || 0) + 1;
    report.conversionsByMedium[medium] = (report.conversionsByMedium[medium] || 0) + 1;
    report.conversionsByType[type] = (report.conversionsByType[type] || 0) + 1;
    report.totalValue += conversion.value;
  });
  
  return report;
}


export function initializeAttribution() {
  if (typeof window === 'undefined') return;
  
  // Store attribution on first visit
  if (!getStoredAttribution()) {
    storeAttribution();
  }
}

export function trackConversionWithAttribution(type: string, value: number) {
  if (typeof window === 'undefined') return;
  
  const attribution = getStoredAttribution() || getAttributionData();
  const conversion: ConversionData = {
    id: Math.random().toString(36).substr(2, 9),
    type,
    value,
    timestamp: new Date().toISOString(),
    attribution,
  };
  
  const conversions = getStoredConversions();
  conversions.push(conversion);
  localStorage.setItem('conversions', JSON.stringify(conversions));
}
