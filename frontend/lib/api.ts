import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";

const API_BASE_URL =
  typeof window === "undefined"
    ? process.env.NEXT_INTERNAL_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://backend:8000/api/v1"
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle token refresh or redirect to login
          if (typeof window !== "undefined") {
            localStorage.removeItem("accessToken");
            window.location.href = "/auth/login";
          }
        }
        return Promise.reject(error);
      }
    );
  }

  setAccessToken(token: string | null) {
    this.accessToken = token;
    if (token) {
      localStorage.setItem("accessToken", token);
    } else {
      localStorage.removeItem("accessToken");
    }
  }

  getAccessToken(): string | null {
    if (!this.accessToken) {
      if (typeof window !== "undefined") {
        this.accessToken = localStorage.getItem("accessToken");
      }
    }
    return this.accessToken;
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const api = new ApiClient();

// Role API endpoints
export const roleApi = {
  getAll: (params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
    search?: string;
  }) => api.get("/roles/", { params }),

  getById: (id: string) => api.get(`/roles/${id}`),

  create: (data: {
    organization_id: string;
    title: string;
    seniority: string;
    department?: string;
    tech_stack?: string[];
    description?: string;
  }) => api.post("/roles/", data),

  update: (id: string, data: Partial<{
    title: string;
    seniority: string;
    department: string;
    tech_stack: string[];
    description: string;
    mission: string;
    core_competencies: Record<string, unknown>[];
    interview_stages: Record<string, unknown>[];
    must_have: Record<string, unknown>;
    nice_to_have: Record<string, unknown>;
    is_active: boolean;
  }>) => api.put(`/roles/${id}`, data),

  delete: (id: string, hardDelete?: boolean) =>
    api.delete(`/roles/${id}`, { params: { hard_delete: hardDelete } }),

  deactivate: (id: string) => api.post(`/roles/${id}/deactivate`),

  activate: (id: string) => api.post(`/roles/${id}/activate`),

  duplicate: (id: string, newTitle?: string) =>
    api.post(`/roles/${id}/duplicate`, null, { params: { new_title: newTitle } }),

  // AI Blueprint endpoints
  generateBlueprint: (data: {
    title: string;
    seniority: string;
    stack?: string[];
    team_context?: string;
  }) => api.post("/roles/blueprint/generate", data),

  createWithBlueprint: (data: {
    organization_id: string;
    title: string;
    seniority: string;
    stack?: string[];
    team_context?: string;
  }) => api.post("/roles/blueprint/create", data),

  updateWithBlueprint: (
    id: string,
    data: {
      title: string;
      seniority: string;
      stack?: string[];
      team_context?: string;
    }
  ) => api.post(`/roles/${id}/blueprint/update`, data),

  getBlueprintTemplate: () => api.get("/roles/blueprint/template"),
};

// Interview Kit API endpoints
export const interviewKitApi = {
  getAll: (params?: {
    skip?: number;
    limit?: number;
    organization_id?: string;
    role_id?: string;
    interview_type?: string;
    is_active?: boolean;
    search?: string;
  }) => api.get("/interview-kits/", { params }),

  getById: (id: string) => api.get(`/interview-kits/${id}`),

  create: (data: {
    organization_id: string;
    role_id?: string;
    title: string;
    type: string;
    description?: string;
    problem_statement?: string;
    evaluation_rubric?: Record<string, unknown>[];
    red_flags?: string[];
    good_answer_outline?: string;
    questions?: Record<string, unknown>[];
    estimated_duration_minutes?: number;
    tips_for_interviewer?: string;
  }) => api.post("/interview-kits/", data),

  update: (id: string, data: Partial<{
    title: string;
    description: string;
    problem_statement: string;
    evaluation_rubric: Record<string, unknown>[];
    red_flags: string[];
    good_answer_outline: string;
    questions: Record<string, unknown>[];
    estimated_duration_minutes: number;
    tips_for_interviewer: string;
    is_active: boolean;
  }>) => api.put(`/interview-kits/${id}`, data),

  delete: (id: string, hardDelete?: boolean) =>
    api.delete(`/interview-kits/${id}`, { params: { hard_delete: hardDelete } }),

  duplicate: (id: string, newTitle?: string) =>
    api.post(`/interview-kits/${id}/duplicate`, null, { params: { new_title: newTitle } }),

  // AI Interview Kit endpoints
  generate: (data: {
    role_id?: string;
    role_title: string;
    seniority: string;
    stack?: string[];
    interview_type: string;
    competencies?: string[];
    duration_minutes?: number;
    additional_context?: string;
  }) => api.post("/interview-kits/generate", data),

  createWithAI: (data: {
    organization_id: string;
    role_id?: string;
    role_title: string;
    seniority: string;
    stack?: string[];
    interview_type: string;
    competencies?: string[];
    duration_minutes?: number;
    additional_context?: string;
  }) => api.post("/interview-kits/create-with-ai", data),

  regenerate: (
    id: string,
    data: {
      role_title: string;
      seniority: string;
      stack?: string[];
      interview_type: string;
      competencies?: string[];
      duration_minutes?: number;
      additional_context?: string;
    }
  ) => api.post(`/interview-kits/${id}/regenerate`, data),

  getKitTemplate: () => api.get("/interview-kits/template"),

  getQuestions: (id: string) => api.get(`/interview-kits/${id}/questions`),
};

