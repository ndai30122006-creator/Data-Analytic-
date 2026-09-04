export interface LoginResponse { access_token: string; token_type: string; username: string; expires_in: number }
export interface RegisterRequest { username: string; password: string }
export interface LoginRequest { username: string; password: string }
export interface DatasetMeta { dataset_name: string; rows: number; cols: number; created_at: string | null }
export interface DatasetListResponse { datasets: DatasetMeta[]; username: string; count: number }
export interface ProfileResponse { dataset_id: number; dataset_name: string; profile: Record<string, unknown> }
export interface IngestResponse { message: string; dataset_id?: number; profile?: Record<string, unknown>; quality?: unknown }
export interface PipelineSpec { name: string; source: string; target: string; steps: PipelineStep[] }
export interface PipelineStep { id: string; op: string; params?: Record<string, unknown>; depends_on?: string[] }
export interface RunStarted { run_id: string; status: string }
export interface RunInfo { run_id: string; pipeline_id: string; status: string; result: Record<string, unknown>; created_at: string | null }
export interface BriefItem { id: string | number; version?: number; content?: string; created_at?: string }
export interface ChartSpec { type: 'kpi'|'bar'|'hist'|'box'|'line'|'scatter'; title?: string; x?: string; y?: string; metric?: { column?: string; aggregation?: string }; bins?: number }
export interface DashboardSpec { name: string; source: string; charts: ChartSpec[] }
export interface AnalysisRequest { dataset_name: string; analysis_type: string; params?: Record<string, unknown> }
export interface AnalysisResponse { status: string; username: string; dataset: string; analysis_type: string; results: unknown }
export interface HealthResponse { status: string }
export interface EnvValidateResponse { status: string; warnings: string[]; cors_origins?: string[]; rate_limiter?: string }
