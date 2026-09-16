export type RecordStatus =
  | 'NEW'
  | 'SCRAPING_IN_PROGRESS'
  | 'SCRAPING_COMPLETED'
  | 'MATCH_FOUND'
  | 'NO_MATCH_FOUND'
  | 'MANUAL_REVIEW'
  | 'FAILED'
  | 'COMPLETED';

export type FuzzyMatchStatus =
  | 'NEW'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'NO_MATCH_FOUND'
  | 'PENDING_REVIEW';

export type BotStatus =
  | 'NOT_TRIGGERED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'FAILED'
  | 'NO_MATCH_FOUND'
  | 'BLOCKED';

export interface BotDetail {
  name: string;
  website_url: string;
  target: 'Yes' | 'No';
  status: BotStatus;
  cases_found: number;
}

export interface ScrapedCourtCase {
  id: string;
  county_name: string;
  case_number: string;
  case_style: string;
  filing_date?: string;
  party_name_searched?: string;
  source_url?: string;
  county_website?: string;
  case_status?: string;
  case_type?: string;
  raw_payload?: Record<string, any>;
  created_at?: string;
}

export interface ErrorScreenshot {
  id: string;
  claim_id: string;
  portal_key?: string;
  portal_name?: string;
  portal?: string;
  county?: string;
  page_url?: string;
  page_title?: string;
  exception_message?: string;
  error_message?: string;
  error_stage?: string;
  attempt_number?: number;
  storage_provider?: string;
  file_path?: string;
  file_size_bytes?: number;
  content_type?: string;
  image_url: string;
  created_at?: string;
}

export interface Claim {
  id: string;
  batch_id?: string;
  claim_number: string;
  exposure_number?: string;
  primary_key?: string;
  dol?: string;
  date_of_loss?: string;
  insured_name: string;
  claimant_name: string;
  driver_name: string;
  insured_first_name?: string;
  insured_last_name?: string;
  claimant_first_name?: string;
  claimant_last_name?: string;
  driver_first_name?: string;
  driver_last_name?: string;
  // garaging_city, garaging_state, loss_location_city, loss_location_county
  // removed from ingestion, forms, and type surface (DB columns preserved for data integrity)
  loss_location_state?: string;
  policy_state?: string;
  record_status: RecordStatus;
  fuzzy_match_status: FuzzyMatchStatus;
  bots: BotDetail[];
  court_cases: ScrapedCourtCase[];
  final_matched_json?: Record<string, any>;
  activity_id?: string;
  retry_count: number;
  last_error?: string;
  action_timings?: Record<string, any>;
  total_duration_seconds?: number;
  created_at: string;
  updated_at: string;
}

export interface ClaimStats {
  total_claims: number;
  new: number;
  in_progress: number;
  match_found: number;
  manual_review: number;
  no_match_found?: number;
  failed: number;
  completed: number;
}

export interface MatchPair {
  id: string;
  claim_id: string;
  court_case_id: string;
  party_type: 'CLAIMANT' | 'INSURED' | 'DRIVER';
  party_name: string;
  case_style: string;
  county_name?: string;
  case_number?: string;
  filing_date?: string;
  county_website?: string;
  similarity_score: number;
  threshold_applied: number;
  is_match: boolean;
  review_status: 'AUTO_MATCHED' | 'PENDING_REVIEW' | 'APPROVED' | 'REJECTED';
  reviewed_by?: string;
  reviewed_at?: string;
  review_notes?: string;
  created_at: string;
}

export interface QueueStatus {
  active_tasks: number;
  pending_tasks: number;
  failed_tasks: number;
  completed_tasks: number;
  queues: Record<string, number>;
  workers_online: number;
}

export interface LiveQueueItem {
  id: string;
  claim_number: string;
  exposure_number?: string;
  insured_name?: string;
  claimant_name?: string;
  driver_name?: string;
  dol?: string;
  policy_state?: string;
  loss_location_state?: string;
  record_status: string;
  fuzzy_match_status?: string;
  queue_position?: number;
  portals_to_run: string[];
  bot_statuses: Record<string, string>;
  total_duration_seconds?: number;
  current_portal?: string;
  created_at?: string;
  updated_at?: string;
}

