const API_BASE_URL = process.env.API_URL || 'http://localhost:3001/api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials extends LoginCredentials {
  username: string;
}

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error('API request failed');
    }

    return response.json();
  }

  async login(credentials: LoginCredentials) {
    return this.request<{ token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async signup(credentials: SignupCredentials) {
    return this.request<{ token: string; user: User }>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async updateProfile(userId: string, data: Partial<User>) {
    return this.request<User>(`/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async updatePreferences(userId: string, preferences: User['preferences']) {
    return this.request<User>(`/users/${userId}/preferences`, {
      method: 'PATCH',
      body: JSON.stringify(preferences),
    });
  }
}

export const apiClient = new ApiClient(); 