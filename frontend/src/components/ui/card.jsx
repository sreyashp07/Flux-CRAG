import * as React from "react";
import { cn } from "@/lib/utils";

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("corner-ticks rounded-lg border border-moss-700 bg-moss-900/80 backdrop-blur-sm", className)}
    {...props}
  />
));
Card.displayName = "Card";

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-wrap items-center justify-between gap-3 border-b border-moss-700/80 px-5 py-3.5", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardLabel = React.forwardRef(({ className, ...props }, ref) => (
  <span
    ref={ref}
    className={cn("font-mono text-[10px] uppercase tracking-[0.22em] text-fern-300", className)}
    {...props}
  />
));
CardLabel.displayName = "CardLabel";

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3 ref={ref} className={cn("font-display text-lg font-medium tracking-tight text-bone-100", className)} {...props} />
));
CardTitle.displayName = "CardTitle";

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-5", className)} {...props} />
));
CardContent.displayName = "CardContent";

export { Card, CardHeader, CardLabel, CardTitle, CardContent };
