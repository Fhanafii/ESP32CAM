import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

export function Header() {
  return (
    <header className="border-b bg-background">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <div>
          <h1 className="text-xl font-bold">
            Monitoring Deteksi
          </h1>

          <p className="text-sm text-muted-foreground">
            Sistem Keamanan Otomatis Berbasis IoT
          </p>
        </div>

        <div className="relative w-80">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />

          <Input
            placeholder="Cari batch..."
            className="pl-9"
          />
        </div>
      </div>
    </header>
  );
}