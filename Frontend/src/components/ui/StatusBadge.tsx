interface StatusBadgeProps {
  value: string;
}

export const StatusBadge = ({ value }: StatusBadgeProps) => {
  const styles: Record<string, string> = {
    // Estados de alertas
    NEW: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    ACKNOWLEDGED: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    RESOLVED: 'bg-green-500/20 text-green-400 border-green-500/50',
    // Severidades
    CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/50',
    HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    LOW: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    INFO: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
    // Estados de línea base / escaneo
    ACTIVE: 'bg-green-500/20 text-green-400 border-green-500/50',
    PROPOSED: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    REJECTED: 'bg-red-500/20 text-red-400 border-red-500/50',
    SUPERSEDED: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
    COMPLETED: 'bg-green-500/20 text-green-400 border-green-500/50',
    FAILED: 'bg-red-500/20 text-red-400 border-red-500/50',
    RUNNING: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    // Outcomes
    SUCCESS: 'bg-green-500/20 text-green-400 border-green-500/50',
    FAILURE: 'bg-red-500/20 text-red-400 border-red-500/50',
    DENIED: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
  };

  return (
    <span className={`px-2 py-1 rounded border text-xs font-semibold ${styles[value] || 'bg-gray-500/20 text-gray-400'}`}>
      {value}
    </span>
  );
};