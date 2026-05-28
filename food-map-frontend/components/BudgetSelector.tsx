"use client";

interface Props {
  budget: string;
  setBudget: (value: string) => void;
}

export default function BudgetSelector({ budget, setBudget }: Props) {
  return (
    <div className="bg-white rounded-3xl shadow-lg p-6 mb-8">
      <h2 className="text-2xl font-bold mb-4">💰 預算</h2>

      <div className="flex gap-4">
        {["低", "中", "高"].map((item) => (
          <button
            key={item}
            onClick={() => setBudget(item)}
            className={`px-6 py-3 rounded-2xl transition ${
              budget === item
                ? "bg-black text-white"
                : "bg-neutral-100 hover:bg-neutral-200"
            }`}
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
