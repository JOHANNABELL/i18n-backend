import { UUID } from 'crypto';

// ============================================================================
// ======================== TYPESCRIPT INTERFACES ===========================
// ============================================================================

// Auth
interface RegisterDTO {
  email: string;
  name: string;
  password: string;
}

interface LoginDTO {
  username: string;
  password: string;
}

interface Token {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  id: string;
  email: string;
  name: string;
}

interface PasswordChangeDTO {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

// Organizations
interface OrganizationCreateDTO {
  name: string;
  description: string;
}

interface OrganizationUpdateDTO {
  name?: string;
  description?: string;
}

interface OrganizationResponse {
  id: string;
  name: string;
  description: string;
  created_at: string;
  created_by: string;
}

// Organization Members
interface OrganizationMemberCreateDTO {
  user_id: string;
  organization_id: string;
  role: string;
}

interface OrganizationMemberUpdateDTO {
  organization_id: string;
  user_id: string;
  new_role: string;
}

interface OrganizationMemberResponse {
  organization_id: string;
  user_id: string;
  org_name: string;
  user_name: string;
  user_email: string;
  role: string;
}

// Projects
interface ProjectCreateDTO {
  name: string;
  description?: string;
  source_language: string;
  target_languages: string[];
}

interface ProjectUpdateDTO {
  name?: string;
  description?: string;
  source_language?: string;
  target_languages?: string[];
}

interface ProjectResponse {
  id: string;
  name: string;
  description?: string;
  organization_id: string;
  created_by?: string;
  source_language: string;
  target_languages: string[];
  created_at: string;
  updated_at?: string;
}

interface ProjectStats {
  [key: string]: any;
}

// Project Members
interface ProjectMemberCreateDTO {
  user_id: string;
  role: 'LEAD' | 'TRANSLATOR' | 'REVIEWER';
}

interface ProjectMemberUpdateDTO {
  role: 'LEAD' | 'TRANSLATOR' | 'REVIEWER';
}

interface ProjectMemberResponse {
  id: string;
  project_id: string;
  user_id: string;
  role: 'LEAD' | 'TRANSLATOR' | 'REVIEWER';
  created_at: string;
  updated_at?: string;
}

// Translation Files
interface TranslationFileCreateDTO {
  language_code: string;
  language_name: string;
}

interface TranslationFileUpdateDTO {
  language_code: string;
  language_name: string;
  messages: Record<string, string>;
}

interface TranslationFileResponse {
  id: string;
  project_id: string;
  created_by?: string;
  language_code: string;
  language_name: string;
  current_version: number;
  created_at: string;
  updated_at?: string;
}

interface ExportResponse {
  language_code: string;
  language_name: string;
  version: number;
  messages: Record<string, string>;
  exported_at: string;
}

interface ImportPayload {
  messages: Record<string, string>;
}

// Messages
interface MessageCreateDTO {
  key: string;
  value: string;
  comment?: string;
}

interface MessageUpdateDTO {
  value?: string;
  comment?: string;
}

interface MessageStatusUpdateDTO {
  status: 'APPROVED' | 'REJECTED' | 'PENDING';
  reason?: string;
}

interface MessageResponse {
  id: string;
  file_id: string;
  key: string;
  value?: string;
  comment?: string;
  status: 'APPROVED' | 'REJECTED' | 'PENDING';
  created_by?: string;
  reviewed_by?: string;
  created_at: string;
  updated_at?: string;
}

// Todos
interface TodoCreateDTO {
  description: string;
  due_date?: string;
  priority?: 'Low' | 'Medium' | 'High';
}

interface TodoResponse {
  id: string;
  description: string;
  due_date?: string;
  priority: 'Low' | 'Medium' | 'High';
  is_completed: boolean;
  completed_at?: string;
}

// Error Response
interface ErrorResponse {
  detail?: string;
  message?: string;
  [key: string]: any;
}

// ============================================================================
// ======================== API CLASS ========================================
// ============================================================================

export default class API {
  private _devApiUrl: string = 'http://localhost:4000';
  private _imagePath: string = 'http://localhost:4000/';
  private _tokenKey: string = 'auth_token';

  public get apiUrl(): string {
    return this._devApiUrl;
  }

  public get imagePath(): string {
    return this._imagePath;
  }

  // ============================================================================
  // ======================== HELPER METHODS ==================================
  // ============================================================================

