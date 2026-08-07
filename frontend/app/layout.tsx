import type { Metadata } from "next";
import Link from "next/link";
import {
  Activity,
  BellRing,
  FlaskConical,
  Info,
  LayoutDashboard,
  Network,
  Radar,
  ShieldCheck,
} from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "FraudLens", template: "%s · FraudLens" },
  description:
    "Radar inteligente e explicável de anomalias em pagamentos sintéticos.",
};

export const dynamic = "force-dynamic";

const navigation = [
  { href: "/", label: "Visão geral", icon: LayoutDashboard },
  { href: "/alerts", label: "Alertas", icon: BellRing },
  { href: "/network", label: "Rede", icon: Network },
  { href: "/model", label: "Modelo", icon: Activity },
  { href: "/scenarios", label: "Cenários", icon: FlaskConical },
  { href: "/about", label: "Sobre", icon: Info },
];

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" data-scroll-behavior="smooth">
      <body>
        <a className="skip-link" href="#main-content">
          Pular para o conteúdo
        </a>
        <div className="app-shell">
          <aside className="sidebar" aria-label="Navegação principal">
            <Link href="/" className="brand" aria-label="FraudLens — início">
              <span className="brand-mark">
                <Radar size={24} />
              </span>
              <span>
                <strong>FraudLens</strong>
                <small>Anomaly radar</small>
              </span>
            </Link>
            <nav>
              {navigation.map(({ href, label, icon: Icon }) => (
                <Link key={href} href={href} className="nav-link">
                  <Icon size={18} />
                  <span>{label}</span>
                </Link>
              ))}
            </nav>
            <div className="sidebar-note">
              <ShieldCheck size={18} />
              <span>Dados 100% sintéticos</span>
            </div>
          </aside>
          <div className="main-shell">
            <header className="topbar">
              <div>
                <span className="eyebrow">AMBIENTE DEMONSTRATIVO</span>
                <span className="live-status">
                  <i /> Monitoramento ativo
                </span>
              </div>
              <div className="analyst">
                <span>FL</span>
                <div>
                  <strong>Analista demo</strong>
                  <small>Investigação responsável</small>
                </div>
              </div>
            </header>
            <main id="main-content">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
