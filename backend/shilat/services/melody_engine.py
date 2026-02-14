from dataclasses import dataclass

@dataclass
class MelodySuggestion:
    rhythm_key: str
    reason: str

METER_TO_RHYTHM = {
    "tawil": ["samri", "khammari", "atifi"],
    "kamil": ["ardah_main", "samri", "modih"],
    "basit": ["samri", "khammari"],
    "mutaqarib": ["dahha", "hamasi"],
    "rajaz": ["dahha", "hamasi"],
}

def suggest_rhythms(meter_guess: str):
    keys = METER_TO_RHYTHM.get(meter_guess, ["samri"])
    return [MelodySuggestion(k, f"اقتراح تلقائي بناءً على البحر: {meter_guess}") for k in keys]
