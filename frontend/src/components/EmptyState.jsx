export default function EmptyState({ text }) {
  return (
    <div className="grid min-h-40 place-items-center rounded-md border border-dashed border-moss-600 px-6 py-10 text-center">
      <p className="max-w-xs font-mono text-[11px] uppercase leading-relaxed tracking-[0.18em] text-bone-500">{text}</p>
    </div>
  );
}
