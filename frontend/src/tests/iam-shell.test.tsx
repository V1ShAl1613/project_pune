import React from "react";
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { AuthStateShell } from "@/identity/shared/auth-state-shell";

describe("AuthStateShell", () => {
  it("renders the auth state title and actions", () => {
    render(<AuthStateShell title="Access denied" description="You do not have access." actions={[{ label: "Go to login", href: "/login" }]} />);

    expect(screen.getByText("Access denied")).toBeInTheDocument();
    expect(screen.getByText("Go to login")).toBeInTheDocument();
  });
});