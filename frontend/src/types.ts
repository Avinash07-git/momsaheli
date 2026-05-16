// Type mirrors of the backend Pydantic schemas (app/schemas/).
// Keep in sync when backend changes.

export type Verdict = 'PASS' | 'BLOCK' | 'WARN';
export type AgentName = 'profile' | 'market_scout' | 'reality_compliance' | 'launch' | 'memory' | 'system';
export type EventType =
  | 'run_started'
  | 'profile_ready'
  | 'evidence_card'
  | 'opportunities_ranked'
  | 'compliance_check'
  | 'winner_selected'
  | 'launch_packet_ready'
  | 'launch_published'
  | 'memory_pattern'
  | 'agent_error'
  | 'run_complete';

export interface Profile {
  persona_id: string;
  display_name: string;
  day_job: string;
  income_gap_monthly_usd: number;
  hours_per_week_available: number;
  skills: string[];
  budget_startup_usd: number;
  state: string;
  city?: string | null;
  hard_constraints: string[];
  notes?: string | null;
}

export interface EvidenceCard {
  id: string;
  title: string;
  source:
    | 'etsy'
    | 'poshmark'
    | 'craigslist'
    | 'nextdoor'
    | 'outschool'
    | 'facebook_marketplace'
    | 'facebook_group'
    | 'castiron'
    | 'instagram';
  source_url: string;
  observed_price_usd: number;
  observed_volume_signal: string;
  estimated_gross_monthly_usd: number;
  estimated_net_monthly_usd: number;
  time_to_first_dollar_days: number;
  notes: string;
  actionbook_session_id?: string | null;
  actionbook_session_url?: string | null;
  actionbook_screenshot_url?: string | null;
}

export interface Opportunity {
  id: string;
  title: string;
  category: 'food_local' | 'digital_async' | 'service_local' | 'resale' | 'tutoring';
  evidence_card_ids: string[];
  rank: number;
  rationale: string;
  estimated_net_monthly_usd: number;
  requires_permit: boolean;
}

export interface ComplianceCheck {
  opportunity_id: string;
  verdict: Verdict;
  constraint_math_passed: boolean;
  constraint_math_reasons: string[];
  legal_passed: boolean;
  legal_citation_source_url?: string | null;
  legal_citation_text?: string | null;
  block_reason?: string | null;
}

export interface OutreachDraft {
  channel: 'nextdoor' | 'facebook_group' | 'text_friends' | 'etsy_listing' | 'instagram';
  subject?: string | null;
  body_markdown: string;
}

export interface DayPlanItem {
  day: number;
  action: string;
  estimated_minutes: number;
}

export interface LaunchPacket {
  opportunity_id: string;
  offer_name: string;
  offer_tagline: string;
  price_usd: number;
  unit: string;
  description_markdown: string;
  target_customer: string;
  outreach_drafts: OutreachDraft[];
  day_plan: DayPlanItem[];
}

export interface CrossUserPattern {
  pattern_text: string;
  supporting_run_ids: string[];
  confidence: number;
}

export interface RunSummary {
  run_id: string;
  persona_display_name: string;
  winner_offer_name?: string | null;
  launch_url?: string | null;
  created_at: string;
  duration_ms: number;
}

export interface AgentEvent {
  type: EventType;
  agent: AgentName;
  run_id: string;
  timestamp: string;
  data: Record<string, any>;
}
