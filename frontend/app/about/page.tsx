import {
  Blocks,
  BrainCircuit,
  Database,
  GitBranch,
  Scale,
  ShieldCheck,
} from "lucide-react";
import { PageHeader } from "@/components/page-header";

export default function AboutPage() {
  return (
    <div className="page">
      <PageHeader
        eyebrow="SOBRE O PROJETO"
        title="Tecnologia para investigar, não condenar"
        description="FraudLens conecta engenharia de dados, machine learning, produto e segurança em uma demonstração reproduzível."
      />
      <section className="about-hero panel">
        <div>
          <span className="eyebrow">PROPÓSITO</span>
          <h2>
            Transformar sinais técnicos em uma história de risco compreensível.
          </h2>
          <p>
            A plataforma gera pagamentos totalmente fictícios, constrói o
            histórico de cada conta, identifica desvios e oferece evidências
            para uma revisão humana. Nenhum score é apresentado como prova ou
            probabilidade real de fraude.
          </p>
        </div>
        <div className="architecture-flow">
          <span>
            <Database />
            Dados sintéticos
          </span>
          <i>→</i>
          <span>
            <GitBranch />
            Features causais
          </span>
          <i>→</i>
          <span>
            <BrainCircuit />
            Regras + modelo
          </span>
          <i>→</i>
          <span>
            <Scale />
            Investigação
          </span>
        </div>
      </section>
      <section className="principles-grid">
        <article>
          <ShieldCheck />
          <h2>Seguro por padrão</h2>
          <p>
            Sem PII, segredos ou integrações bancárias. Entradas validadas, CORS
            restrito e administração desabilitada.
          </p>
        </article>
        <article>
          <Blocks />
          <h2>Arquitetura pragmática</h2>
          <p>
            FastAPI, SQLAlchemy e SQLite no backend; Next.js e React no
            frontend; PostgreSQL opcional via Docker.
          </p>
        </article>
        <article>
          <BrainCircuit />
          <h2>Explicável e reproduzível</h2>
          <p>
            Isolation Forest com seed fixa, regras YAML e decomposição
            transparente do score combinado.
          </p>
        </article>
      </section>
      <section className="responsible-use">
        <strong>Uso responsável</strong>
        <p>
          Este é um projeto educacional de portfólio. Todos os dados e cenários
          são sintéticos. Não deve ser usado para decisões financeiras,
          bloqueios, acusações ou análise de pessoas reais.
        </p>
      </section>
    </div>
  );
}
