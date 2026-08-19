// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title EvidenceAnchor
 * @dev Anchors canonical SHA-256 digital evidence digests on-chain for tamper-evident verification.
 * 
 * TCF-FX Principle:
 * Keeps full evidence off-chain to protect confidentiality and privacy.
 * Only immutable 32-byte cryptographic hashes and provenance timestamps are recorded on-chain.
 */
contract EvidenceAnchor {
    
    struct AnchorRecord {
        bytes32 evidenceId;
        bytes32 digest;
        address submitter;
        uint256 timestamp;
        uint256 blockNumber;
        bool exists;
    }

    // Mapping from evidenceId (bytes32) to AnchorRecord
    mapping(bytes32 => AnchorRecord) private anchors;

    // Total registered anchors counter
    uint256 public totalAnchors;

    // Events
    event EvidenceAnchored(
        bytes32 indexed evidenceId,
        bytes32 indexed digest,
        address indexed submitter,
        uint256 timestamp,
        uint256 blockNumber
    );

    error EvidenceAlreadyAnchored(bytes32 evidenceId);
    error EvidenceNotFound(bytes32 evidenceId);
    error InvalidDigest();

    /**
     * @dev Anchors a new evidence digest. Fails if evidenceId has already been anchored.
     */
    function submitEvidence(bytes32 evidenceId, bytes32 digest) external returns (bool) {
        if (anchors[evidenceId].exists) {
            revert EvidenceAlreadyAnchored(evidenceId);
        }
        if (digest == bytes32(0)) {
            revert InvalidDigest();
        }

        anchors[evidenceId] = AnchorRecord({
            evidenceId: evidenceId,
            digest: digest,
            submitter: msg.sender,
            timestamp: block.timestamp,
            blockNumber: block.number,
            exists: true
        });

        totalAnchors += 1;

        emit EvidenceAnchored(
            evidenceId,
            digest,
            msg.sender,
            block.timestamp,
            block.number
        );

        return true;
    }

    /**
     * @dev Retrieves and verifies an anchored evidence record by evidenceId.
     */
    function verifyEvidence(bytes32 evidenceId)
        external
        view
        returns (
            bytes32 digest,
            address submitter,
            uint256 timestamp,
            uint256 blockNumber,
            bool isAnchored
        )
    {
        AnchorRecord memory record = anchors[evidenceId];
        if (!record.exists) {
            return (bytes32(0), address(0), 0, 0, false);
        }
        return (
            record.digest,
            record.submitter,
            record.timestamp,
            record.blockNumber,
            true
        );
    }
}