export interface LiveQueueState {
  auto_queue_enabled: boolean;
  is_running: boolean;
  current_claim_id?: string;
  max_concurrency: number;
  available_slots: number;
  active_items: LiveQueueItem[];
  active_item: LiveQueueItem | null;
  pending_items: LiveQueueItem[];
  recently_completed: LiveQueueItem[];
  total_pending_count: number;
  total_in_progress_count: number;
  workers_online: number;
}

export interface IngestionBatch {
  id: string;
  filename: string;
  total_records: number;
  processed_records: number;
  failed_records: number;
  duplicate_records?: number;
  invalid_records?: number;
  mapping_config?: Record<string, string>;
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED';
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface AutomationSettings {
  max_captcha_attempts: number;
  captcha_wait_seconds: number;
  page_timeout_seconds: number;
  reload_backoff_seconds: number;
  headless_mode: boolean;
  max_concurrent_claims?: number;
  browser_engine?: "chromium" | "chrome" | "msedge";
  use_chrome_browser?: boolean;
  chrome_binary_path?: string | null;
  chrome_extension_dir?: string | null;
  anticaptcha_api_key?: string | null;
  chrome_user_data_dir?: string | null;
  user_agent?: string;
  extension_setup_verified?: boolean;
  extension_setup_timestamp?: string | null;
  typing_speed_mode?: "turbo" | "fast" | "balanced" | "cautious" | string;
  typing_delay_ms?: number;
  action_pacing_ms?: number;
  stealth_clicks?: boolean;
}

export interface ExtensionSetupResponse {
  status: string;
  extension_id: string;
  pinned_to_toolbar: boolean;
  persistent_profile_path: string;
  verified: boolean;
  timestamp: string;
  message: string;
}

export interface PortalsSettings {
  broward_url: string;
  broward_enabled: boolean;
  hillsborough_url: string;
  hillsborough_enabled: boolean;
  miami_url: string;
  miami_enabled: boolean;
  miami_username?: string;
  miami_password?: string;
  miami_requires_login?: boolean;
  travis_url: string;
  travis_enabled: boolean;
  dallas_url: string;
  dallas_enabled: boolean;
  harris_jp_url: string;
  harris_jp_enabled: boolean;
  harris_cclerk_url: string;
  harris_cclerk_enabled: boolean;
  harris_district_url: string;
  harris_district_enabled: boolean;
}

export interface FuzzyMatcherSettings {
  auto_match_threshold: number;
  manual_review_threshold: number;
  scorer_algorithm: string;
  min_filing_date: string;
  unique_names_threshold?: number;
  clean_party_name_patterns: string[];
  clean_case_style_patterns?: string[];
  whitelisted_statuses: string[];
  whitelisted_case_types: string[];
}

export interface IntegrationSettings {
  guidewire_mock_mode: boolean;
  guidewire_api_url: string;
  guidewire_auth_type: string;
  guidewire_api_key: string;
  guidewire_client_id: string;
  guidewire_client_secret: string;
  guidewire_timeout_seconds: number;
  auto_push_on_match: boolean;
  notification_email: string;
  notification_dispatch_mode?: "direct_system" | "guidewire_activity" | "both" | string;
}

export interface TaskQueueSettings {
  max_task_retries: number;
  task_retry_delay_seconds: number;
  batch_chunk_size: number;
  auto_retry_failed_scrapes: boolean;
  max_concurrent_claims?: number;
}

export interface ThemePalette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  card: string;
  header: string;
  sidebar: string;
  text: string;
  text_muted: string;
  border: string;
  divider: string;
  input_background: string;
  input_text: string;
  button: string;
  button_text: string;
  link: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  focus: string;
  hover: string;
  active: string;
  selected: string;
  disabled: string;
}

export interface BrandingSettings {
  app_title: string;
  app_subtitle: string;
  app_logo_url: string;
  badge_letter: string;
  theme_accent?: string;
  light_palette?: ThemePalette;
  dark_palette?: ThemePalette;
}

