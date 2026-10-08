import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-mono text-xs font-medium uppercase tracking-[0.14em] outline-none transition-all duration-200 focus-visible:ring-2 focus-visible:ring-spark-200/60 disabled:pointer-events-none disabled:opacity-40 [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "glow-fern bg-fern-400 text-moss-950 hover:-translate-y-px hover:bg-fern-300",
        outline: "border border-moss-600 bg-transparent text-bone-100 hover:border-fern-400 hover:bg-moss-800",
        ghost: "text-bone-300 hover:bg-moss-800 hover:text-bone-100",
      },
      size: {
        default: "h-10 px-5",
        sm: "h-8 px-3",
        icon: "size-9",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button";
  return <Comp ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />;
});
Button.displayName = "Button";

export { Button, buttonVariants };
