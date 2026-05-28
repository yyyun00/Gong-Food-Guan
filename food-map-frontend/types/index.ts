export type EmotionType = "happy" | "sad" | "angry" | "calm" | "anxious";

export interface OptionItem {
  name: string;
  emotion: EmotionType;
  emoji?: string;
}

export interface Restaurant {
  id: number;
  name: string;
  category: string;
  budget: string;
  emotion: EmotionType;
  description: string;
}

export interface RecommendationResponse {
  emotion: EmotionType;
  foods: string[];
  restaurants: Restaurant[];
}