export interface StorageSettings {
  capture_error_screenshots: boolean;
  storage_provider: "local" | "s3" | "azure_blob" | "gcs" | string;
  s3_bucket_name?: string;
  s3_region?: string;
  s3_access_key?: string;
  s3_secret_key?: string;
  azure_connection_string?: string;
  azure_container_name?: string;
  gcs_bucket_name?: string;
  gcs_project_id?: string;
  gcs_credentials_json?: string;
}

export interface SystemSettings {
  automation: AutomationSettings;
  portals: PortalsSettings;
  matcher: FuzzyMatcherSettings;
  integration: IntegrationSettings;
  queue: TaskQueueSettings;
  branding?: BrandingSettings;
  storage?: StorageSettings;
  email?: EmailSettings;
  proxy?: ProxySettings;
}

export interface ProxySettings {
  enabled: boolean;
  host: string;
  port: number;
  username?: string;
  password?: string;
}

export interface StorageTestRequest {
  storage_provider: string;
  s3_bucket_name?: string;
  s3_region?: string;
  s3_access_key?: string;
  s3_secret_key?: string;
  azure_connection_string?: string;
  azure_container_name?: string;
  gcs_bucket_name?: string;
  gcs_project_id?: string;
  gcs_credentials_json?: string;
}

export interface StorageTestResponse {
  success: boolean;
  storage_provider: string;
  message: string;
  duration_ms: number;
  details?: Record<string, any>;
  error_detail?: string;
}

export interface GuidewireTestRequest {
  api_url?: string;
  auth_type?: string;
  api_key?: string;
  client_id?: string;
  client_secret?: string;
  mock_mode?: boolean;
  timeout_seconds?: number;
  custom_payload?: Record<string, any>;
}

export interface GuidewireTestResponse {
  success: boolean;
  status_code: number;
  status_text: string;
  duration_ms: number;
  request_url: string;
  request_method: string;
  request_headers: Record<string, string>;
  request_body: Record<string, any>;
  response_headers: Record<string, string>;
  response_body: any;
  error_detail?: string;
}

export interface PortalTestRequest {
  portal_name: string;
  url: string;
  timeout_seconds?: number;
}

export interface PortalTestResponse {
  portal_name: string;
  url: string;
  reachable: boolean;
  status_code?: number;
  status_text: string;
  duration_ms: number;
  error_detail?: string;
}

export interface BrowserTestRequest {
  headless?: boolean;
  browser_engine?: "chromium" | "chrome" | "msedge";
  test_url?: string;
  timeout_seconds?: number;
  chrome_binary_path?: string | null;
  chrome_extension_dir?: string | null;
}

export interface BrowserTestResponse {
  success: boolean;
  mode: string;
  browser_engine?: string;
  headless: boolean;
  chrome_found: boolean;
  chrome_executable?: string | null;
  extension_found: boolean;
  extension_path?: string | null;
  extension_loaded?: boolean;
  extension_id?: string | null;
  service_worker_active?: boolean;
  warning?: string | null;
  page_title?: string | null;
  duration_ms: number;
  message: string;
  error_detail?: string | null;
}

export interface FilePreviewRecord {
  row_number: number;
  claim_number: string;
  insured_name?: string;
  claimant_name?: string;
  driver_name?: string;
  dol?: string;
  policy_state?: string;
  loss_location?: string;
  target_bots: string[];
}

export interface TargetFieldDefinition {
  key: string;
  label: string;
  required: boolean;
  description: string;
}

export interface ColumnMappingRecommendation {
  target_key: string;
  target_label: string;
  source_column: string | null;
  confidence: 'EXACT' | 'HIGH_FUZZY' | 'LOW_FUZZY' | 'UNMAPPED';
  confidence_score: number;
  required: boolean;
}

export interface ValidationIssue {
  row_number: number;
  claim_number?: string | null;
  issue_type: 'INVALID' | 'DUPLICATE_IN_FILE' | 'DUPLICATE_IN_DB';
  reason: string;
}

