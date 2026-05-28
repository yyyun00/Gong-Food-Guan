"use client";

import { OptionItem } from "@/types";

interface Props {
  title: string;
  options: OptionItem[];
  selected: OptionItem | null;
  onSelect: (item: OptionItem) => void;
}

export default function EmotionSelector({
  title,
  options,
  selected,
  onSelect,
}: Props) {
  return (
    <div className="bg-white rounded-3xl shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>

      <div className="space-y-3">
        {options.map((item) => (
          <button
            key={item.name}
            onClick={() => onSelect(item)}
            className={`w-full rounded-2xl  p-3 transition text-left ${
              selected?.name === item.name
                ? "bg-black text-white"
                : "bg-neutral-100 hover:bg-neutral-100"
            }`}
          >
            {item.emoji} {item.name}
          </button>
        ))}
      </div>
    </div>
  );
}
