interface StatCardProps {
  number: string;
  label: string;
  source: string;
  sourceUrl?: string;
}

export default function StatCard({ number, label, source, sourceUrl }: StatCardProps) {
  return (
    <div className="card card-hover p-5 animate-fade-in">
      <div className="serif text-4xl font-bold text-brand-700 mb-1">{number}</div>
      <div className="text-sm text-gray-800 leading-tight mb-2">{label}</div>
      {sourceUrl ? (
        <a href={sourceUrl} target="_blank" rel="noreferrer"
           className="text-xs text-gray-500 hover:text-brand-700 underline-offset-2 hover:underline">
          {source}
        </a>
      ) : (
        <span className="text-xs text-gray-500">{source}</span>
      )}
    </div>
  );
}
