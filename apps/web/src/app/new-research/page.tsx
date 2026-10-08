import { RuntimeStartWorkspace } from "@/components/runtime/runtime-start-workspace";

type NewResearchPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

function firstParam(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function NewResearchPage({ searchParams }: NewResearchPageProps) {
  const params = await searchParams;

  return (
    <RuntimeStartWorkspace
      initialQuestion={firstParam(params.question)}
      initialTarget={firstParam(params.target)}
    />
  );
}
