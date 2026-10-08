import { useEffect, useRef } from "react";
import gsap from "gsap";
import { Cpu, Database, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import CountUp from "@/components/CountUp";

function BrandMark() {
  return (
    <svg viewBox="0 0 48 48" className="size-10" aria-hidden="true">
      <path d="M24 3 42 13.5v21L24 45 6 34.5v-21z" fill="none" stroke="var(--color-fern-400)" strokeWidth="1.6" />
      <path
        d="M13 29c4-9 8-9 11-4s7 5 11-6"
        fill="none"
        stroke="var(--color-spark-200)"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      <circle cx="35" cy="19" r="2.6" fill="var(--color-spark-200)" />
    </svg>
  );
}

export default function Header({ health }) {
  const ref = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from("[data-head]", { opacity: 0, y: -14, duration: 0.7, stagger: 0.08, ease: "power3.out" });
    }, ref);
    return () => ctx.revert();
  }, []);

  const online = health && health.status === "ok";

  return (
    <header ref={ref} className="border-b border-moss-700/80 bg-moss-950/60 backdrop-blur">
      <div className="mx-auto flex max-w-[1500px] flex-wrap items-center justify-between gap-4 px-5 py-4 lg:px-8">
        <div data-head className="flex items-center gap-3">
          <BrandMark />
          <div>
            <h1 className="font-display text-2xl font-medium leading-none tracking-tight">
              Flux<span className="text-spark-200">-</span>CRAG
            </h1>
            <p className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.24em] text-bone-500">
              Corrective retrieval control room
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge data-head variant={online ? "success" : health ? "warn" : "muted"}>
            <span className={`size-1.5 rounded-full bg-current ${online ? "animate-pulse" : ""}`} />
            {health ? health.status : "connecting"}
          </Badge>
          <Badge data-head variant="default">
            <Cpu className="size-3" />
            {health?.llm_model ?? "llm"}
          </Badge>
          <Badge data-head variant="default">
            <Layers className="size-3" />
            {health?.embedding_model ?? "embeddings"}
          </Badge>
          <Badge data-head variant="muted">
            <Database className="size-3" />
            <CountUp value={health?.chunks_indexed ?? null} /> chunks
          </Badge>
        </div>
      </div>
    </header>
  );
}
