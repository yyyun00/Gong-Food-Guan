"use client";

import { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Question = {
  stage: string;
  topic: string;
  text: string;
  options: string[];
};

type Restaurant = {
  id: number;
  name: string;
  category: string;
  price_tier: number;
  address: string;
};

type Phase = "loading" | "quiz" | "q4" | "budget" | "result" | "error";

const STAGE_EMOJI: Record<string, string> = {
  quote: "💬",
  environment: "🌍",
  color: "🎨",
};
const STAGE_LABEL: Record<string, string> = {
  quote: "名言",
  environment: "環境",
  color: "顏色",
};
const EMOTION_EMOJI: Record<string, string> = {
  開心: "☀️",
  生氣: "🔥",
  難過: "🌧️",
  煩躁: "⚡",
  平靜: "🌿",
  都可以: "🎲",
};
const PRICE_LABEL: Record<number, string> = { 1: "平價", 2: "中等", 3: "精緻" };

// Mobile steps: 0=Q1, 1=Q2, 2=Q3, 3=budget
const MOBILE_STEPS = ["名言", "環境", "顏色", "預算"];

export default function Home() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [sessionId, setSessionId] = useState("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selections, setSelections] = useState<(number | null)[]>([
    null,
    null,
    null,
  ]);
  const [flash, setFlash] = useState<string | null>(null);
  const [q4Options, setQ4Options] = useState<string[]>([]);
  const [finalEmotion, setFinalEmotion] = useState<string | null>(null);
  const [budget, setBudget] = useState<string | null>(null);
  const [restaurantName, setRestaurantName] = useState<string | null>(null);
  const [restaurantDetail, setRestaurantDetail] = useState<Restaurant | null>(
    null,
  );
  const [submitting, setSubmitting] = useState(false);
  const [mobileStep, setMobileStep] = useState(0); // 0-3

  useEffect(() => {
    fetchQuestions();
  }, []);

  async function fetchQuestions() {
    setPhase("loading");
    try {
      const res = await fetch(`${API_BASE}/quiz/questions`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      setSessionId(data.session_id);
      setQuestions(data.questions);
      setSelections([null, null, null]);
      setFinalEmotion(null);
      setBudget(null);
      setRestaurantName(null);
      setRestaurantDetail(null);
      setMobileStep(0);
      setPhase("quiz");
    } catch {
      setPhase("error");
    }
  }

  function handleSelect(qIndex: number, optIndex: number) {
    const key = `${qIndex}-${optIndex}`;
    setFlash(key);
    setTimeout(() => {
      setFlash(null);
      const next = [...selections];
      next[qIndex] = optIndex;
      setSelections(next);
    }, 200);
  }

  function canAdvanceMobileStep() {
    if (mobileStep < 3) return selections[mobileStep] !== null;
    return budget !== null;
  }

  async function handleStartRecommend() {
    if (selections.some((s) => s === null) || !budget) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/quiz/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          idx1: selections[0],
          idx2: selections[1],
          idx3: selections[2],
        }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      if (data.trigger_q4) {
        setQ4Options(data.q4_options);
        setPhase("q4");
      } else {
        setFinalEmotion(data.determined_emotion);
        await submitRecommend(data.determined_emotion, budget!);
      }
    } catch {
      setPhase("error");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleQ4Select(emotion: string) {
    setFinalEmotion(emotion);
    await submitRecommend(emotion, budget!);
  }

  async function submitRecommend(emotion: string, b: string) {
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/quiz/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          final_emotion: emotion,
          budget: b,
        }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setRestaurantName(data.restaurant_name);
      setRestaurantDetail(data.detail ?? null);
      setPhase("result");
    } catch {
      setPhase("error");
    } finally {
      setSubmitting(false);
    }
  }

  const allSelected = selections.every((s) => s !== null);

  // Decide what's shown on the current mobile step
  const isBudgetStep = mobileStep === 3;
  const currentQuestion = !isBudgetStep && questions[mobileStep];
  const isLastMobileStep = mobileStep === MOBILE_STEPS.length - 1;

  return (
    <div className="min-h-screen bg-[#f5f5f5] flex flex-col items-center py-10 px-4">
      <h1 className="text-4xl font-bold mb-2 tracking-tight text-gray-900">
        🍜 Gong Food Guan
      </h1>
      <p
        className="text-xl mb-10 tracking-tight text-gray-500 italic"
        style={{ fontFamily: "var(--font-lora), Georgia, serif" }}
      >
        A exploring food journey. A satisfying food map.
      </p>

      {/* ── LOADING ── */}
      {phase === "loading" && (
        <p className="text-gray-400 text-sm mt-20">載入問卷中…</p>
      )}

      {/* ── ERROR ── */}
      {phase === "error" && (
        <div className="text-center mt-20">
          <p className="text-red-400 mb-4">
            無法連線到後端 API（{API_BASE}），請確認 FastAPI 已啟動。
          </p>
          <button
            onClick={fetchQuestions}
            className="text-sm text-gray-500 underline"
          >
            重試
          </button>
        </div>
      )}

      {/* ── QUIZ ── */}
      {phase === "quiz" && questions.length === 3 && (
        <>
          {/* ════════════════════════════════
              DESKTOP: 三欄 + 預算 + 按鈕
          ════════════════════════════════ */}
          <div className="hidden md:flex md:flex-col md:items-center w-full">
            <div className="w-full max-w-5xl grid grid-cols-3 gap-4 mb-6">
              {questions.map((q, qi) => (
                <div
                  key={qi}
                  className="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3"
                >
                  <h2 className="text-lg font-semibold text-gray-800">
                    {STAGE_EMOJI[q.stage]} {STAGE_LABEL[q.stage]}
                  </h2>
                  <div className="flex flex-col gap-2">
                    {q.options.map((optText, oi) => {
                      const key = `${qi}-${oi}`;
                      const isSelected = selections[qi] === oi;
                      const isFlashing = flash === key;
                      return (
                        <button
                          key={oi}
                          onClick={() => handleSelect(qi, oi)}
                          className={[
                            "w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-150 border",
                            isSelected
                              ? "bg-gray-900 text-white border-gray-900"
                              : isFlashing
                                ? "bg-gray-200 border-gray-300 text-gray-800"
                                : "bg-gray-100 border-gray-100 text-gray-700 hover:bg-gray-200",
                          ].join(" ")}
                        >
                          {optText}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* 預算 */}
            <div className="w-full max-w-5xl bg-white rounded-2xl shadow-sm p-5 mb-8">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">
                💰 預算
              </h2>
              <div className="flex gap-3">
                {(["低", "中", "高"] as const).map((b) => (
                  <button
                    key={b}
                    onClick={() => setBudget(b)}
                    className={[
                      "px-6 py-2 rounded-full text-sm font-medium border transition-all duration-150",
                      budget === b
                        ? "bg-gray-900 text-white border-gray-900"
                        : "bg-gray-100 text-gray-600 border-gray-100 hover:bg-gray-200",
                    ].join(" ")}
                  >
                    {b}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleStartRecommend}
              disabled={!allSelected || !budget || submitting}
              className={[
                "px-10 py-4 rounded-full text-base font-semibold transition-all duration-200",
                allSelected && budget && !submitting
                  ? "bg-gray-900 text-white hover:bg-gray-700 shadow-lg"
                  : "bg-gray-300 text-gray-400 cursor-not-allowed",
              ].join(" ")}
            >
              {submitting ? "分析中…" : "開始推薦 🎯"}
            </button>
          </div>

          {/* ════════════════════════════════
              MOBILE: 分步驟卡片
          ════════════════════════════════ */}
          <div className="flex md:hidden flex-col items-center w-full max-w-sm">
            {/* 步驟指示器 */}
            <div className="flex items-center gap-1 mb-6 w-full justify-center">
              {MOBILE_STEPS.map((label, i) => (
                <div key={i} className="flex items-center gap-1">
                  <button
                    onClick={() => {
                      // allow going back to already-answered steps
                      if (
                        i < mobileStep ||
                        (i > 0 && selections[i - 1] !== null)
                      ) {
                        setMobileStep(i);
                      }
                    }}
                    className="flex flex-col items-center gap-0.5"
                  >
                    <div
                      className={[
                        "w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200",
                        i === mobileStep
                          ? "bg-gray-900 text-white scale-110"
                          : i < mobileStep
                            ? "bg-gray-400 text-white"
                            : "bg-gray-200 text-gray-400",
                      ].join(" ")}
                    >
                      {i < mobileStep ? "✓" : i + 1}
                    </div>
                    <span
                      className={[
                        "text-[10px]",
                        i === mobileStep
                          ? "text-gray-900 font-semibold"
                          : "text-gray-400",
                      ].join(" ")}
                    >
                      {label}
                    </span>
                  </button>
                  {i < MOBILE_STEPS.length - 1 && (
                    <div
                      className={[
                        "w-6 h-px mb-3 transition-all duration-300",
                        i < mobileStep ? "bg-gray-400" : "bg-gray-200",
                      ].join(" ")}
                    />
                  )}
                </div>
              ))}
            </div>

            {/* 卡片內容 */}
            <div className="w-full bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3 min-h-[320px]">
              {!isBudgetStep && currentQuestion && (
                <>
                  <h2 className="text-lg font-semibold text-gray-800">
                    {STAGE_EMOJI[currentQuestion.stage]}{" "}
                    {STAGE_LABEL[currentQuestion.stage]}
                  </h2>
                  <p className="text-xs text-gray-400">
                    {currentQuestion.text}
                  </p>
                  <div className="flex flex-col gap-2">
                    {currentQuestion.options.map((optText, oi) => {
                      const key = `${mobileStep}-${oi}`;
                      const isSelected = selections[mobileStep] === oi;
                      const isFlashing = flash === key;
                      return (
                        <button
                          key={oi}
                          onClick={() => handleSelect(mobileStep, oi)}
                          className={[
                            "w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-150 border",
                            isSelected
                              ? "bg-gray-900 text-white border-gray-900"
                              : isFlashing
                                ? "bg-gray-200 border-gray-300 text-gray-800"
                                : "bg-gray-100 border-gray-100 text-gray-700 hover:bg-gray-200",
                          ].join(" ")}
                        >
                          {optText}
                        </button>
                      );
                    })}
                  </div>
                </>
              )}

              {isBudgetStep && (
                <>
                  <h2 className="text-lg font-semibold text-gray-800">
                    💰 預算
                  </h2>
                  <p className="text-xs text-gray-400 mb-2">今天想花多少？</p>
                  <div className="flex flex-col gap-3">
                    {(
                      [
                        { key: "低", label: "平價", sub: "200 元以內" },
                        { key: "中", label: "一般", sub: "200–400 元" },
                        { key: "高", label: "精緻", sub: "400 元以上" },
                      ] as const
                    ).map(({ key, label, sub }) => (
                      <button
                        key={key}
                        onClick={() => setBudget(key)}
                        className={[
                          "w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-150 border flex items-center justify-between",
                          budget === key
                            ? "bg-gray-900 text-white border-gray-900"
                            : "bg-gray-100 border-gray-100 text-gray-700 hover:bg-gray-200",
                        ].join(" ")}
                      >
                        <span className="font-medium">{label}</span>
                        <span
                          className={
                            budget === key
                              ? "text-gray-300 text-xs"
                              : "text-gray-400 text-xs"
                          }
                        >
                          {sub}
                        </span>
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            {/* 下一步 / 送出按鈕 */}
            <div className="flex w-full gap-3 mt-4">
              {mobileStep > 0 && (
                <button
                  onClick={() => setMobileStep((s) => s - 1)}
                  className="flex-1 py-3 rounded-full border border-gray-300 text-sm text-gray-500 hover:bg-gray-100 transition-all"
                >
                  ← 上一步
                </button>
              )}
              {!isLastMobileStep ? (
                <button
                  onClick={() =>
                    canAdvanceMobileStep() && setMobileStep((s) => s + 1)
                  }
                  disabled={!canAdvanceMobileStep()}
                  className={[
                    "flex-1 py-3 rounded-full text-sm font-semibold transition-all duration-200",
                    canAdvanceMobileStep()
                      ? "bg-gray-900 text-white hover:bg-gray-700"
                      : "bg-gray-200 text-gray-400 cursor-not-allowed",
                  ].join(" ")}
                >
                  下一步 →
                </button>
              ) : (
                <button
                  onClick={handleStartRecommend}
                  disabled={!allSelected || !budget || submitting}
                  className={[
                    "flex-1 py-3 rounded-full text-sm font-semibold transition-all duration-200",
                    allSelected && budget && !submitting
                      ? "bg-gray-900 text-white hover:bg-gray-700 shadow-lg"
                      : "bg-gray-200 text-gray-400 cursor-not-allowed",
                  ].join(" ")}
                >
                  {submitting ? "分析中…" : "開始推薦 🎯"}
                </button>
              )}
            </div>
          </div>
        </>
      )}

      {/* ── Q4 第四題 ── */}
      {phase === "q4" && (
        <div className="w-full max-w-md bg-white rounded-2xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-2">
            🤔 再問你一題
          </h2>
          <p className="text-sm text-gray-400 mb-5">你今天最想要的感覺是？</p>
          <div className="flex flex-col gap-2">
            {q4Options.map((opt) => (
              <button
                key={opt}
                onClick={() => !submitting && handleQ4Select(opt)}
                disabled={submitting}
                className="w-full text-left px-4 py-3 rounded-xl text-sm bg-gray-100 border border-gray-100 text-gray-700 hover:bg-gray-900 hover:text-white transition-all duration-150"
              >
                {EMOTION_EMOJI[opt]} {opt}
              </button>
            ))}
          </div>
          {submitting && (
            <p className="text-xs text-gray-400 text-center mt-4">
              正在幫你配對…
            </p>
          )}
        </div>
      )}

      {/* ── RESULT ── */}
      {phase === "result" && (
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-sm p-6 mb-4 text-center">
            <div className="text-5xl mb-3">
              {finalEmotion ? (EMOTION_EMOJI[finalEmotion] ?? "🍽️") : "🍽️"}
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              {finalEmotion && `心情：${finalEmotion}`}
            </h2>
            <p className="text-gray-400 text-sm">
              預算：
              {budget === "低" ? "平價" : budget === "中" ? "一般" : "精緻"}
            </p>
          </div>

          {restaurantName ? (
            <div className="bg-white rounded-2xl shadow-sm px-5 py-4 mb-6">
              <div className="text-xs text-gray-400 mb-1">
                今天就去這裡吧 👇
              </div>
              <div className="font-semibold text-gray-900 text-lg">
                {restaurantName}
              </div>
              {restaurantDetail && (
                <div className="text-xs text-gray-400 mt-1 flex items-center gap-2">
                  <span>{restaurantDetail.category}</span>
                  <span>·</span>
                  <span>{restaurantDetail.address}</span>
                  <span className="ml-auto bg-gray-100 px-2 py-0.5 rounded-full">
                    {PRICE_LABEL[restaurantDetail.price_tier]}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm p-5 text-center text-gray-400 text-sm mb-6">
              目前此情緒／預算的餐廳池為空，請在 quiz.py 的 RESTAURANT_POOL
              補充資料。
            </div>
          )}

          <div className="text-center">
            <button
              onClick={fetchQuestions}
              className="px-8 py-3 rounded-full border border-gray-300 text-sm text-gray-500 hover:bg-gray-100 transition-all"
            >
              重新測驗
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
