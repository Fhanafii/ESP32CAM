import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface SearchBarProps {
    value: string;
    onChange: (value: string) => void;
}

export function SearchBar({
    value,
    onChange,
}: SearchBarProps) {

    return (
        <div className="relative w-full md:max-w-sm">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />

            <Input
                value={value}
                onChange={(e)=>onChange(e.target.value)}
                placeholder="Cari batch..."
                className="pl-9"
            />
        </div>
    );

}