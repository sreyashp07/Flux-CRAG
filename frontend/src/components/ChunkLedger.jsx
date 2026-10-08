import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import EmptyState from "@/components/EmptyState";

// Squared-L2 distance: smaller means closer. Map to a 0..1 bar for display.
const proximity = (distance) => Math.max(0.04, Math.min(1, 1 - distance / 1.5));

function Verdict({ grade }) {
  if (!grade) {
    return (
      <Badge variant="muted">
        <span className="size-1.5 animate-pulse rounded-full bg-current" />
        grading
      </Badge>
    );
  }
  return grade.relevant ? <Badge variant="success">relevant</Badge> : <Badge variant="danger">rejected</Badge>;
}

export default function ChunkLedger({ retrieved, grades, webResults }) {
  const listRef = useRef(null);

  useEffect(() => {
    const root = listRef.current;
    if (!root) return;
    const rows = root.querySelectorAll("[data-row]");
    const bars = root.querySelectorAll("[data-bar]");
    if (rows.length === 0) return;
    const rowTween = gsap.fromTo(
      rows,
      { opacity: 0, y: 14 },
      { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: "power3.out" }
    );
    const barTween = gsap.fromTo(
      bars,
      { scaleX: 0 },
      { scaleX: 1, duration: 0.9, stagger: 0.08, delay: 0.2, ease: "power2.out", transformOrigin: "left center" }
    );
    return () => {
      rowTween.kill();
      barTween.kill();
    };
  }, [retrieved]);

  const verified = grades.filter((grade) => grade.relevant).length;

  return (
    <ScrollArea className="h-[560px]">
      <div ref={listRef} className="space-y-5 p-5">
        {retrieved.length === 0 ? (
          <EmptyState text="Retrieved chunks and the grader's verdicts appear here" />
        ) : (
          <>
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-fern-300">Retrieval ledger</span>
              <span className="font-mono text-[11px] text-bone-300">
                {grades.length > 0 ? `${verified} of ${retrieved.length} verified` : "grading in progress"}
              </span>
            </div>
            <ul className="space-y-3">
              {retrieved.map((chunk, index) => (
                <li key={`${chunk.source}-${index}`} data-row className="rounded-md border border-moss-700 bg-moss-850/70 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate font-mono text-[11px] text-bone-300">
                      <span className="mr-2 text-bone-500">{String(index + 1).padStart(2, "0")}</span>
                      {chunk.source}
                    </span>
                    <Verdict grade={grades[index]} />
                  </div>
                  <div className="mt-2.5 flex items-center gap-3">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-moss-700">
                      <div data-bar className="bar-fill h-full rounded-full" style={{ width: `${proximity(chunk.distance) * 100}%` }} />
                    </div>
                    <span className="font-mono text-[10px] tabular-nums text-bone-500">d={chunk.distance.toFixed(3)}</span>
                  </div>
                  <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-bone-300">{chunk.preview}</p>
                  {grades[index] && <p className="mt-1.5 font-mono text-[10px] leading-relaxed text-bone-500">{grades[index].reason}</p>}
                </li>
              ))}
            </ul>
          </>
        )}

        {webResults.length > 0 && (
          <div data-row>
            <p className="mb-3 font-mono text-[10px] uppercase tracking-[0.22em] text-ochre-400">Web fallback results</p>
            <ul className="space-y-2">
              {webResults.map((result) => (
                <li key={result.url} className="rounded-md border border-moss-700 bg-moss-850/70 p-3">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-2 text-sm text-bone-100 transition-colors hover:text-spark-200"
                  >
                    <ExternalLink className="size-3.5 shrink-0" />
                    <span className="truncate">{result.title}</span>
                  </a>
                  <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-bone-500">{result.snippet}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