export interface FileValidationResult {
  filename: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  duplicate_rows: number;
  duplicate_strategy: 'SKIP' | 'OVERWRITE' | 'IMPORT_ALL';
  florida_claims_count: number;
  texas_claims_count: number;
  cross_state_claims_count: number;
  estimated_bot_runs: number;
  issues: ValidationIssue[];
  preview_records: FilePreviewRecord[];
  can_proceed: boolean;
}

export interface FilePreviewData {
  filename: string;
  filesize_bytes: number;
  filesize_formatted: string;
  file_type: string;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  sheet_names: string[];
  detected_columns: string[];
  column_samples?: Record<string, string[]>;
  target_fields?: TargetFieldDefinition[];
  mapping_recommendations?: ColumnMappingRecommendation[];
  florida_claims_count: number;
  texas_claims_count: number;
  cross_state_claims_count: number;
  estimated_bot_runs: number;
  preview_records: FilePreviewRecord[];
}

export type HealthStatus = 'healthy' | 'warning' | 'critical';

export interface HealthComponentDetail {
  name: string;
  status: HealthStatus;
  latency_ms?: number;
  details: Record<string, any>;
}

export interface HealthPortalDetail {
  key: string;
  name: string;
  state: string;
  url: string;
  enabled: boolean;
  has_dol: boolean;
  has_casetype: boolean;
  login_required?: boolean;
}

export interface SystemHealthData {
  status: HealthStatus;
  timestamp: string;
  environment: string;
  version: string;
  components: {
    api: HealthComponentDetail;
    database: HealthComponentDetail;
    redis: HealthComponentDetail;
    celery: HealthComponentDetail;
    chrome: HealthComponentDetail;
    anticaptcha: HealthComponentDetail;
    guidewire: HealthComponentDetail;
    storage: HealthComponentDetail;
    [key: string]: HealthComponentDetail;
  };
  portals: Record<string, HealthPortalDetail>;
}

export interface PortalPingResponse {
  portal_key: string;
  portal_name: string;
  url: string;
  reachable: boolean;
  status_code: number;
  latency_ms: number;
  status: HealthStatus;
  error?: string;
}

export interface RetryFailedResponse {
  status: string;
  message: string;
  retried_portals: string[];
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  ip_address?: string | null;
  user_agent?: string | null;
  action: string;
  entity_type: string;
  entity_id?: string | null;
  claim_number?: string | null;
  description: string;
  status: string;
  details?: Record<string, any> | null;
}

