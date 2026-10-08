import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-sm border px-2 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.14em]",
  {
    variants: {
      variant: {
        default: "border-fern-400/50 bg-fern-400/10 text-fern-300",
        success: "border-spark-200/50 bg-spark-200/10 text-spark-200",
        warn: "border-ochre-400/50 bg-ochre-400/10 text-ochre-400",
        danger: "border-rust-400/50 bg-rust-400/10 text-rust-400",
        muted: "border-moss-600 bg-moss-800 text-bone-500",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

const Badge = React.forwardRef(({ className, variant, ...props }, ref) => (
  <span ref={ref} className={cn(badgeVariants({ variant }), className)} {...props} />
));
Badge.displayName = "Badge";

export { Badge, badgeVariants };
