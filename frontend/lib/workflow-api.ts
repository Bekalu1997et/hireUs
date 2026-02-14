import { api } from "./api";

/**
 * Workflow API endpoints
 */
export const workflowApi = {
  // Workflow CRUD
  getAll: (params?: {
    skip?: number;
    limit?: number;
  }) => api.get("/workflows/", { params }),

  getById: (id: string) => api.get(`/workflows/${id}`),

  getDefault: (organizationId?: string) =>
    api.get("/workflows/default", { params: { organization_id: organizationId } }),

  createDefault: (organizationId?: string) =>
    api.post("/workflows/default", null, { params: { organization_id: organizationId } }),

  getTemplate: () => api.get<WorkflowTemplateResponse>("/workflows/template"),

  create: (data: {
    organization_id: string;
    name: string;
    description?: string;
    stages?: WorkflowStage[];
    is_default?: boolean;
  }) => api.post("/workflows/", data),

  update: (id: string, data: Partial<{
    name: string;
    description: string;
    stages: WorkflowStage[];
    is_default: boolean;
    is_active: boolean;
  }>) => api.put(`/workflows/${id}`, data),

  delete: (id: string, hardDelete?: boolean) =>
    api.delete(`/workflows/${id}`, { params: { hard_delete: hardDelete } }),

  setDefault: (id: string, organizationId?: string) =>
    api.post(`/workflows/${id}/set-default`, null, { params: { organization_id: organizationId } }),

  getStats: (id: string) => api.get(`/workflows/${id}/stats`),

  // Stage management
  addStage: (workflowId: string, stageData: Record<string, unknown>) =>
    api.post(`/workflows/${workflowId}/stages`, stageData),

  updateStage: (workflowId: string, stageId: string, stageData: Record<string, unknown>) =>
    api.put(`/workflows/${workflowId}/stages/${stageId}`, stageData),

  deleteStage: (workflowId: string, stageId: string) =>
    api.delete(`/workflows/${workflowId}/stages/${stageId}`),

  reorderStages: (workflowId: string, stageOrders: { id: string; order: number }[]) =>
    api.put(`/workflows/${workflowId}/stages/reorder`, stageOrders),

  // Candidate stage transitions
  moveCandidate: (data: {
    candidate_id: string;
    to_stage_id: string;
    reason?: string;
    skip_feedback_check?: boolean;
  }) => api.post("/workflows/candidates/move", data, { params: { skip_feedback_check: data.skip_feedback_check } }),

  bulkMoveCandidates: (data: {
    candidate_ids: string[];
    to_stage_id: string;
    reason?: string;
  }) => api.post("/workflows/candidates/bulk-move", data),

  validateMove: (candidateId: string, targetStageId: string) =>
    api.get(`/workflows/candidates/${candidateId}/validate-move/${targetStageId}`),

  // Feedback status
  getFeedbackStatus: (candidateId: string) =>
    api.get(`/workflows/candidates/${candidateId}/feedback-status`),

  getStageHistory: (candidateId: string, limit?: number) =>
    api.get(`/workflows/candidates/${candidateId}/stage-history`, { params: { limit } }),

  // Interviewer assignments
  assignInterviewer: (data: {
    candidate_id: string;
    interviewer_id: string;
    interview_kit_id?: string;
    scheduled_at?: string;
    duration_minutes?: number;
    notes?: string;
  }) => api.post("/workflows/assignments", data),

  reassignInterviewer: (assignmentId: string, data: {
    new_interviewer_id: string;
    reason?: string;
  }) => api.put(`/workflows/assignments/${assignmentId}/reassign`, data),

  cancelAssignment: (assignmentId: string, reason?: string) =>
    api.post(`/workflows/assignments/${assignmentId}/cancel`, null, { params: { reason } }),

  getCandidateAssignments: (candidateId: string) =>
    api.get(`/workflows/candidates/${candidateId}/assignments`),

  getPendingAssignments: (params?: {
    interviewer_id?: string;
    skip?: number;
    limit?: number;
  }) => api.get("/workflows/assignments/pending", { params }),
};

// Types for workflow data
export interface WorkflowStage {
  id: string;
  name: string;
  order: number;
  description?: string;
  color: string;
  required_feedback_count: number;
  interview_types: string[];
}

export interface Workflow {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  stages: WorkflowStage[];
  is_default: boolean;
  is_active: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkflowListResponse {
  items: Workflow[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface WorkflowDetail extends Workflow {
  candidates_count?: Record<string, number>;
}

export interface MoveCandidateRequest {
  candidate_id: string;
  to_stage_id: string;
  reason?: string;
  skip_feedback_check?: boolean;
}

export interface StageTransitionResult {
  success: boolean;
  candidate_id: string;
  from_stage?: string;
  to_stage: string;
  message: string;
  blocked_reason?: string;
}

export interface CanMoveCandidateResponse {
  can_move: boolean;
  candidate_id: string;
  current_stage_id?: string;
  required_feedbacks: number;
  submitted_feedbacks: number;
  missing_feedbacks: string[];
  blocked_reason?: string;
}

export interface AssignmentResponse {
  id: string;
  candidate_id: string;
  interviewer_id: string;
  interviewer_name?: string;
  interview_kit_id?: string;
  interview_kit_title?: string;
  scheduled_at?: string;
  duration_minutes: number;
  status: string;
  notes?: string;
  feedback_required: boolean;
  feedback_submitted: boolean;
  created_at: string;
}

export interface FeedbackStatusResponse {
  candidate_id: string;
  candidate_name: string;
  current_stage_id?: string;
  current_stage_name?: string;
  total_required_feedbacks: number;
  total_submitted_feedbacks: number;
  is_blocked: boolean;
  blocked_reason?: string;
  assignments: AssignmentResponse[];
}

export interface WorkflowStatsResponse {
  workflow_id: string;
  total_candidates: number;
  active_candidates: number;
  completed_candidates: number;
  rejected_candidates: number;
  stage_stats: {
    stage_id: string;
    stage_name: string;
    candidate_count: number;
    avg_time_in_stage_hours?: number;
    feedback_completion_rate: number;
  }[];
}

export interface WorkflowTemplateResponse {
  name: string;
  description: string;
  stages: WorkflowStage[];
  use_template: string;
}

