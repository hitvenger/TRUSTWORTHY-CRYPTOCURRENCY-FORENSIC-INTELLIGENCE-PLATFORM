# Digital Chain of Custody Protocol

## 1. Chained Hash Architecture
Every action taken within the platform generates an immutable custody event structured as a cryptographic blockchain:
$$\text{Event Hash}_i = \text{SHA-256}\Big(\text{Canonical}\big(\text{PrevHash}_{i-1}, \text{Actor}, \text{Role}, \text{Action}, \text{Timestamp}, \text{Payload}\big)\Big)$$

---

## 2. Genesis and Linkage Rules
- **Genesis Event**: The case initialization event links to `previous_hash = "0" * 64`.
- **Consecutive Integrity**: For every event $i > 0$, $\text{Event}_i.\text{previous\_hash} == \text{Event}_{i-1}.\text{event\_hash}$.
- **Tamper Localization**: If any event record is modified in the database, the hash verification algorithm immediately identifies the exact broken link in the chain.
