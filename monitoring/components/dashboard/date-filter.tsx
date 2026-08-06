"use client";

import * as React from "react";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { id } from "date-fns/locale";
import { DateRange } from "react-day-picker";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";

import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";

interface Props {
    start:string;
    end:string;
    onStartChange:(value:string)=>void;
    onEndChange:(value:string)=>void;
}

export function DateFilter({
    start,
    end,
    onStartChange,
    onEndChange,
}:Props){

    const [range,setRange]=React.useState<DateRange | undefined>({
        from:start ? new Date(start):undefined,
        to:end ? new Date(end):undefined,
    });

    React.useEffect(() => {
        if (range?.from) {
            onStartChange(
                format(range.from, "yyyy-MM-dd HH:mm:ss")
            );

        } else {
            onStartChange("");
        }

        if (range?.to) {
            const last = new Date(range.to);
            last.setHours(23, 59, 59, 999);
            onEndChange(
                format(last, "yyyy-MM-dd HH:mm:ss")
            );

        } else {
            onEndChange("");
        }

    }, [
        range,
        onStartChange,
        onEndChange,
    ]);

    return (
        <Popover>
            {/* Gunakan properti render di bawah ini */}
            <PopoverTrigger
                render={
                    <Button
                        variant="outline"
                        className={cn(
                            "w-[280px] justify-start text-left font-normal",
                            !range && "text-muted-foreground"
                        )}
                    >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {range?.from ? (
                            range.to ? (
                                `${format(range.from, "dd MMM yyyy", { locale: id })} - ${format(range.to, "dd MMM yyyy", { locale: id })}`
                            ) : (
                                format(range.from, "dd MMM yyyy", { locale: id })
                            )
                        ) : (
                            "Pilih Rentang Tanggal"
                        )}
                    </Button>
                }
            />

            <PopoverContent className="w-auto p-0" align="end">
                <Calendar
                    mode="range"
                    numberOfMonths={2}
                    selected={range}
                    onSelect={setRange}
                />
            </PopoverContent>
        </Popover>
    );
}