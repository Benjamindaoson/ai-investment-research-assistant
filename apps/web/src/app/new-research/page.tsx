import { NewResearchWorkspace } from "@/components/research/new-research-workspace";

export default async function NewResearchPage({ searchParams }: { searchParams: Promise<{ question?: string }> }) { const { question } = await searchParams; return <NewResearchWorkspace initialQuestion={question} />; }
