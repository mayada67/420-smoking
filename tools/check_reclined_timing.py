from pathlib import Path
source=Path('tools/check_smoking_timing.py').read_text(encoding='utf-8')
source=source.replace('420_smoking_male.skeleton','420_reclined_male.skeleton').replace('420_smoke_','420_recline_').replace('smoking_timing_roundtrip.json','reclined_timing_roundtrip.json')
exec(compile(source,'check_reclined_timing','exec'))
