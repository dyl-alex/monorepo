"use client";

import { QueryErrorResetBoundary } from "@tanstack/react-query";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Suspense } from "react";
import { ErrorBoundary } from "react-error-boundary";

import { Button } from "@/components/ui/button";

export function QueryPanel({
  children,
  fallback,
  errorMessage,
}: {
  children: React.ReactNode;
  fallback: React.ReactNode;
  errorMessage: string;
}) {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ resetErrorBoundary }) => (
            <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-xl border border-destructive/20 bg-destructive/5 p-6 text-center">
              <AlertCircle
                className="size-6 text-destructive"
                aria-hidden="true"
              />
              <p className="font-medium">{errorMessage}</p>
              <Button variant="outline" size="sm" onClick={resetErrorBoundary}>
                <RotateCcw className="size-4" />
                Try again
              </Button>
            </div>
          )}
        >
          <Suspense fallback={fallback}>{children}</Suspense>
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}
