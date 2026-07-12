/** Shared selectors and role patterns for KrishiFarms CRM. */
export const SELECTORS = {
  auth: {
    accessTokenKey: "krishi-access-token",
    refreshTokenKey: "krishi-refresh-token",
  },
  shell: {
    fatalError:
      /Application error|Internal Server Error|This page could not be found|Unhandled Runtime Error/i,
    emptyState: /coming soon|no .+ found|nothing here/i,
  },
  roles: {
    loginButton: /^(Next|Sign in)$/i,
    addButton: /^Add$/i,
  },
} as const;

/** MUI dialog field locator strategy (handles floating labels / required asterisks). */
export function dialogFieldRoles(): Array<
  "textbox" | "combobox" | "spinbutton" | "checkbox"
> {
  return ["textbox", "combobox", "spinbutton", "checkbox"];
}
