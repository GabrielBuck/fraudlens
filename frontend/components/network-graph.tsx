"use client";

import { useSyncExternalStore } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const positions = (nodes: Node[]) =>
  nodes.map((node, index) => ({
    ...node,
    position:
      index === 0
        ? { x: 400, y: 240 }
        : {
            x: 400 + Math.cos(index * 1.7) * (120 + index * 11),
            y: 240 + Math.sin(index * 1.7) * (120 + index * 9),
          },
  }));
const subscribe = () => () => undefined;

export function NetworkGraph({
  nodes,
  edges,
}: {
  nodes: Array<{ id: string; label: string; type: string; risk: number }>;
  edges: Edge[];
}) {
  const mounted = useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );

  if (!mounted) {
    return (
      <div
        className="network-canvas"
        aria-label="Carregando grafo de relações"
        aria-busy="true"
      />
    );
  }

  const flowNodes: Node[] = positions(
    nodes.map((node) => ({
      id: node.id,
      data: { label: node.label },
      position: { x: 0, y: 0 },
      className: `network-node node-${node.type} ${node.risk >= 60 ? "node-risk" : ""}`,
    })),
  );
  return (
    <div
      className="network-canvas"
      aria-label="Grafo interativo de relações da conta"
    >
      <ReactFlow
        nodes={flowNodes}
        edges={edges}
        fitView
        minZoom={0.35}
        maxZoom={2}
      >
        <Background color="#343a40" gap={22} />
        <MiniMap
          nodeColor={(node) =>
            node.className?.includes("risk") ? "#df5b57" : "#77818b"
          }
          maskColor="rgba(18,20,22,.78)"
        />
        <Controls />
      </ReactFlow>
    </div>
  );
}
