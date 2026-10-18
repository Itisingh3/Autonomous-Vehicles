# Malicious-node lifecycle

Events are retained in a sliding window and assigned severity weights. Temporary low/medium faults receive forgiveness based on recent accuracy; critical evidence never receives forgiveness. Nodes move through trusted, suspicious, quarantined, and revoked states. Quarantined nodes are excluded from active consensus but monitored. Revoked pseudonyms and credentials are permanently excluded.

Permanent revocation requires confirmed critical evidence or a minimum reputation plus `2f+1` independent confirmations. The signed evidence record is committed to the blockchain. Honest nodes can recover when temporary faults expire from the window and subsequent contributions are valid.
