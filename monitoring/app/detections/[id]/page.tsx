interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function DetectionDetailPage({
  params,
}: PageProps) {

  const { id } = await params;

  return (
    <main className="mx-auto max-w-7xl p-8">

      <h1 className="text-3xl font-bold">
        Detail Deteksi
      </h1>

      <p className="mt-2 text-muted-foreground">
        Batch ID : {id}
      </p>

    </main>
  );
}