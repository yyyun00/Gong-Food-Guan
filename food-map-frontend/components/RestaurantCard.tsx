"use client";

import { Restaurant } from "@/types";

interface Props {
  restaurant: Restaurant;
}

export default function RestaurantCard({ restaurant }: Props) {
  return (
    <div className="rounded-3xl border p-5 hover:shadow-xl transition bg-white">
      <div className="text-2xl font-bold mb-2">{restaurant.name}</div>

      <div className="text-neutral-600 mb-2">類型：{restaurant.category}</div>

      <div className="text-neutral-600 mb-3">預算：{restaurant.budget}</div>

      <div className="bg-neutral-100 rounded-2xl p-3 text-sm">
        {restaurant.description}
      </div>
    </div>
  );
}
