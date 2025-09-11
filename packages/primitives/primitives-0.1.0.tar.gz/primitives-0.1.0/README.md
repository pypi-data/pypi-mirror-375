timers-latches

Lightweight, production-ready implementations of PLC-style primitives in Python:

TON — On-delay timer

SR — Set/Reset latch (reset dominant)

These primitives are useful for industrial automation logic, simulations, or anywhere you want PLC-like control behavior in Python.

Installation
pip install timers-latches


Or, for development:

git clone https://github.com/yourorg/timers-latches.git
cd timers-latches
pip install -e .

Usage
from timers_latches import TON, SR

# --- TON example ---
ton = TON(preset_s=2.0)   # 2-second delay
for step in range(5):
    q = ton.update(enable=True, dt_s=0.5)
    print(f"t={step*0.5:.1f}s, Q={q}")
# Q will turn True after 2.0 seconds of accumulated enable time

# --- SR example ---
latch = SR(initial=False)
print(latch.update(set_=True, reset=False))   # True
print(latch.update(set_=False, reset=True))   # False (reset dominates)

API
TON(preset_s: float)

preset_s: delay time in seconds (must be ≥ 0).

.update(enable: bool, dt_s: float) -> bool: call once per scan; returns the done bit (Q).

.Q: current output (done bit).

SR(initial: bool = False)

initial: starting state.

.update(set_: bool, reset: bool) -> bool: updates and returns current state. Reset dominates set.

.state: current latched state.

Versioning

Follows Semantic Versioning
.

API is stable from 1.0.0 onward.

License

MIT © Your Name / Your Organization

⚡️ This package is intentionally minimal and focused: no dependencies, only core primitives. You can drop it into simulations, control logic, or larger automation frameworks.