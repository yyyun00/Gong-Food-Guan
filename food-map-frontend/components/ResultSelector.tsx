"use client";

import { RecommendationResponse } from "@/types";
import RestaurantCard from "./RestaurantCard";

interface Props {
  result: RecommendationResponse;
}

const emotionLabels = {
  happy: "快樂 😄",
  sad: "悲傷 😢",
  angry: "憤怒 😡",
  calm: "平靜 😌",
  anxious: "焦躁 😵‍💫",
};

export default function ResultSection({ result }: Props) {
  return (
    <div className="bg-white rounded-3xl shadow-xl p-8">
      <h2 className="text-3xl font-bold mb-5">
        偵測情緒：{emotionLabels[result.emotion]}
      </h2>

      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-3">推薦食物</h3>

        <div className="flex flex-wrap gap-3">
          {result.foods.map((food) => (
            <div key={food} className="bg-neutral-200 px-4 py-2 rounded-full">
              {food}
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-4">推薦餐廳</h3>

        <div className="grid md:grid-cols-2 gap-4">
          {result.restaurants.map((restaurant) => (
            <RestaurantCard key={restaurant.id} restaurant={restaurant} />
          ))}
        </div>
      </div>
    </div>
  );
}
