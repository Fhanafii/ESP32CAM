import { Button } from "@/components/ui/button";

interface Props {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function HistoryPagination({
  page,
  totalPages,
  onPageChange,
}: Props) {

  return (

    <div className="flex justify-end gap-2">

      <Button
        variant="outline"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        Sebelumnya
      </Button>

      <Button variant="secondary">
        {page} / {totalPages}
      </Button>

      <Button
        variant="outline"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        Selanjutnya
      </Button>

    </div>
  );
}