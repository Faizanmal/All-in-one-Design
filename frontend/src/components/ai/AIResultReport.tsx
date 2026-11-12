/** Render structured assistant feedback without assuming a provider-specific schema. */
export function AIResultReport({ value }: { value: unknown }) {
  if (value === null || value === undefined) return null;
  if (Array.isArray(value)) {
    return <ul className="space-y-2 pl-4 list-disc">{value.map((item, index) => <li key={index}><AIResultReport value={item} /></li>)}</ul>;
  }
  if (typeof value === 'object') {
    return <dl className="space-y-3">{Object.entries(value).map(([key, item]) => (
      <div key={key}><dt className="font-medium capitalize">{key.replace(/_/g, ' ')}</dt><dd className="text-muted-foreground"><AIResultReport value={item} /></dd></div>
    ))}</dl>;
  }
  return <span className="whitespace-pre-wrap">{typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}</span>;
}
