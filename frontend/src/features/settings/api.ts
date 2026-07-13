import { fetchApi } from "@/lib/api/client";

export interface UserRole {
  id: string;
  code: string;
  name: string;
}

export interface User {
  id: string;
  org_id: string;
  email: string | null;
  phone: string | null;
  full_name: string;
  village_id: string | null;
  preferred_locale: string;
  is_active: boolean;
  role: UserRole;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserListData {
  items: User[];
  total: number;
  page: number;
  page_size: number;
}

export function fetchUsers(page = 1, pageSize = 50): Promise<UserListData> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<UserListData>(`/users?${params}`, { method: "GET", clientHeaders: false });
}

export function fetchRoles(): Promise<UserRole[]> {
  return fetchApi<UserRole[]>("/roles", { method: "GET", clientHeaders: false });
}

export function createUser(payload: {
  full_name: string;
  role_id: string;
  email?: string | null;
  password?: string | null;
  phone?: string | null;
  village_id?: string | null;
  preferred_locale?: string;
}): Promise<User> {
  return fetchApi<User>("/users", { method: "POST", body: payload, clientHeaders: true });
}

export function updateUser(
  id: string,
  payload: Partial<{
    full_name: string;
    phone: string | null;
    village_id: string | null;
    role_id: string;
    preferred_locale: string;
    is_active: boolean;
    password: string;
  }>,
): Promise<User> {
  return fetchApi<User>(`/users/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}

export function deleteUser(id: string): Promise<{ message: string }> {
  return fetchApi<{ message: string }>(`/users/${id}`, { method: "DELETE", clientHeaders: true });
}
