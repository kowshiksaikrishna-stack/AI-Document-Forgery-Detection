// blockchain/contracts/DocumentVerification.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DocumentVerification {

    struct Verification {
        string documentType;
        string documentHash;
        string result;
        uint256 timestamp;
        address verifier;
    }

    mapping(bytes32 => Verification) private records;

    event DocumentVerified(
        bytes32 indexed recordId,
        string documentType,
        string documentHash,
        string result,
        uint256 timestamp,
        address verifier
    );

    function storeVerification(
        string memory documentType,
        string memory documentHash,
        string memory result
    ) public returns (bytes32) {

        bytes32 recordId = keccak256(
            abi.encodePacked(
                documentType,
                documentHash,
                block.timestamp,
                msg.sender
            )
        );

        records[recordId] = Verification({
            documentType: documentType,
            documentHash: documentHash,
            result: result,
            timestamp: block.timestamp,
            verifier: msg.sender
        });

        emit DocumentVerified(
            recordId,
            documentType,
            documentHash,
            result,
            block.timestamp,
            msg.sender
        );

        return recordId;
    }

    function getVerification(
        bytes32 recordId
    )
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            uint256,
            address
        )
    {
        Verification memory record = records[recordId];

        return (
            record.documentType,
            record.documentHash,
            record.result,
            record.timestamp,
            record.verifier
        );
    }
}