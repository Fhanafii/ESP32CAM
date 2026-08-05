export function getStatusBadgeClass(status: string): string {
  switch (status) {
    case "Normal":
      return "bg-green-600 hover:bg-green-700 text-white";

    case "Perlu Dipantau":
      return "bg-yellow-500 hover:bg-yellow-600 text-black";

    case "Mencurigakan":
      return "bg-red-600 hover:bg-red-700 text-white";

    default:
      return "bg-slate-600 text-white";
  }
}