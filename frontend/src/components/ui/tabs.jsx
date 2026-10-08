import * as React from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

const Tabs = TabsPrimitive.Root;

const TabsList = React.forwardRef(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn("flex items-center gap-1 border-b border-moss-700 px-3", className)}
    {...props}
  />
));
TabsList.displayName = "TabsList";

const TabsTrigger = React.forwardRef(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      "relative px-3 py-3 font-mono text-[11px] uppercase tracking-[0.16em] text-bone-500 outline-none transition-colors hover:text-bone-100 data-[state=active]:text-spark-200",
      "after:absolute after:inset-x-3 after:-bottom-px after:h-px after:origin-left after:scale-x-0 after:bg-spark-200 after:transition-transform after:duration-300 data-[state=active]:after:scale-x-100",
      className
    )}
    {...props}
  />
));
TabsTrigger.displayName = "TabsTrigger";

const TabsContent = React.forwardRef(({ className, ...props }, ref) => (
  <TabsPrimitive.Content ref={ref} className={cn("outline-none", className)} {...props} />
));
TabsContent.displayName = "TabsContent";

export { Tabs, TabsList, TabsTrigger, TabsContent };
