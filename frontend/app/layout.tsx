import type { Metadata } from "next";
import Link from "next/link";
import { Database, Radar, ShieldCheck } from "lucide-react";
import { ActiveNavigation } from "@/components/active-navigation";
import { getMeta } from "@/lib/api";
import { dateTime, number } from "@/lib/format";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "FraudLens", template: "%s · FraudLens" },
  description: "Investigação explicável de anomalias em pagamentos sintéticos.",
  openGraph: {
    title: "FraudLens · Payment anomaly investigation",
    description:
      "Dados sintéticos, features causais, regras, ML não supervisionado e revisão humana.",
    type: "website",
  },
};

export const dynamic = "force-dynamic";

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const meta = await getMeta().catch(() => null);
  return (
    <html lang="pt-BR" data-scroll-behavior="smooth">
      <body>
        <a className="skip-link" href="#main-content">
          Pular para o conteúdo
        </a>
        <div className="app-shell">
          <aside className="sidebar">
            <Link href="/" className="brand" aria-label="FraudLens — início">
              <span className="brand-mark">
                <Radar size={19} />
              </span>
              <span>
                <strong>FraudLens</strong>
                <small>Risk operations</small>
              </span>
            </Link>
            <ActiveNavigation />
            <div className="sidebar-note">
              <ShieldCheck size={16} />
              <span>Ambiente sintético</span>
            </div>
          </aside>
          <div className="main-shell">
            <header className="topbar" aria-label="Metadados operacionais">
              <div className="topbar-meta">
                <span>
                  <small>DATASET</small>
                  <strong>
                    <Database size={13} /> Synthetic · seed{" "}
                    {meta?.dataset?.seed ?? "—"}
                  </strong>
                </span>
                <span>
                  <small>MODEL</small>
                  <strong>
                    {meta?.model
                      ? `${meta.model.model_name} · v${meta.model.model_version}`
                      : "Indisponível"}
                  </strong>
                </span>
                <span>
                  <small>LAST SCORING</small>
                  <strong>
                    {meta?.last_scoring_at
                      ? dateTime(meta.last_scoring_at)
                      : "Não executado"}
                  </strong>
                </span>
                <span>
                  <small>ROWS</small>
                  <strong>
                    {meta?.dataset
                      ? number(meta.dataset.transaction_count)
                      : "—"}
                  </strong>
                </span>
              </div>
            </header>
            <main id="main-content" className="app-main">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
