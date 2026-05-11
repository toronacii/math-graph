import katex from "katex";

interface Props {
  expression: string | null;
  fallback: string;
}

export default function MathBlock({ expression, fallback }: Props) {
  if (!expression) {
    return <code className="details-block-code">{fallback}</code>;
  }

  let html: string;

  try {
    html = katex.renderToString(expression, {
      displayMode: true,
      throwOnError: false,
      output: "html",
      trust: false,
      strict: "warn",
    });
  } catch {
    return <code className="details-block-code">{expression}</code>;
  }

  return (
    <div
      className="details-math-block"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