export interface AuditLogListResponse {
  items: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AuditLogStats {
  total_events: number;
  total_today: number;
  total_claims_ops: number;
  total_settings_ops: number;
  total_match_reviews: number;
  total_failures: number;
  by_action: Record<string, number>;
  by_entity_type: Record<string, number>;
  by_status: Record<string, number>;
}

export interface AuditLogQueryParams {
  page?: number;
  page_size?: number;
  action?: string;
  entity_type?: string;
  entity_id?: string;
  claim_number?: string;
  user_id?: string;
  status?: string;
  search?: string;
  start_date?: string;
  end_date?: string;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
}

export interface EmailSettings {
  email_notifications_enabled: boolean;
  provider: "local_mock" | "maildev" | "smtp" | "direct_mx" | "graph" | "sendgrid" | "ses" | string;
  maildev_web_url?: string;
  smtp_host: string;
  smtp_port: number;
  smtp_username?: string;
  smtp_password?: string;
  smtp_encryption: "tls" | "ssl" | "none" | string;
  from_name: string;
  from_email: string;
  reply_to?: string;
  // Microsoft Graph configuration
  graph_tenant_id?: string;
  graph_client_id?: string;
  graph_client_secret?: string;
  // Amazon SES configuration
  ses_region?: string;
  ses_access_key_id?: string;
  ses_secret_access_key?: string;
  to_recipients: string[];
  cc_recipients: string[];
  bcc_recipients: string[];
  timeout_seconds: number;
  retry_count: number;
  retry_delay_seconds: number;
  rules: {
    guidewire_activity_created?: boolean;
    guidewire_activity_failed?: boolean;
    scraper_failed?: boolean;
    claim_failed?: boolean;
    [key: string]: boolean | undefined;
  };
}

export interface EmailConnectionTestRequest {
  provider?: string;
  smtp_host?: string;
  smtp_port?: number;
  smtp_username?: string;
  smtp_password?: string;
  smtp_encryption?: string;
  graph_tenant_id?: string;
  graph_client_id?: string;
  graph_client_secret?: string;
  ses_region?: string;
  ses_access_key_id?: string;
  ses_secret_access_key?: string;
  timeout_seconds?: number;
  recipient_domain?: string;
}

export interface EmailConnectionTestResponse {
  success: boolean;
  provider: string;
  message: string;
  duration_ms: number;
  error_detail?: string | null;
}

export interface TestEmailSendRequest {
  recipient: string;
  subject?: string;
  body?: string;
  provider?: string;
}

export interface TestEmailSendResponse {
  success: boolean;
  notification_id: string;
  recipient: string;
  status: string;
  message: string;
  duration_ms: number;
  error_detail?: string | null;
}

export interface NotificationItem {
  id: string;
  event_type: string;
  claim_id?: string | null;
  claim_number?: string | null;
  recipient: string;
  cc?: string | null;
  bcc?: string | null;
  subject: string;
  provider: string;
  status: "PENDING" | "QUEUED" | "SENDING" | "SENT" | "FAILED" | "RETRYING" | "SKIPPED" | string;
  error_message?: string | null;
  retry_count: number;
  created_at: string;
  sent_at?: string | null;
  failed_at?: string | null;
  delivery_receipt?: Record<string, any> | null;
  details?: Record<string, any> | null;
}

export interface NotificationListResponse {
  items: NotificationItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TemplateParameter {
  token: string;
  label: string;
  category: string;
  description: string;
  sample: string;
}

export interface TemplatePreviewRequest {
  event_type?: string;
  subject_template?: string;
  body_template_html?: string;
  body_template_text?: string;
  template_str?: string;
  sample_data?: Record<string, any>;
  context?: Record<string, any>;
  is_html?: boolean;
}

export interface TemplatePreviewResponse {
  event_type: string;
  subject: string;
  body_html: string;
  body_text?: string;
  rendered_content?: string;
}

export interface NotificationTemplate {
  id: string;
  name: string;
  event_type: string;
  subject_template: string;
  body_template_html: string;
  body_template_text?: string | null;
  is_active: boolean;
  is_custom?: boolean;
  updated_at?: string | null;
  available_variables?: string[];
  parameter_catalog?: TemplateParameter[];
}

export interface TemplateUpdateRequest {
  name?: string;
  subject_template: string;
  body_template_html: string;
  body_template_text?: string | null;
  is_active?: boolean;
}

export interface NotificationRule {
  id?: string;
  event_type: string;
  description: string;
  enabled: boolean;
  recipients_override?: string[];
}

// --- New: Fuzzy Match Search (Legacy Power Automate API) ---

export interface FuzzyMatchItem {
  court_case_id: string;
  case_number: string;
  case_style: string;
  county_name: string;
  county_website?: string;
  filing_date?: string;
  case_status?: string;
  case_type?: string;
  similarity_score: number;
  claim_id?: string;
}

export interface FuzzySearchRequest {
  search_name: string;
  threshold?: number;
  party_type?: string;
  limit?: number;
  min_filing_year?: number;
}

export interface FuzzySearchResponse {
  matches: FuzzyMatchItem[];
  total: number;
  threshold_applied: number;
  search_name: string;
  duration_ms: number;
}

export interface UniqueNameItem {
  party_type: string;
  first_name?: string | null;
  last_name?: string | null;
  full_name: string;
  search_order: number;
}

export interface UniqueNamesPartyItem {
  FirstName?: string;
  LastName?: string;
  MiddleName?: string;
  Suffix?: string;
  first_name?: string;
  last_name?: string;
  name?: string;
  [key: string]: any;
}

export interface UniqueNamesRequest {
  claim_id?: string;
  claim_number?: string | null;
  threshold?: number;
  noise_patterns?: string[];
  insured_first_name?: string | null;
  insured_last_name?: string | null;
  driver_first_name?: string | null;
  driver_last_name?: string | null;
  claimant_first_name?: string | null;
  claimant_last_name?: string | null;
  Claimants?: (UniqueNamesPartyItem | string)[];
  claimants?: (UniqueNamesPartyItem | string)[];
  Insureds?: (UniqueNamesPartyItem | string)[];
  insureds?: (UniqueNamesPartyItem | string)[];
  Drivers?: (UniqueNamesPartyItem | string)[];
  drivers?: (UniqueNamesPartyItem | string)[];
  parties?: (UniqueNamesPartyItem | string)[];
  [key: string]: any;
}

export interface UniqueNamesResponse {
  unique_names: UniqueNameItem[];
  total_unique_names: number;
  count: number;
}

export interface FuzzyMatchScore {
  target_string: string;
  result: string;
  score: number;
}

export interface DirectFuzzyMatchRequest {
  text1?: string;
  text2?: string;
  threshold?: number;
  filing_date?: string;
  min_filing_date?: string;
  cases?: Array<{
    CaseNumber?: string;
    case_number?: string;
    CaseStyle?: string;
    case_style?: string;
    FilingDate?: string;
    filing_date?: string;
    [key: string]: any;
  }>;
  reference_string?: string;
  target_strings?: string[];
}

export interface FuzzyMatchCaseResult {
  case_number: string;
  case_style: string;
  filing_date: string;
  score: number;
  result: string;
  guidewire_eligible: boolean;
  filter_reason?: string | null;
}

export interface DirectFuzzyMatchResponse {
  result: string;
  score: number;
  text1?: string;
  text2?: string;
  threshold_applied?: number;
  filing_date?: string;
  min_filing_date?: string;
  guidewire_eligible?: boolean;
  filter_reason?: string | null;
  reference_string?: string;
  matches?: FuzzyMatchScore[];
  cases_results?: FuzzyMatchCaseResult[];
}

// --- New: Extract Unique Party Names ---

export interface ExtractNamesResponse {
  insured: string[];
  driver: string[];
  claimant: string[];
  total: number;
}

// --- New: Anti-Captcha API Key Test ---

export interface AntiCaptchaTestResponse {
  status: 'ok' | 'error';
  balance?: number | null;
  message: string;
  latency_ms: number;
  error_code?: string | null;
}

// --- Enterprise Data Cleanup & Retention Types ---

export interface CleanupCategory {
  id: string;
  name: string;
  description: string;
  is_database: boolean;
  current_count: number;
}

export interface CleanupPreviewRequest {
  categories: string[];
  time_scope?: string;
  n_units?: number;
  start_date?: string;
  end_date?: string;
  before_date?: string;
  after_date?: string;
}

export interface CleanupPreviewResponse {
  time_scope: string;
  start_time?: string | null;
  end_time?: string | null;
  categories: string[];
  record_counts: Record<string, number>;
  file_counts: Record<string, number>;
  total_database_records: number;
  total_files: number;
  can_proceed: boolean;
  warnings: string[];
}

export interface CleanupExecuteRequest {
  categories: string[];
  time_scope?: string;
  n_units?: number;
  start_date?: string;
  end_date?: string;
  before_date?: string;
  after_date?: string;
  confirmed?: boolean;
  dry_run?: boolean;
}

export interface CleanupExecuteResponse {
  cleanup_id: string;
  success: boolean;
  started_at: string;
  completed_at: string;
  time_scope: string;
  start_time?: string | null;
  end_time?: string | null;
  records_deleted: Record<string, number>;
  total_records_deleted: number;
  files_deleted: number;
  redis_purged: boolean;
  referential_integrity: string;
  dashboard_reconciliation: string;
  notification_history_reconciliation: string;
  message: string;
  details?: Record<string, any>;
}
