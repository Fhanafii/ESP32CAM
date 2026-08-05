"use client";

import { useState } from "react";

import { Header } from "@/components/layout/header";
import { SummaryGrid } from "./summary-grid";
import { SearchBar } from "./search-bar";
import { DateFilter } from "./date-filter";
import { HistoryList } from "./history-list";
import { HistoryPagination } from "./history-pagination";

import { useDashboard } from "@/hooks/useDashboard";
import { useDetections } from "@/hooks/useDetections";

export function DashboardPage() {
    const [page, setPage] = useState(1);
    const [keyword, setKeyword] = useState("");
    const [start, setStart] = useState("");
    const [end, setEnd] = useState("");
    const dashboardQuery = useDashboard();
    const detectionsQuery = useDetections({
        page,
        keyword,
        start,
        end,
    });
    
    return (
        <>
            <Header
                keyword={keyword}
                onKeywordChange={setKeyword}
            />
            
            <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">
                
                {dashboardQuery.data && (
                    <SummaryGrid
                        dashboard={dashboardQuery.data.data}
                    />
                )}

                <DateFilter
                    start={start}
                    end={end}
                    onStartChange={setStart}
                    onEndChange={setEnd}
                />

                <HistoryList
                    detections={detectionsQuery.data?.data ?? []}
                    loading={detectionsQuery.isLoading}
                />

                <HistoryPagination
                    page={page}
                    totalPages={detectionsQuery.data?.total_pages ?? 1}
                    onPageChange={setPage}
                />
            </main>
        </>
    );

}