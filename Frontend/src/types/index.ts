export interface User {
  id: number;
  username: string;
  email: string;
  role_id: number;
  is_active: boolean;
  must_change_password: boolean;
}

export interface Repository {
  id: number;
  name: string;
  root_path: string;
  description: string;
  is_active: boolean;
}

export interface Asset {
  id: number;
  repository_id: number;
  relative_path: string;
  file_name: string;
  size_bytes: number;
  is_active: boolean;
  expected_sha256?: string;
}

export interface Alert {
  id: number;
  event_id: number;
  status: 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED';
  created_at: string;
  resolution_note?: string;
}

export interface SecurityEvent {
  id: number;
  event_type: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  expected_sha256?: string;
  actual_sha256?: string;
  detected_at: string;
  details_json?: any;
}

export interface DashboardSummary {
  total_repositories: number;
  open_alerts: number;
  last_scan: {
    id: number;
    status: string;
    started_at: string;
    summary: Record<string, number>;
  } | null;
}