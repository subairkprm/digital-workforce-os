// @vitest-environment jsdom

import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";

import { InvitationPanel } from "./InvitationPanel";

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

it("submits the selected tenant role and displays the one-time token", async () => {
  const api = vi.fn()
    .mockResolvedValueOnce([{ id: "role-1", name: "Employee", permissions: ["employee.read"] }])
    .mockResolvedValueOnce({ token: "one-time-token" });
  const reload = vi.fn().mockResolvedValue(undefined);
  render(<InvitationPanel api={api} reload={reload} />);
  await waitFor(() => expect(screen.getByRole("option", { name: "Employee" })).toBeInTheDocument());
  fireEvent.change(screen.getByLabelText("Invitation email"), { target: { value: "new@example.com" } });
  fireEvent.change(screen.getByLabelText("Invitation role"), { target: { value: "role-1" } });
  fireEvent.click(screen.getByRole("button", { name: "Create invitation" }));
  await waitFor(() => expect(api).toHaveBeenCalledTimes(2));
  expect(api.mock.calls[1][0]).toBe("/invitations");
  expect(JSON.parse(api.mock.calls[1][1].body)).toEqual({ email: "new@example.com", role_ids: ["role-1"] });
  expect(await screen.findByText("one-time-token")).toBeInTheDocument();
  await waitFor(() => expect(reload).toHaveBeenCalled());
});
