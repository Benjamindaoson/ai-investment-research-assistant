import { http, HttpResponse } from "msw";
import { mockTodayData } from "./fixtures/today";

// Optional browser/test transport. Production can replace this endpoint with FastAPI.
export const mockResearchHandlers = [
  http.get("/api/research/today", () => HttpResponse.json(mockTodayData)),
];
