"use client";

import { useState } from "react";
import { browserApi } from "@/lib/api";

export function ReviewActions({
  alertId,
  initialStatus,
}: {
  alertId: string;
  initialStatus: string;
}) {
  const [status, setStatus] = useState(initialStatus);
  const [comment, setComment] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(
    classification: "fraude confirmada" | "falso positivo" | "inconclusivo",
  ) {
    setBusy(true);
    setMessage("");
    try {
      await browserApi(`/api/v1/alerts/${alertId}/feedback`, {
        method: "POST",
        body: JSON.stringify({
          classification,
          comment: comment || "Revisão registrada sem comentário adicional.",
        }),
      });
      setStatus(
        classification === "inconclusivo" ? "em análise" : classification,
      );
      setComment("");
      setMessage("Decisão registrada com sucesso.");
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Falha ao registrar.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel review-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">DECISÃO HUMANA</span>
          <h2>Registrar revisão</h2>
        </div>
        <span className="status-badge">{status}</span>
      </div>
      <label htmlFor="review-comment">Comentário da análise</label>
      <textarea
        id="review-comment"
        value={comment}
        onChange={(event) => setComment(event.target.value)}
        maxLength={1000}
        placeholder="Registre evidências e contexto da decisão…"
      />
      <div className="review-actions">
        <button
          className="button danger"
          disabled={busy}
          onClick={() => submit("fraude confirmada")}
        >
          Confirmar cenário sintético
        </button>
        <button
          className="button secondary"
          disabled={busy}
          onClick={() => submit("falso positivo")}
        >
          Marcar falso positivo
        </button>
        <button
          className="text-button"
          disabled={busy}
          onClick={() => submit("inconclusivo")}
        >
          Manter em análise
        </button>
      </div>
      {message && (
        <p className="action-message" role="status">
          {message}
        </p>
      )}
    </section>
  );
}
