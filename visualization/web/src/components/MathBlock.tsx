import katex from "katex";

interface Props {
  expression: string | null | undefined;
  fallback?: string;
  display?: boolean;
}

export default function MathBlock({ expression, fallback, display = true }: Props) {
  if (!expression) {
    return fallback ? (
      <code className="block whitespace-pre-wrap rounded bg-slate-100 p-2 text-xs text-slate-600">
        {fallback}
      </code>
    ) : null;
  }

  let html: string;
  try {
    html = katex.renderToString(expression, {
      displayMode: display,
      throwOnError: false,
      output: "html",
      trust: false,
      strict: "warn",
    });
  } catch {
    return (
      <code className="block whitespace-pre-wrap rounded bg-slate-100 p-2 text-xs text-slate-600">
        {expression}
      </code>
    );
  }

  return (
    <div
      className="overflow-x-auto py-1"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