// Auth API endpoints
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authApi = {
  login: (email: string, password: string) =>
    api.post<Token>("/auth/login/json", { email, password }),

  register: (data: {
    email: string;
    password: string;
    confirm_password: string;
    full_name?: string;
  }) => api.post<Token>("/auth/register", data),

  refreshToken: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),

  getMe: () => api.get("/auth/me"),

  updateMe: (data: {
    full_name?: string;
    phone?: string;
  }) => api.put("/auth/me", data),

  changePassword: (data: {
    current_password: string;
    new_password: string;
    confirm_new_password: string;
  }) => api.post("/auth/change-password", data),
};

// Evaluation API endpoints
export const evaluationApi = {
  getAll: (params?: {
    organization_id?: string;
    role_id?: string;
    candidate_id?: string;
    interviewer_id?: string;
    is_submitted?: boolean;
    is_draft?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get("/evaluations/", { params }),

  getMyDrafts: (params?: {
    skip?: number;
    limit?: number;
  }) => api.get("/evaluations/my-drafts", { params }),

  getById: (id: string) => api.get(`/evaluations/${id}`),

  create: (data: {
    candidate_id: string;
    assignment_id?: string;
    scores: Record<string, unknown>;
    confidence: number;
    strengths?: string;
    weaknesses?: string;
    summary?: string;
    recommendation: string;
    is_draft?: boolean;
  }) => api.post("/evaluations/", data),

  update: (id: string, data: Partial<{
    scores: Record<string, unknown>;
    confidence: number;
    strengths: string;
    weaknesses: string;
    summary: string;
    recommendation: string;
    is_draft: boolean;
  }>) => api.put(`/evaluations/${id}`, data),

  delete: (id: string, hardDelete?: boolean) =>
    api.delete(`/evaluations/${id}`, { params: { hard_delete: hardDelete } }),

  submit: (id: string, validateFirst?: boolean) =>
    api.post(`/evaluations/${id}/submit`, null, { params: { validate_first: validateFirst } }),

  validate: (id: string) => api.get(`/evaluations/${id}/validate`),

  // Candidate scorecards
  getCandidateScorecards: (candidateId: string, submittedOnly?: boolean) =>
    api.get(`/evaluations/candidates/${candidateId}`, { params: { submitted_only: submittedOnly } }),

  getCandidateStats: (candidateId: string) =>
    api.get(`/evaluations/candidates/${candidateId}/stats`),

  getCandidateAverageScores: (candidateId: string) =>
    api.get(`/evaluations/candidates/${candidateId}/average-scores`),

  // AI Feedback Improvement
  improveFeedback: (id: string, data: {
    target: string;
    context?: string;
  }) => api.post(`/evaluations/${id}/improve-feedback`, data),

  suggestEvidence: (id: string, competency: string) =>
    api.post(`/evaluations/${id}/suggest-evidence`, null, { params: { competency } }),

  generateSummary: (id: string) =>
    api.post(`/evaluations/${id}/generate-summary`),

  // Assignment feedback status
  getAssignmentFeedbackStatus: (assignmentId: string) =>
    api.get(`/evaluations/assignments/${assignmentId}/feedback-status`),
};

// Comparison API endpoints
export const comparisonApi = {
  // Compare multiple candidates
  compare: (data: {
    candidate_ids: string[];
    include_evaluations?: boolean;
    include_feedback_summary?: boolean;
  }) => api.post("/comparison/compare", data),

  // Detect signal gaps
  detectSignalGaps: (data: {
    candidate_id: string;
    competency_threshold?: number;
    confidence_threshold?: number;
    variance_threshold?: number;
  }) => api.post("/comparison/signal-gaps", data),

  // Rank candidates
  rank: (params: {
    candidate_ids: string[];
    criteria?: string;
  }) => {
    const queryParams = new URLSearchParams();
    params.candidate_ids.forEach((id) => queryParams.append("candidate_ids", id));
    if (params.criteria) queryParams.set("criteria", params.criteria);
    return api.get(`/comparison/rank?${queryParams.toString()}`);
  },

  // Batch compare many candidates
  batchCompare: (data: {
    candidate_ids: string[];
    max_candidates_per_comparison?: number;
    include_heatmap?: boolean;
  }) => api.post("/comparison/batch", data),

  // Get heatmap data
  getHeatmap: (candidateIds: string[]) => {
    const queryParams = new URLSearchParams();
    candidateIds.forEach((id) => queryParams.append("candidate_ids", id));
    return api.get(`/comparison/heatmap?${queryParams.toString()}`);
  },

  // Get candidate comparison summary
  getSummary: (candidateId: string) =>
    api.get(`/comparison/summary/${candidateId}`),

  // Get comparable candidates for a role
  getRoleCandidates: (params: {
    roleId: string;
    minEvaluations?: number;
    skip?: number;
    limit?: number;
  }) => {
    const queryParams = new URLSearchParams();
    queryParams.set("role_id", params.roleId);
    if (params.minEvaluations) queryParams.set("min_evaluations", params.minEvaluations.toString());
    if (params.skip) queryParams.set("skip", params.skip.toString());
    if (params.limit) queryParams.set("limit", params.limit.toString());
    return api.get(`/comparison/role/${params.roleId}/candidates?${queryParams.toString()}`);
  },

  // Compare all candidates for a role
  compareRoleCandidates: (roleId: string, statusFilter?: string[]) => {
    const queryParams = new URLSearchParams();
    if (statusFilter) {
      statusFilter.forEach((s) => queryParams.append("status_filter", s));
    }
    return api.get(`/comparison/role/${roleId}/comparison?${queryParams.toString()}`);
  },

  // Get candidates at a workflow stage
  getStageCandidates: (workflowId: string, stageId: string) =>
    api.get(`/comparison/workflow/${workflowId}/stage/${stageId}/candidates`),
};

// Decision Brief API endpoints
export const decisionApi = {
  // Generate a decision brief
  generateBrief: (data: {
    candidate_id: string;
    include_comparison?: boolean;
    comparison_candidate_ids?: string[];
    focus_areas?: string[];
    custom_prompt?: string;
  }, organizationId: string) => 
    api.post(`/decisions/brief/generate?organization_id=${organizationId}`, data),

  // Get a specific brief
  getBrief: (briefId: string) =>
    api.get(`/decisions/brief/${briefId}`),

  // Get briefs for a candidate
  getCandidateBriefs: (candidateId: string, organizationId: string) =>
    api.get(`/decisions/candidates/${candidateId}/briefs?organization_id=${organizationId}`),

  // Get signal analysis for a candidate
  getSignalAnalysis: (candidateId: string) =>
    api.get(`/decisions/candidates/${candidateId}/signal-analysis`),

  // Get evaluation statistics for a candidate
  getCandidateStats: (candidateId: string) =>
    api.get(`/decisions/candidates/${candidateId}/statistics`),

  // Get candidates eligible for decision briefs
  getComparableCandidates: (params: {
    organization_id: string;
    role_id?: string;
    min_evaluations?: number;
    skip?: number;
    limit?: number;
  }) => api.get("/decisions/candidates", { params }),

  // Bulk generate briefs
  bulkGenerateBriefs: (candidateIds: string[], organizationId: string) =>
    api.post(`/decisions/brief/bulk-generate?organization_id=${organizationId}`, candidateIds),

  // Get decision summary
  getDecisionSummary: (params: {
    organization_id: string;
    role_id?: string;
    min_evaluations?: number;
    skip?: number;
    limit?: number;
  }) => api.get("/decisions/summary", { params }),
};

// Candidate API endpoints
export const candidateApi = {
  getAll: (params?: {
    skip?: number;
    limit?: number;
    organization_id?: string;
    role_id?: string;
    workflow_id?: string;
    stage_id?: string;
    status?: string;
    is_active?: boolean;
    search?: string;
  }) => api.get("/candidates/", { params }),

  getById: (id: string) => api.get(`/candidates/${id}`),

  create: (data: {
    organization_id: string;
    full_name: string;
    email: string;
    phone?: string;
    resume_url?: string;
    linkedin_url?: string;
    portfolio_url?: string;
    role_id?: string;
    source?: string;
    status?: string;
    candidate_metadata?: Record<string, unknown>;
  }) => api.post("/candidates/", data),

  update: (id: string, data: Partial<{
    full_name: string;
    email: string;
    phone: string;
    resume_url: string;
    linkedin_url: string;
    portfolio_url: string;
    role_id: string;
    status: string;
    source: string;
    is_active: boolean;
    candidate_metadata: Record<string, unknown>;
  }>) => api.put(`/candidates/${id}`, data),

  delete: (id: string, hardDelete?: boolean) =>
    api.delete(`/candidates/${id}`, { params: { hard_delete: hardDelete } }),

  // Candidate stage/workflow endpoints
  assignToStage: (candidateId: string, data: {
    workflow_id: string;
    stage_id: string;
  }) =>
    api.post("/workflows/candidates/move", {
      candidate_id: candidateId,
      to_stage_id: data.stage_id,
    }),

  moveToStage: (candidateId: string, data: {
    stage_id: string;
    notes?: string;
  }) =>
    api.post("/workflows/candidates/move", {
      candidate_id: candidateId,
      to_stage_id: data.stage_id,
      reason: data.notes,
    }),

  // Candidate evaluations
  getEvaluations: (candidateId: string) =>
    api.get(`/evaluations/candidates/${candidateId}`),
};

// Organization API endpoints
export const organizationApi = {
  getAll: (params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
  }) => api.get("/organizations/", { params }),

  getById: (id: string) => api.get(`/organizations/${id}`),

  create: (data: {
    name: string;
    description?: string;
    website?: string;
    logo_url?: string;
    industry?: string;
    size?: string;
    location?: string;
  }) => api.post("/organizations/", data),

  update: (id: string, data: Partial<{
    name: string;
    description: string;
    website: string;
    logo_url: string;
    industry: string;
    size: string;
    location: string;
    is_active: boolean;
  }>) => api.put(`/organizations/${id}`, data),

  delete: (id: string) => api.delete(`/organizations/${id}`),

  getStats: (id: string) => api.get(`/organizations/stats`, { params: { organization_id: id } }),

  // Organization members
  getMembers: (organizationId: string, params?: {
    skip?: number;
    limit?: number;
  }) => api.get(`/organizations/${organizationId}/members`, { params }),

  addMember: (organizationId: string, data: {
    user_id: string;
    role?: string;
  }) => api.post(`/organizations/${organizationId}/members`, null, { params: data }),

  updateMemberRole: (organizationId: string, userId: string, role: string) =>
    api.put(`/organizations/${organizationId}/members/${userId}`, null, { params: { role } }),

  removeMember: (organizationId: string, userId: string) =>
    api.delete(`/organizations/${organizationId}/members/${userId}`),

  checkMembership: (organizationId: string, userId: string) =>
    api.get(`/organizations/${organizationId}/members/${userId}`),
};