  /**
   * Build headers with optional JWT token
   */
  private buildHeaders(token?: string | null, isMultipart: boolean = false): HeadersInit {
    const headers: HeadersInit = {};

    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Get token from localStorage
   */
  private getStoredToken(): string | null {
    try {
      return localStorage.getItem(this._tokenKey);
    } catch {
      return null;
    }
  }

  /**
   * Handle response and throw error if not ok
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ErrorResponse = await response.json().catch(() => ({}));
      throw new Error(error.detail || error.message || 'Unexpected error');
    }
    
    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // ============================================================================
  // ======================== BASE HTTP METHODS ===============================
  // ============================================================================

  async getData<T>(
    url: string,
    token?: string | null
  ): Promise<T> {
    const finalToken = token || this.getStoredToken();
    const response = await fetch(url, {
      method: 'GET',
      headers: this.buildHeaders(finalToken),
    });
    return this.handleResponse<T>(response);
  }

  async postData<T>(
    url: string,
    data?: any,
    token?: string | null,
    isMultipart: boolean = false
  ): Promise<T> {
    const finalToken = token || this.getStoredToken();
    const headers = this.buildHeaders(finalToken, isMultipart);

    const options: RequestInit = {
      method: 'POST',
      headers,
    };

    if (data) {
      if (isMultipart && data instanceof FormData) {
        options.body = data;
      } else {
        options.body = JSON.stringify(data);
      }
    }

    const response = await fetch(url, options);
    return this.handleResponse<T>(response);
  }

  async putData<T>(
    url: string,
    data: any,
    token?: string | null,
    isMultipart: boolean = false
  ): Promise<T> {
    const finalToken = token || this.getStoredToken();
    const headers = this.buildHeaders(finalToken, isMultipart);

    const options: RequestInit = {
      method: 'PUT',
      headers,
    };

    if (isMultipart && data instanceof FormData) {
      options.body = data;
    } else {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    return this.handleResponse<T>(response);
  }

  async patchData<T>(
    url: string,
    data: any,
    token?: string | null,
    isMultipart: boolean = false
  ): Promise<T> {
    const finalToken = token || this.getStoredToken();
    const headers = this.buildHeaders(finalToken, isMultipart);

    const options: RequestInit = {
      method: 'PATCH',
      headers,
    };

    if (isMultipart && data instanceof FormData) {
      options.body = data;
    } else {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    return this.handleResponse<T>(response);
  }

  async deleteData<T>(
    url: string,
    token?: string | null,
    data?: any
  ): Promise<T> {
    const finalToken = token || this.getStoredToken();
    const headers = this.buildHeaders(finalToken);

    const options: RequestInit = {
      method: 'DELETE',
      headers,
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    return this.handleResponse<T>(response);
  }

  // ============================================================================
  // ======================== AUTH ROUTES =====================================
  // ============================================================================

  /**
   * Register a new user
   */
  async register(data: RegisterDTO): Promise<UserResponse> {
    const result = await this.postData<UserResponse>(
      `${this.apiUrl}/auth/`,
      data
    );
    return result;
  }

  /**
   * Login with email and password
   */
  async login(data: LoginDTO): Promise<Token> {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await fetch(`${this.apiUrl}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    const result = await this.handleResponse<Token>(response);
    
    // Store token in localStorage
    localStorage.setItem(this._tokenKey, result.access_token);
    
    return result;
  }

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem(this._tokenKey);
  }

  // ============================================================================
  // ======================== USERS ROUTES ====================================
  // ============================================================================

  /**
   * Get current user
   */
  async getCurrentUser(token?: string | null): Promise<UserResponse> {
    return this.getData<UserResponse>(
      `${this.apiUrl}/users/me`,
      token
    );
  }

  /**
   * Change password
   */
  async changePassword(
    data: PasswordChangeDTO,
    token?: string | null
  ): Promise<UserResponse> {
    return this.putData<UserResponse>(
      `${this.apiUrl}/users/change-password`,
      data,
      token
    );
  }

  // ============================================================================
  // ======================== ORGANIZATIONS ROUTES ============================
  // ============================================================================

  /**
   * Create a new organization
   */
  async createOrganization(
    data: OrganizationCreateDTO,
    token?: string | null
  ): Promise<OrganizationResponse> {
    return this.postData<OrganizationResponse>(
      `${this.apiUrl}/organizations/`,
      data,
      token
    );
  }

  /**
   * Get organization by ID
   */
  async getOrganization(
    orgId: string,
    token?: string | null
  ): Promise<OrganizationResponse> {
    return this.getData<OrganizationResponse>(
      `${this.apiUrl}/organizations/${orgId}`,
      token
    );
  }

  /**
   * Get organization by name
   */
  async getOrganizationByName(
    name: string,
    token?: string | null
  ): Promise<OrganizationResponse> {
    return this.getData<OrganizationResponse>(
      `${this.apiUrl}/organizations/by-name/${name}`,
      token
    );
  }

  /**
   * Get organizations by user
   */
  async getOrganizationsByUser(
    userId: string,
    token?: string | null
  ): Promise<OrganizationResponse[]> {
    return this.getData<OrganizationResponse[]>(
      `${this.apiUrl}/organizations/user/${userId}`,
      token
    );
  }

  /**
   * Update organization
   */
  async updateOrganization(
    orgId: string,
    data: OrganizationUpdateDTO,
    token?: string | null
  ): Promise<OrganizationResponse> {
    return this.putData<OrganizationResponse>(
      `${this.apiUrl}/organizations/${orgId}`,
      data,
      token
    );
  }

  /**
   * Delete organization
   */
  async deleteOrganization(
    orgId: string,
    token?: string | null
  ): Promise<{ message: string }> {
    return this.deleteData<{ message: string }>(
      `${this.apiUrl}/organizations/${orgId}`,
      token
    );
  }

  // ============================================================================
  // ======================== ORGANIZATION MEMBERS ROUTES ======================
  // ============================================================================

  /**
   * Add member to organization
   */
  async createOrganizationMember(
    data: OrganizationMemberCreateDTO,
    token?: string | null
  ): Promise<OrganizationMemberResponse> {
    return this.postData<OrganizationMemberResponse>(
      `${this.apiUrl}/org_members/`,
      data,
      token
    );
  }

  /**
   * Get organization members with filters
   */
  async getOrganizationMembers(
    params?: {
      user_id?: string;
      organization_id?: string;
      role?: string;
    },
    token?: string | null
  ): Promise<OrganizationMemberResponse[]> {
    const queryParams = new URLSearchParams();
    if (params?.user_id) queryParams.append('user_id', params.user_id);
    if (params?.organization_id) queryParams.append('organization_id', params.organization_id);
    if (params?.role) queryParams.append('role', params.role);

    const url = `${this.apiUrl}/org_members/by-user/?${queryParams.toString()}`;
    return this.getData<OrganizationMemberResponse[]>(url, token);
  }

  /**
   * Update organization member role
   */
  async updateOrganizationMemberRole(
    data: OrganizationMemberUpdateDTO,
    token?: string | null
  ): Promise<OrganizationMemberResponse> {
    return this.putData<OrganizationMemberResponse>(
      `${this.apiUrl}/org_members/`,
      data,
      token
    );
  }

  /**
   * Delete member from organization
   */
  async deleteOrganizationMember(
    userId: string,
    orgId: string,
    token?: string | null
  ): Promise<{ message: string }> {
    return this.deleteData<{ message: string }>(
      `${this.apiUrl}/org_members/${userId}/${orgId}`,
      token
    );
  }

  /**
   * Delete all members from organization
   */
  async deleteOrganizationMembers(
    orgId: string,
    token?: string | null
  ): Promise<{ message: string }> {
    return this.deleteData<{ message: string }>(
      `${this.apiUrl}/org_members/delete/org/${orgId}`,
      token
    );
  }

  /**
   * Delete all memberships for a user
   */
  async deleteUserMemberships(
    userId: string,
    token?: string | null
  ): Promise<{ message: string }> {
    return this.deleteData<{ message: string }>(
      `${this.apiUrl}/org_members/delete/user/${userId}`,
      token
    );
  }

  // ============================================================================
  // ======================== PROJECTS ROUTES ==================================
  // ============================================================================

  /**
   * Create a new project
   */
  async createProject(
    organizationId: string,
    data: ProjectCreateDTO,
    token?: string | null
  ): Promise<ProjectResponse> {
    return this.postData<ProjectResponse>(
      `${this.apiUrl}/projects?organization_id=${organizationId}`,
      data,
      token
    );
  }

  /**
   * Get project by ID
   */
  async getProject(
    projectId: string,
    token?: string | null
  ): Promise<ProjectResponse> {
    return this.getData<ProjectResponse>(
      `${this.apiUrl}/projects/${projectId}`,
      token
    );
  }

  /**
   * List all projects in organization
   */
  async listProjects(
    organizationId: string,
    token?: string | null
  ): Promise<ProjectResponse[]> {
    return this.getData<ProjectResponse[]>(
      `${this.apiUrl}/projects?organization_id=${organizationId}`,
      token
    );
  }

  /**
   * List all projects for current user
   */
  async listUserProjects(token?: string | null): Promise<ProjectResponse[]> {
    return this.getData<ProjectResponse[]>(
      `${this.apiUrl}/projects/user/projects`,
      token
    );
  }

  /**
   * Update project
   */
  async updateProject(
    projectId: string,
    data: ProjectUpdateDTO,
    token?: string | null
  ): Promise<ProjectResponse> {
    return this.patchData<ProjectResponse>(
      `${this.apiUrl}/projects/${projectId}`,
      data,
      token
    );
  }

  /**
   * Delete project
   */
  async deleteProject(
    projectId: string,
    token?: string | null
  ): Promise<void> {
    return this.deleteData<void>(
      `${this.apiUrl}/projects/${projectId}`,
      token
    );
  }

  /**
   * Get project statistics
   */
  async getProjectStats(
    projectId: string,
    token?: string | null
  ): Promise<ProjectStats> {
    return this.getData<ProjectStats>(
      `${this.apiUrl}/projects/${projectId}/stats`,
      token
    );
  }

  // ============================================================================
  // ======================== PROJECT MEMBERS ROUTES ===========================
  // ============================================================================

  /**
   * Add member to project
   */
  async addProjectMember(
    projectId: string,
    data: ProjectMemberCreateDTO,
    token?: string | null
  ): Promise<ProjectMemberResponse> {
    return this.postData<ProjectMemberResponse>(
      `${this.apiUrl}/projects/${projectId}/members`,
      data,
      token
    );
  }

  /**
   * List all members in project
   */
  async listProjectMembers(
    projectId: string,
    token?: string | null
  ): Promise<ProjectMemberResponse[]> {
    return this.getData<ProjectMemberResponse[]>(
      `${this.apiUrl}/projects/${projectId}/members`,
      token
    );
  }

  /**
   * Get project member by ID
   */
  async getProjectMember(
    projectId: string,
    memberId: string,
    token?: string | null
  ): Promise<ProjectMemberResponse> {
    return this.getData<ProjectMemberResponse>(
      `${this.apiUrl}/projects/${projectId}/members/${memberId}`,
      token
    );
  }

  /**
   * Update project member role
   */
  async updateProjectMember(
    projectId: string,
    memberId: string,
    data: ProjectMemberUpdateDTO,
    token?: string | null
  ): Promise<ProjectMemberResponse> {
    return this.patchData<ProjectMemberResponse>(
      `${this.apiUrl}/projects/${projectId}/members/${memberId}`,
      data,
      token
    );
  }

  /**
   * Remove member from project
   */
  async removeProjectMember(
    projectId: string,
    memberId: string,
    token?: string | null
  ): Promise<void> {
    return this.deleteData<void>(
      `${this.apiUrl}/projects/${projectId}/members/${memberId}`,
      token
    );
  }

  // ============================================================================
  // ======================== TRANSLATION FILES ROUTES ==========================
  // ============================================================================

  /**
   * Create translation file
   */
  async createTranslationFile(
    projectId: string,
    data: TranslationFileCreateDTO,
    token?: string | null
  ): Promise<TranslationFileResponse> {
    return this.postData<TranslationFileResponse>(
      `${this.apiUrl}/projects/${projectId}/files`,
      data,
      token
    );
  }

  /**
   * List translation files in project
   */
  async listTranslationFiles(
    projectId: string,
    token?: string | null
  ): Promise<TranslationFileResponse[]> {
    return this.getData<TranslationFileResponse[]>(
      `${this.apiUrl}/projects/${projectId}/files`,
      token
    );
  }

  /**
   * Get translation file by ID
   */
  async getTranslationFile(
    projectId: string,
    fileId: string,
    token?: string | null
  ): Promise<TranslationFileResponse> {
    return this.getData<TranslationFileResponse>(
      `${this.apiUrl}/projects/${projectId}/files/${fileId}`,
      token
    );
  }

  /**
   * Update translation file
   */
  async updateTranslationFile(
    projectId: string,
    fileId: string,
    data: TranslationFileUpdateDTO,
    token?: string | null
  ): Promise<TranslationFileResponse> {
    return this.patchData<TranslationFileResponse>(
      `${this.apiUrl}/projects/${projectId}/files/${fileId}`,
      data,
      token
    );
  }

  /**
   * Delete translation file
   */
  async deleteTranslationFile(
    projectId: string,
    fileId: string,
    token?: string | null
  ): Promise<void> {
    return this.deleteData<void>(
      `${this.apiUrl}/projects/${projectId}/files/${fileId}`,
      token
    );
  }

  /**
   * Export translation file
   */
  async exportTranslationFile(
    projectId: string,
    fileId: string,
    token?: string | null
  ): Promise<ExportResponse> {
    return this.getData<ExportResponse>(
      `${this.apiUrl}/projects/${projectId}/files/${fileId}/export`,
      token
    );
  }

  /**
   * Import translations
   */
  async importTranslations(
    projectId: string,
    fileId: string,
    data: ImportPayload,
    token?: string | null
  ): Promise<TranslationFileResponse> {
    return this.postData<TranslationFileResponse>(
      `${this.apiUrl}/projects/${projectId}/files/${fileId}/import`,
      data,
      token
    );
  }

  // ============================================================================
  // ======================== MESSAGES ROUTES ==================================
  // ============================================================================

  /**
   * Create message
   */
  async createMessage(
    fileId: string,
    projectId: string,
    data: MessageCreateDTO,
    token?: string | null
  ): Promise<MessageResponse> {
    return this.postData<MessageResponse>(
      `${this.apiUrl}/files/${fileId}/messages?project_id=${projectId}`,
      data,
      token
    );
  }

  /**
   * List messages in file
   */
  async listMessages(
    fileId: string,
    status?: string,
    token?: string | null
  ): Promise<MessageResponse[]> {
    const url = status
      ? `${this.apiUrl}/files/${fileId}/messages?status=${status}`
      : `${this.apiUrl}/files/${fileId}/messages`;
    return this.getData<MessageResponse[]>(url, token);
  }

  /**
   * Get message by ID
   */
  async getMessage(
    fileId: string,
    messageId: string,
    token?: string | null
  ): Promise<MessageResponse> {
    return this.getData<MessageResponse>(
      `${this.apiUrl}/files/${fileId}/messages/${messageId}`,
      token
    );
  }

  /**
   * Update message
   */
  async updateMessage(
    fileId: string,
    messageId: string,
    projectId: string,
    data: MessageUpdateDTO,
    token?: string | null
  ): Promise<MessageResponse> {
    return this.patchData<MessageResponse>(
      `${this.apiUrl}/files/${fileId}/messages/${messageId}?project_id=${projectId}`,
      data,
      token
    );
  }

  /**
   * Approve message
   */
  async approveMessage(
    fileId: string,
    messageId: string,
    token?: string | null
  ): Promise<MessageResponse> {
    return this.postData<MessageResponse>(
      `${this.apiUrl}/files/${fileId}/messages/${messageId}/approve`,
      {},
      token
    );
  }

  /**
   * Reject message
   */
  async rejectMessage(
    fileId: string,
    messageId: string,
    data: MessageStatusUpdateDTO,
    token?: string | null
  ): Promise<MessageResponse> {
    return this.postData<MessageResponse>(
      `${this.apiUrl}/files/${fileId}/messages/${messageId}/reject`,
      data,
      token
    );
  }

  // ============================================================================
  // ======================== TODOS ROUTES ======================================
  // ============================================================================

  /**
   * Create todo
   */
  async createTodo(
    data: TodoCreateDTO,
    token?: string | null
  ): Promise<TodoResponse> {
    return this.postData<TodoResponse>(
      `${this.apiUrl}/todos/`,
      data,
      token
    );
  }

  /**
   * Get all todos for current user
   */
  async getTodos(token?: string | null): Promise<TodoResponse[]> {
    return this.getData<TodoResponse[]>(
      `${this.apiUrl}/todos/`,
      token
    );
  }

  /**
   * Get todo by ID
   */
  async getTodo(
    todoId: string,
    token?: string | null
  ): Promise<TodoResponse> {
    return this.getData<TodoResponse>(
      `${this.apiUrl}/todos/${todoId}`,
      token
    );
  }

  /**
   * Update todo
   */
  async updateTodo(
    todoId: string,
    data: TodoCreateDTO,
    token?: string | null
  ): Promise<TodoResponse> {
    return this.putData<TodoResponse>(
      `${this.apiUrl}/todos/${todoId}`,
      data,
      token
    );
  }

  /**
   * Mark todo as completed
   */
  async completeTodo(
    todoId: string,
    token?: string | null
  ): Promise<TodoResponse> {
    return this.putData<TodoResponse>(
      `${this.apiUrl}/todos/${todoId}/complete`,
      {},
      token
    );
  }

  /**
   * Delete todo
   */
  async deleteTodo(
    todoId: string,
    token?: string | null
  ): Promise<void> {
    return this.deleteData<void>(
      `${this.apiUrl}/todos/${todoId}`,
      token
    );
  }
}
