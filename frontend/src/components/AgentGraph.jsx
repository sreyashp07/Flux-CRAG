import { useEffect, useMemo, useRef } from "react";
import gsap from "gsap";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardLabel, CardTitle } from "@/components/ui/card";
import { NODE_H, NODE_W, VIEW, edgeGeometry, positionOf } from "@/lib/graphLayout";
import "@/styles/graph.css";

const CAPTION = {
  idle: "STANDBY",
  active: "RUNNING",
  done: "COMPLETE",
  warn: "RECOVERED",
  skipped: "BYPASSED",
};

export default function AgentGraph({ topology, nodes, order, status }) {
  const rootRef = useRef(null);
  const ctxRef = useRef(null);
  const animatedEdges = useRef(new Set());
  const settledNodes = useRef(new Set());

  const layout = useMemo(() => {
    if (!topology) return null;
    const positions = Object.fromEntries(topology.nodes.map((n, i) => [n.id, positionOf(n.id, i)]));
    const edges = topology.edges.map((edge) => ({
      ...edge,
      key: `${edge.source}->${edge.target}`,
      ...edgeGeometry(positions[edge.source], positions[edge.target]),
    }));
    return { positions, edges };
  }, [topology]);

  const visited = new Set(order);
  const takenKeys = new Set(order.slice(1).map((id, i) => `${order[i]}->${id}`));
  const stateOf = (id) => nodes[id] ?? (status === "done" && !visited.has(id) ? "skipped" : "idle");

  // One long-lived GSAP context: animations are added to it and reverted only on unmount.
  useEffect(() => {
    ctxRef.current = gsap.context(() => {}, rootRef);
    return () => {
      ctxRef.current?.revert();
      ctxRef.current = null;
    };
  }, []);

  // Entrance
  useEffect(() => {
    if (!layout || !ctxRef.current) return;
    ctxRef.current.add(() => {
      gsap.from(".gnode", {
        opacity: 0,
        y: 22,
        scale: 0.9,
        duration: 0.8,
        stagger: 0.1,
        ease: "power3.out",
        transformOrigin: "50% 50%",
      });
      gsap.from(".gedge-base", { opacity: 0, duration: 1, delay: 0.35, stagger: 0.08 });
      gsap.from(".glabel", { opacity: 0, duration: 0.6, delay: 0.9 });
    });
  }, [layout]);

  // Pulse ring on the active node
  const activeKey = Object.entries(nodes)
    .filter(([, s]) => s === "active")
    .map(([id]) => id)
    .join(",");
  useEffect(() => {
    if (!ctxRef.current || !rootRef.current) return;
    const root = rootRef.current;
    ctxRef.current.add(() => {
      root.querySelectorAll("[data-ring]").forEach((ring) => {
        gsap.killTweensOf(ring);
        if (activeKey.split(",").includes(ring.dataset.ring)) {
          gsap.fromTo(
            ring,
            { opacity: 0.9, scale: 1 },
            { opacity: 0, scale: 1.18, duration: 1.2, repeat: -1, ease: "power1.out", transformOrigin: "50% 50%" }
          );
        } else {
          gsap.set(ring, { opacity: 0, scale: 1 });
        }
      });
    });
  }, [activeKey, layout]);

  // Settle pop when a node completes
  const doneKey = Object.entries(nodes)
    .filter(([, s]) => s === "done" || s === "warn")
    .map(([id]) => id)
    .join(",");
  useEffect(() => {
    if (!ctxRef.current || !rootRef.current) return;
    if (doneKey === "") {
      settledNodes.current.clear();
      return;
    }
    const root = rootRef.current;
    doneKey.split(",").forEach((id) => {
      if (settledNodes.current.has(id)) return;
      settledNodes.current.add(id);
      ctxRef.current.add(() => {
        const body = root.querySelector(`[data-node="${id}"]`);
        if (body) {
          gsap.fromTo(
            body,
            { scale: 1.07 },
            { scale: 1, duration: 0.6, ease: "back.out(2.4)", transformOrigin: "50% 50%" }
          );
        }
      });
    });
  }, [doneKey]);

  // Edge traversal: draw the edge and send a packet along it
  const orderKey = order.join(">");
  useEffect(() => {
    if (!layout || !ctxRef.current || !rootRef.current) return;
    const root = rootRef.current;

    if (order.length === 0) {
      animatedEdges.current.clear();
      root.querySelectorAll(".gflow, .gpacket").forEach((el) => {
        gsap.killTweensOf(el);
        gsap.set(el, { opacity: 0 });
      });
      return;
    }

    order.slice(1).forEach((id, i) => {
      const key = `${order[i]}->${id}`;
      if (animatedEdges.current.has(key)) return;
      const flow = root.querySelector(`[data-flow="${key}"]`);
      const packet = root.querySelector(`[data-packet="${key}"]`);
      if (!flow || !packet) return;
      animatedEdges.current.add(key);

      ctxRef.current.add(() => {
        const length = flow.getTotalLength();
        const progress = { t: 0 };
        gsap.set(flow, { strokeDasharray: length, strokeDashoffset: length, opacity: 1 });
        gsap.set(packet, { opacity: 1 });
        gsap.to(flow, { strokeDashoffset: 0, duration: 0.9, ease: "power2.inOut" });
        gsap.to(progress, {
          t: 1,
          duration: 0.9,
          ease: "power2.inOut",
          onUpdate: () => {
            const point = flow.getPointAtLength(progress.t * length);
            packet.setAttribute("cx", point.x);
            packet.setAttribute("cy", point.y);
          },
          onComplete: () => gsap.to(packet, { opacity: 0, duration: 0.3 }),
        });
      });
    });
  }, [orderKey, layout]);

  return (
    <Card data-reveal>
      <CardHeader>
        <div className="flex items-center gap-3">
          <CardLabel>Agent state machine</CardLabel>
          <CardTitle>Live routing</CardTitle>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden font-mono text-[10px] uppercase tracking-[0.16em] text-bone-500 md:inline">
            solid fixed route / dashed conditional route
          </span>
          <Badge variant={status === "running" ? "success" : status === "error" ? "danger" : "muted"}>{status}</Badge>
        </div>
      </CardHeader>
      {status === "running" && <div className="scanbar" />}
      <CardContent className="pt-3">
        <div ref={rootRef}>
          {!layout ? (
            <div className="grid h-[300px] place-items-center font-mono text-xs uppercase tracking-[0.2em] text-bone-500">
              Loading topology
            </div>
          ) : (
            <svg viewBox={`0 0 ${VIEW.width} ${VIEW.height}`} className="h-auto w-full" role="img" aria-label="Agent state machine">
              <defs>
                <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
                  <circle cx="1" cy="1" r="1" fill="rgb(236 234 210 / 0.07)" />
                </pattern>
                <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
                  <feGaussianBlur stdDeviation="3.5" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                <marker id="arrow-idle" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
                  <path d="M0 0 L10 5 L0 10 z" fill="#3a4825" />
                </marker>
                <marker id="arrow-taken" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
                  <path d="M0 0 L10 5 L0 10 z" fill="#a6bb5a" />
                </marker>
              </defs>

              <rect width={VIEW.width} height={VIEW.height} fill="url(#dots)" />

              {layout.edges.map((edge) => {
                const taken = takenKeys.has(edge.key);
                const labelWidth = edge.label ? edge.label.length * 7.2 + 20 : 0;
                return (
                  <g key={edge.key} className="gedgewrap" data-dim={status === "done" && !taken ? "true" : "false"}>
                    <path
                      className="gedge-base"
                      d={edge.d}
                      fill="none"
                      data-taken={taken}
                      strokeDasharray={edge.conditional ? "5 6" : undefined}
                      markerEnd={`url(#arrow-${taken ? "taken" : "idle"})`}
                    />
                    <path className="gflow" data-flow={edge.key} d={edge.d} fill="none" />
                    <circle className="gpacket" data-packet={edge.key} r="5" cx={edge.mid.x} cy={edge.mid.y} />
                    {edge.label && (
                      <g className="glabel" data-taken={taken} transform={`translate(${edge.mid.x} ${edge.mid.y})`}>
                        <rect x={-labelWidth / 2} y="-9" width={labelWidth} height="18" rx="3" />
                        <text>{edge.label}</text>
                      </g>
                    )}
                  </g>
                );
              })}

              {topology.nodes.map((node, index) => {
                const { x, y } = layout.positions[node.id];
                const state = stateOf(node.id);
                return (
                  <g key={node.id} className="gwrap" data-state={state} transform={`translate(${x} ${y})`}>
                    <g className="gnode" data-node={node.id}>
                      <title>{node.description}</title>
                      <rect
                        className="ring"
                        data-ring={node.id}
                        x={-NODE_W / 2 - 4}
                        y={-NODE_H / 2 - 4}
                        width={NODE_W + 8}
                        height={NODE_H + 8}
                        rx="14"
                      />
                      <rect className="body" x={-NODE_W / 2} y={-NODE_H / 2} width={NODE_W} height={NODE_H} rx="10" />
                      <text className="index" x={-NODE_W / 2 + 12} y={-NODE_H / 2 + 17}>
                        {String(index + 1).padStart(2, "0")}
                      </text>
                      <circle className="dot" cx={NODE_W / 2 - 14} cy={-NODE_H / 2 + 14} r="3.5" />
                      <text className="label" x={-NODE_W / 2 + 12} y="9">
                        {node.label}
                      </text>
                      <text className="caption" x={-NODE_W / 2 + 12} y={NODE_H / 2 - 10}>
                        {CAPTION[state]}
                      </text>
                    </g>
                  </g>
                );
              })}
            </svg>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
