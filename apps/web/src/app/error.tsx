"use client";
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) { return <main className="route-state"><div className="error-state" role="alert"><b>The research workspace encountered an error</b><span>{error.message}</span><button type="button" onClick={reset}>Try again</button></div></main>; }
