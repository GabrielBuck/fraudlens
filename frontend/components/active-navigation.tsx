"use client";

import {
  Activity,
  BellRing,
  Building2,
  FlaskConical,
  Info,
  LayoutDashboard,
  Network,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/", label: "Visão geral", icon: LayoutDashboard },
  { href: "/alerts", label: "Alertas", icon: BellRing },
  { href: "/accounts", label: "Contas", icon: Building2 },
  { href: "/network", label: "Rede", icon: Network },
  { href: "/model", label: "Modelo e dados", icon: Activity },
  { href: "/scenarios", label: "Validação", icon: FlaskConical },
  { href: "/about", label: "Sobre", icon: Info },
];

export function isRouteActive(pathname: string, href: string) {
  return href === "/"
    ? pathname === "/"
    : pathname === href || pathname.startsWith(`${href}/`);
}

export function ActiveNavigation() {
  const pathname = usePathname();
  return (
    <nav aria-label="Navegação principal">
      {navigation.map(({ href, label, icon: Icon }) => {
        const active = isRouteActive(pathname, href);
        return (
          <Link
            key={href}
            href={href}
            className="nav-link"
            aria-current={active ? "page" : undefined}
          >
            <Icon size={17} aria-hidden="true" />
            <span>{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
