import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertTable } from "../components/alert-table";
import { isRouteActive } from "../components/active-navigation";
import { MetricCard, SeverityBadge } from "../components/ui";

describe("core dashboard components", () => {
  it("derives active navigation from the current route", () => {
    expect(isRouteActive("/", "/")).toBe(true);
    expect(isRouteActive("/alerts/ALT-00000001", "/alerts")).toBe(true);
    expect(isRouteActive("/model", "/")).toBe(false);
    expect(isRouteActive("/accounts", "/alerts")).toBe(false);
  });
  it("renders a contextual metric", () => {
    render(
      <MetricCard
        label="Alertas"
        value="42"
        context="janela atual"
        icon={<span>!</span>}
      />,
    );
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("janela atual")).toBeInTheDocument();
  });

  it("communicates severity with text", () => {
    render(<SeverityBadge severity="crítica" />);
    expect(screen.getByText("crítica")).toBeInTheDocument();
  });

  it("renders a meaningful empty alerts state", () => {
    render(<AlertTable alerts={[]} />);
    expect(screen.getByText("Nenhum alerta encontrado")).toBeInTheDocument();
  });
});
