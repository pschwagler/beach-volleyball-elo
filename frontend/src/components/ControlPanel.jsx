import { useState } from 'react';
import { RefreshCw, ExternalLink, Loader2 } from 'lucide-react';
import { Button } from './UI';

const GOOGLE_SHEETS_URL = 'https://docs.google.com/spreadsheets/d/1KZhd5prjzDjDTJCvg0b1fxVAM-uGDBxsHJJwKBKrBIA/edit?usp=sharing';

export default function ControlPanel({ onRecalculate }) {
  const [isCalculating, setIsCalculating] = useState(false);

  const handleRecalculate = async () => {
    setIsCalculating(true);
    await onRecalculate();
    setIsCalculating(false);
  };

  return (
    <div className="controls">
      <Button
        onClick={handleRecalculate}
        disabled={isCalculating}
      >
        {isCalculating ? (
          <>
            <Loader2 size={18} className="spin" />
            Calculating...
          </>
        ) : (
          <>
            <RefreshCw size={18} />
            Recalculate Stats
          </>
        )}
      </Button>
      
      <a href={GOOGLE_SHEETS_URL} target="_blank" rel="noopener noreferrer" className="no-underline">
        <Button variant="success">
          <ExternalLink size={18} />
          View Input Data
        </Button>
      </a>
    </div>
  );
}

