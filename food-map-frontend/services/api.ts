import { RecommendationResponse } from "@/types";

export const getRecommendations = async (): Promise<RecommendationResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    emotion: "calm",
    foods: ["咖啡廳", "日式料理", "輕食"],
    restaurants: [
      {
        id: 1,
        name: "森呼吸咖啡館",
        category: "咖啡廳",
        budget: "中",
        emotion: "calm",
        description: "安靜放鬆的空間",
      },
      {
        id: 2,
        name: "山木日式食堂",
        category: "日式料理",
        budget: "中",
        emotion: "calm",
        description: "適合一個人慢慢吃飯",
      },
    ],
  };
};
