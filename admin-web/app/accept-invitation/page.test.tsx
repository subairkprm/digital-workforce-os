// @vitest-environment jsdom

import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";

import AcceptInvitationPage from "./page";

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

it("rejects mismatched passwords before calling the API", async () => {
  const fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  render(<AcceptInvitationPage />);
  fireEvent.change(screen.getByLabelText("Invitation token"), { target: { value: "a".repeat(48) } });
  fireEvent.change(screen.getByLabelText("Password"), { target: { value: "long-password-one" } });
  fireEvent.change(screen.getByLabelText("Confirm password"), { target: { value: "long-password-two" } });
  fireEvent.click(screen.getByRole("button", { name: "Accept invitation" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Passwords do not match");
  expect(fetchMock).not.toHaveBeenCalled();
});

it("shows completion after the API accepts the invitation", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 204 }));
  render(<AcceptInvitationPage />);
  fireEvent.change(screen.getByLabelText("Invitation token"), { target: { value: "b".repeat(48) } });
  fireEvent.change(screen.getByLabelText("Password"), { target: { value: "long-password-value" } });
  fireEvent.change(screen.getByLabelText("Confirm password"), { target: { value: "long-password-value" } });
  fireEvent.click(screen.getByRole("button", { name: "Accept invitation" }));
  expect(await screen.findByRole("heading", { name: "Invitation accepted" })).toBeInTheDocument();
});
