function ComparisonCard({ title, left, right }) {
  return (
    <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
      <div className="font-semibold">{title}</div>
      <div className="mt-3 grid grid-cols-2 gap-4">
        <div>{left}</div>
        <div>{right}</div>
      </div>
    </div>
  );
}

export default ComparisonCard;