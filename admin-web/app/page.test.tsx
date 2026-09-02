// @vitest-environment jsdom

import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import AdminShell from "./page";

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe("AdminShell", () => {
  it("reports failed authentication without exposing the workspace", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 401 }));
    render(<AdminShell />);
    fireEvent.change(screen.getByLabelText("Tenant ID"), { target: { value: "tenant-a" } });
    fireEvent.change(screen.getByLabelText("Work email"), { target: { value: "user@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "wrong-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Sign-in failed");
    expect(screen.queryByRole("navigation", { name: "Administration" })).not.toBeInTheDocument();
  });

  it("shows only server-authorized navigation after login", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ access_token: "access" }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ email: "viewer@example.com", tenant_id: "tenant-a", permissions: ["employee.read"] }) });
    vi.stubGlobal("fetch", fetchMock);
    render(<AdminShell />);
    fireEvent.change(screen.getByLabelText("Tenant ID"), { target: { value: "tenant-a" } });
    fireEvent.change(screen.getByLabelText("Work email"), { target: { value: "viewer@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "correct-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    await waitFor(() => expect(screen.getByRole("navigation", { name: "Administration" })).toBeInTheDocument());
    expect(screen.getByRole("button", { name: "Employees" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Departments" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Roles" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Audit" })).not.toBeInTheDocument();
  });
});
