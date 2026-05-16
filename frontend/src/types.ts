// Type mirrors of the backend Pydantic schemas (app/schemas/).
// Keep in sync when backend changes.

export type Verdict = 'PASS' | 'BLOCK' | 'WARN';
export type AgentName = 'profile' | 'market_scout' | 'reality_compliance' | 'launch' | 'customer_activation' | 'memory' | 'system';
export type EventType =
  | 'run_started'
  | 'profile_ready'
  | 'evidence_card'
  | 'opportunities_ranked'
  | 'compliance_check'
  | 'winner_selected'
  | 'launch_packet_ready'
  | 'launch_published'
  | 'customer_leads_found'
  | 'activation_plan_ready'
  | 'action_execution_result'
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
  assets?: string[];
  preferred_channels?: string[];
  approved_channels?: ApprovedChannel[];
  marketing_permission_level?: 'draft_only' | 'fill_no_submit' | 'post_after_review';
  service_radius_miles?: number | null;
}

export interface ApprovedChannel {
  id: string;
  type:
    | 'whatsapp_group'
    | 'facebook_group'
    | 'nextdoor'
    | 'instagram'
    | 'friends_text'
    | 'email'
    | 'vendor_form'
    | 'marketplace'
    | 'manual';
  name: string;
  audience?: string | null;
  url?: string | null;
  rules_summary?: string | null;
  user_approved: boolean;
  allowed_actions: Array<'draft' | 'fill' | 'submit' | 'post'>;
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
  live_scrape_ok?: boolean;
  live_scrape_provider?: string | null;
}

export interface RevenueCitation {
  url: string;
  title: string;
  snippet: string;
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
  revenue_citations: RevenueCitation[];
}

export interface ComplianceDimension {
  dimension: string;
  passed: boolean;
  citation_url?: string | null;
  citation_text?: string | null;
  note: string;
}

export interface ComplianceCheck {
  opportunity_id: string;
  verdict: Verdict;
  constraint_math_passed: boolean;
  constraint_math_reasons: string[];
  legal_passed: boolean;
  legal_citation_source_url?: string | null;
  legal_citation_text?: string | null;
  legal_citation_live?: boolean;
  legal_citation_provider?: string | null;
  block_reason?: string | null;
  dimensions: ComplianceDimension[];
}

export interface OutreachDraft {
  channel:
    | 'nextdoor'
    | 'facebook_group'
    | 'text_friends'
    | 'etsy_listing'
    | 'instagram'
    | 'whatsapp_group'
    | 'vendor_form'
    | 'marketplace_listing'
    | 'email'
    | 'manual';
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

export interface CustomerLead {
  id: string;
  title: string;
  source_type:
    | 'vendor_form'
    | 'community_page'
    | 'school_page'
    | 'marketplace'
    | 'approved_group'
    | 'warm_network'
    | 'public_demand_post'
    | 'local_directory'
    | 'event_page'
    | 'manual';
  source_url?: string | null;
  audience_match: string;
  why_relevant: string;
  estimated_reach?: string | null;
  confidence: number;
  live_source: boolean;
  provider: string;
  notes?: string | null;
  posted_at?: string | null;
  recency?: string | null;
  demand_signal?: string | null;
}

export interface ActionCandidate {
  id: string;
  type:
    | 'whatsapp_post'
    | 'facebook_group_post'
    | 'nextdoor_post'
    | 'warm_text'
    | 'email'
    | 'vendor_form_fill'
    | 'marketplace_listing'
    | 'instagram_post'
    | 'manual_step';
  title: string;
  destination_name: string;
  destination_url?: string | null;
  linked_lead_id?: string | null;
  priority_score: number;
  reason: string;
  expected_outcome: string;
  effort_minutes: number;
  risk_level: 'low' | 'medium' | 'high';
  execution_mode: 'draft_only' | 'fill_no_submit' | 'post_after_review';
  requires_user_approval: boolean;
  draft_text?: string | null;
  form_fields?: Record<string, string> | null;
  actionbook_session_id?: string | null;
  actionbook_screenshot_url?: string | null;
}

export interface ActivationPlan {
  opportunity_id: string;
  mom_display_name: string;
  summary: string;
  recommended_first_action_id?: string | null;
  leads: CustomerLead[];
  actions: ActionCandidate[];
  launch_message_short: string;
  launch_message_friendly: string;
  launch_message_formal: string;
  safety_notes: string[];
  used_live_search: boolean;
}

export interface ActionExecutionResult {
  action_id: string;
  status: 'drafted' | 'filled' | 'posted' | 'submitted' | 'blocked' | 'failed';
  message: string;
  proof_url?: string | null;
  screenshot_url?: string | null;
  actionbook_session_id?: string | null;
  error?: string | null;
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
