import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ExternalLink, FileText, Globe } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardLabel, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const STATUS_VARIANT = { idle: "muted", running: "success", done: "default", error: "danger" };

function renderWithCitations(text, setActive) {
  return text.split(/(\[\d+\])/g).map((part, index) => {
    const match = part.match(/^\[(\d+)\]$/);
    if (!match) return <span key={index}>{part}</span>;
    const id = Number(match[1]);
    return (
      <button
        key={index}
        type="button"
        onMouseEnter={() => setActive(id)}
        onMouseLeave={() => setActive(null)}
        onFocus={() => setActive(id)}
        onBlur={() => setActive(null)}
        className="mx-0.5 inline-flex h-[1.25em] min-w-[1.5em] -translate-y-[0.15em] items-center justify-center rounded-sm border border-fern-400/60 bg-fern-400/15 px-1 font-mono text-[0.62em] text-spark-200 transition-colors hover:bg-spark-200 hover:text-moss-950"
      >
        {id}
      </button>
    );
  });
}

export default function AnswerPanel({ question, answer, status, sources, error }) {
  const [active, setActive] = useState(null);
  const listRef = useRef(null);
  const running = status === "running";

  useEffect(() => {
    const cards = listRef.current?.querySelectorAll("[data-source]");
    if (!cards || cards.length === 0) return;
    const tween = gsap.fromTo(
      cards,
      { opacity: 0, y: 16 },
      { opacity: 1, y: 0, duration: 0.55, stagger: 0.09, ease: "power3.out" }
    );
    return () => tween.kill();
  }, [sources.length]);

  return (
    <Card data-reveal>
      <CardHeader>
        <div className="flex items-center gap-3">
          <CardLabel>Generation</CardLabel>
          <CardTitle>Grounded answer</CardTitle>
        </div>
        <Badge variant={STATUS_VARIANT[status]}>{status}</Badge>
      </CardHeader>

      <CardContent className="space-y-5">
        {question && (
          <p className="font-mono text-xs text-bone-500">
            <span className="text-spark-200">{">"}</span> {question}
          </p>
        )}

        {status === "idle" && (
          <p className="text-sm leading-relaxed text-bone-500">
            Ask a question above. The answer streams here token by token, with citations tied to verified sources.
          </p>
        )}

        {running && !answer && (
          <div className="space-y-2.5">
            <div className="shimmer h-3.5 w-11/12 rounded-sm" />
            <div className="shimmer h-3.5 w-9/12 rounded-sm" />
            <div className="shimmer h-3.5 w-7/12 rounded-sm" />
          </div>
        )}

        {answer && (
          <p
            className={cn(
              "whitespace-pre-wrap font-display text-[1.08rem] leading-[1.75] text-bone-100",
              running && "caret"
            )}
          >
            {renderWithCitations(answer, setActive)}
          </p>
        )}

        {error && (
          <p className="rounded-md border border-rust-400/40 bg-rust-400/10 p-3 font-mono text-xs leading-relaxed text-rust-400">
            {error}
          </p>
        )}

        {sources.length > 0 && (
          <div>
            <p className="mb-3 font-mono text-[10px] uppercase tracking-[0.22em] text-fern-300">Verified sources</p>
            <ul ref={listRef} className="grid gap-2.5 sm:grid-cols-2">
              {sources.map((source) => (
                <li
                  key={source.id}
                  data-source
                  className={cn(
                    "rounded-md border p-3 transition-colors duration-300",
                    active === source.id ? "border-spark-200 bg-moss-800" : "border-moss-700 bg-moss-850/70"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[11px] text-spark-200">[{source.id}]</span>
                    <Badge variant={source.origin === "web" ? "warn" : "default"}>
                      {source.origin === "web" ? <Globe className="size-3" /> : <FileText className="size-3" />}
                      {source.origin}
                    </Badge>
                  </div>
                  <p className="mt-2 truncate text-sm text-bone-100" title={source.title}>
                    {source.title}
                  </p>
                  {source.origin === "web" ? (
                    <a
                      href={source.location}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-1 flex items-center gap-1 font-mono text-[10px] text-bone-500 transition-colors hover:text-spark-200"
                    >
                      <ExternalLink className="size-3 shrink-0" />
                      <span className="truncate">{source.location}</span>
                    </a>
                  ) : (
                    <p className="mt-1 truncate font-mono text-[10px] text-bone-500">{source.location}</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
